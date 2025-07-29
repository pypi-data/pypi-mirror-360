import asyncio
import aiohttp
import aiofiles
import json
import codecs
from aiohttp import web
import aiohttp_cors
from traceback import print_exc
from appPublic.sshx import SSHNode
from appPublic.dictObject import DictObject
from appPublic.log import info, debug, warning, error, exception, critical
from .baseProcessor import BaseProcessor, PythonScriptProcessor

class XtermProcessor(PythonScriptProcessor):
	@classmethod
	def isMe(self,name):
		return name=='xterm'

	async def ws_2_process(self, ws):
		async for msg in ws:
			if msg.type == aiohttp.WSMsgType.TEXT:
				resize_pattern = '_#_resize_#_'
				heartbeat_pattern = '_#_heartbeat_#_'
				if msg.data.startswith(resize_pattern):
					row, col = [ int(i) for i in msg.data[len(resize_pattern):].split(',')]
					await self.p_obj.set_terminal_size(row, col)
					continue
				if msg.data == heartbeat_pattern:
					await ws_send(ws, heartbeat_pattern)
					continue
				self.p_obj.stdin.write(msg.data)
			elif msg.type == aiohttp.WSMsgType.ERROR:
				# print('ws connection closed with exception %s' % ws.exception())
				return
		
	async def process_2_ws(self, ws):
		while self.running:
			x = await self.p_obj.stdout.read(1024)
			await self.ws_sendstr(ws, x)

	async def datahandle(self,request):
		await self.path_call(request)
		
	async def path_call(self, request, params={}):
		#
		# xterm file is a python script as dspy file
		# it must return a DictObject with sshnode information
		# parameters: nodeid
		#
		await self.set_run_env(request, params=params)
		login_info = await super().path_call(request, params=params)
		if login_info is None:
			raise Exception('data error')

		debug(f'{login_info=}')
		ws = web.WebSocketResponse()
		await ws.prepare(request)
		await self.create_process(login_info)
		r1 = self.ws_2_process(ws)
		r2 = self.process_2_ws(ws)
		await asyncio.gather(r1,r2)
		self.retResponse = ws
		return ws

	async def create_process(self, login_info):
		# id = lenv['params_kw'].get('termid')
		host = login_info['host']
		port = login_info.get('port', 22)
		commandline = login_info.get('commandline', 'bash')
		username = login_info.get('username', 'root')
		password = login_info.get('password',None)
		client_key = login_info.get('client_key', None)
		passphrase = login_info.get('passphrase', None)
		jumpers = login_info.get('jumpers', [])
		self.sshnode = SSHNode(host, username=username,
									password=password,
									port=port,
									client_keys=[] if client_key is None else [client_key],
									passphrase=passphrase,
									jumpers=jumpers)
		await self.sshnode.connect()
		self.p_obj = await self.sshnode._process(commandline,
											term_type='xterm-256color',
											term_size=(80, 24),
											encoding='utf-8')
		self.running = True

	async def ws_sendstr(self, ws:web.WebSocketResponse, s:str):
		data = {
			"type":1,
			"data":s
		}
		await ws.send_str(json.dumps(data, indent=4, ensure_ascii=False))

	def close_process(self):
		self.sshnode.close()
		self.p_obj.close()

async def ws_send(ws:web.WebSocketResponse, data):
	info(f'data={data} {ws=}')
	d = {
		"type":1,
		"data":data
	}
	d = json.dumps(d, indent=4, ensure_ascii=False)
	try:
		return await ws.send_str(d)
	except Exception as e:
		exception(f'ws.send_str() error: {e=}')
		print_exc()
		return False

class WsSession:
	def __init__(self, session):
		self.session = session
		self.nodes = {}
	
	def join(node):
		self.nodes[node.id] = node
	
	def leave(node):
		self.nodes = {k:v for k,v in self.nodes.items() if k != node.id}
	
class WsData:
	def __init__(self):
		self.nodes = {}
		self.sessions = {}
	
	def add_node(self, node):
		self.nodes[node.id] = node
	
	def del_node(self, node):
		self.nodes = {k:v for k,v in self.nodes.items() if k!=node.id}
	
	def get_nodes(self):
		return self.nodes

	def get_node(self, id):
		return self.nodes.get(id)
	
	def add_session(self, session):
		self.sessions[session.sessionid] = session
	
	def del_session(self, session):
		self.sessions = {k:v for k,v in self.sessions.items() if k != session.sessionid}
	
	def get_session(self, id):
		return self.sessions.get(id)

class WsPool:
	def __init__(self, ws, ip, ws_path, app):
		self.app = app
		self.ip = ip
		self.id = None
		self.ws = ws
		self.ws_path = ws_path

	def get_data(self):
		r = self.app.get_data(self.ws_path)
		if r is None:
			r = WsData()
			self.set_data(r)
		return r

	def set_data(self, data):
		self.app.set_data(self.ws_path, data)

	def is_online(self, userid):
		data = self.get_data()
		node = data.get_node(userid)
		if node is None:
			return False
		return True

	def register(self, id):
		iddata = DictObject()
		iddata.id = id
		self.add_me(iddata)

	def add_me(self, iddata):
		data = self.get_data()
		iddata.ws = self.ws
		iddata.ip = self.ip
		self.id = iddata.id
		data.add_node(iddata)
		self.set_data(data)

	def delete_id(self, id):
		data = self.get_data()
		node = data.get_node(id)
		if node:
			data.del_node(node)
		self.set_data(data)

	def delete_me(self):
		self.delete_id(self.id)
		
	def add_session(self, session):
		data = self.get_data()
		data.add_session(session)
		self.set_data(data)
	
	def del_session(self, session):
		data = self.get_data()
		data.del_session(session)
		self.set_data(data)

	def get_session(self, sessionid):
		data = self.get_data()
		return data.get_session(sessionid)

	async def sendto(self, data, id=None):
		if id is None:
			return await ws_send(self.ws, data)
		d = self.get_data()
		iddata = d.get_node(id)
		ws = iddata.ws
		try:
			return await ws_send(ws, data)
		except:
			self.delete_id(id)

class WebsocketProcessor(PythonScriptProcessor):
	@classmethod
	def isMe(self,name):
		return name=='ws'

	async def path_call(self, request,params={}):
		cookie = request.headers.get('Sec-WebSocket-Protocol', None)
		if cookie:
			request.headers['Cookies'] = cookie
			userid = await get_user()
			debug(f'{cookie=}, {userid=}')
		await self.set_run_env(request)
		lenv = self.run_ns.copy()
		lenv.update(params)
		params_kw = lenv.params_kw
		userid = lenv.params_kw.userid or await lenv.get_user()
		del lenv['request']
		txt = await self.loadScript(self.real_path)
		ws = web.WebSocketResponse()
		try:
			await ws.prepare(request)
		except Exception as e:
			exception(f'--------except: {e}')
			print_exc()
			raise e
		ws_pool = WsPool(ws, request['client_ip'], request.path, request.app)
		debug(f'========== debug ===========')
		async for msg in ws:
			if msg.type == aiohttp.WSMsgType.TEXT:
				if msg.data == '_#_heartbeat_#_':
					await ws_send(ws, '_#_heartbeat_#_')
				else:
					lenv['ws_data'] = msg.data
					lenv['ws_pool'] = ws_pool
					exec(txt,lenv,lenv)
					func = lenv['myfunc']
					resp =  await func(request,**lenv)

			elif msg.type == aiohttp.WSMsgType.ERROR:
				error('ws connection closed with exception %s' % ws.exception())
				break
			else:
				info('datatype error', msg.type)
		debug(f'========== ws connection end ===========')
		ws_pool.delete_me()
		self.retResponse =  ws
		await ws.close()
		return ws

