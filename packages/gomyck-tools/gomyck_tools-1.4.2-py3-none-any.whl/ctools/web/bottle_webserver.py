import sys
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server

from bottle import ServerAdapter, Bottle, template, static_file, abort, redirect, response

from ctools import sys_info

"""
module_names = list(globals().keys())
def get_modules():
  mods = []
  for modname in module_names:
    if modname == 'base' or modname == 'online' or modname.startswith('__') or modname == 'importlib': continue
    module = globals()[modname]
    mods.append(module)
  return mods

def get_ws_modules():
  from . import websocket
  return [websocket]
"""

"""
from ctools.web import bottle_web_base, ctoken, bottle_webserver
from ctools.web.api_result import R

secret_key = "xxx"
app = bottle_web_base.init_app('子模块写 context_path, 主模块就不用写任何东西')

# 通用的鉴权方法
@bottle_web_base.before_intercept(0)
def token_check():
  return bottle_web_base.common_auth_verify(secret_key)

@app.post('/login')
def login(params):
  return R.ok(ctoken.gen_token({'username': 'xxx'}, secret_key, 3600))

@app.get('/demo')
@bottle_web_base.rule('DOC:DOWNLOAD')
def demo(params):
  print(params)

if __name__ == '__main__':
  main_app = bottle_webserver.init_bottle() # 这里可以传 APP 当做主模块, 但是 context_path 就不好使了, 上下文必须是 /
  main_app.mount(app.context_path, app)
  main_app.set_index(r'index.html')
  main_app.run()
"""

_default_port = 8888


class CBottle:

  def __init__(self, bottle: Bottle, port=_default_port, quiet=False):
    self.port = port
    self.quiet = quiet
    self.bottle = bottle
    self.index_root = './'
    self.index_filename = 'index.html'
    self.is_tpl = False
    self.tmp_args = {}
    self.redirect_url = None
    self.static_root = './static'
    self.download_root = './download'

    @self.bottle.route(['/', '/index'])
    def index():
      try:
        if self.redirect_url: return redirect(self.redirect_url)
        if self.is_tpl: return template(f"{self.index_root}/{self.index_filename}", self.tmp_args)
        return static_file(filename=self.index_filename, root=self.index_root)
      except FileNotFoundError:
        abort(404, "File not found...")

    @self.bottle.route('/static/<filepath:path>')
    def static(filepath):
      try:
        return static_file(filepath, root=self.static_root)
      except FileNotFoundError:
        abort(404, "File not found...")

    @self.bottle.route('/download/<filepath:path>')
    def download(filepath):
      return static_file(filepath, root=self.download_root, download=True)

    @self.bottle.route('/favicon.ico')
    def favicon():
      response.content_type = 'image/svg+xml'
      svg_icon = '''<?xml version="1.0" encoding="UTF-8"?>
      <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
          <circle cx="16" cy="16" r="14" fill="#007bff"/>
          <path d="M16 8a8 8 0 0 0-8 8h2a6 6 0 0 1 12 0h2a8 8 0 0 0-8-8z" fill="white"/>
          <circle cx="16" cy="20" r="2" fill="white"/>
      </svg>
      '''
      return svg_icon

  def run(self):
    http_server = WSGIRefServer(port=self.port)
    print('Click the link below to open the service homepage %s' % '\n \t\t http://localhost:%s \n \t\t http://%s:%s' % (self.port, sys_info.get_local_ipv4(), self.port), file=sys.stderr)
    self.bottle.run(server=http_server, quiet=self.quiet)

  def set_index(self, filename='index.html', root='./', is_tpl=False, redirect_url=None, **kwargs):
    self.index_root = root
    self.index_filename = filename
    self.is_tpl = is_tpl
    self.redirect_url = redirect_url
    self.tmp_args = kwargs

  def set_static(self, root='./static'):
    self.static_root = root

  def set_download(self, root='./download'):
    self.download_root = root

  def mount(self, context_path, app, **kwargs):
    if not context_path: return
    self.bottle.mount(context_path, app, **kwargs)


def init_bottle(app: Bottle = None, port=_default_port, quiet=False) -> CBottle:
  bottle = app or Bottle()
  return CBottle(bottle, port, quiet)


class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
  daemon_threads = True


class CustomWSGIHandler(WSGIRequestHandler):
  def log_request(*args, **kw): pass


class WSGIRefServer(ServerAdapter):

  def __init__(self, host='0.0.0.0', port=_default_port):
    super().__init__(host, port)
    self.server = None

  def run(self, handler):
    req_handler = WSGIRequestHandler
    if self.quiet: req_handler = CustomWSGIHandler
    self.server = make_server(self.host, self.port, handler, server_class=ThreadedWSGIServer, handler_class=req_handler)
    self.server.serve_forever()

  def stop(self):
    self.server.shutdown()
