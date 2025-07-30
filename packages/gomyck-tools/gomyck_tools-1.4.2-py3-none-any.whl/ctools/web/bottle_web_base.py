import inspect
import threading
from functools import wraps

import bottle
from bottle import response, Bottle, request

from ctools.dict_wrapper import DictWrapper
from ctools.sys_log import flog as log
from ctools.web import ctoken
from ctools.web.api_result import R

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 50
func_has_params = {}


class GlobalState:
  lock = threading.Lock()
  withOutLoginURI = [
    '/',
    '/index',
    '/login',
    '/favicon.ico',
  ]
  allowRemoteCallURI = [

  ]
  token = {}
  interceptors = []


def init_app(context_path=None):
  app = Bottle()
  app.context_path = context_path

  @app.hook('before_request')
  def before_request():
    for interceptor in GlobalState.interceptors:
      res: R = interceptor['func']()
      if res.code != 200: bottle.abort(res.code, res.message)

  @app.error(401)
  def unauthorized(error):
    response.status = 401
    log.error("系统未授权: {} {} {}".format(error.body, request.method, request.fullpath))
    return R.error(resp=R.Code.cus_code(401, "系统未授权! {}".format(error.body)))

  @app.error(403)
  def unauthorized(error):
    response.status = 403
    log.error("访问受限: {} {} {}".format(error.body, request.method, request.fullpath))
    return R.error(resp=R.Code.cus_code(403, "访问受限: {}".format(error.body)))

  @app.error(404)
  def not_found(error):
    response.status = 404
    log.error("404 not found : {} {} {}".format(error.body, request.method, request.fullpath))
    return R.error(resp=R.Code.cus_code(404, "资源未找到: {}".format(error.body)))

  @app.error(405)
  def method_not_allow(error):
    response.status = 405
    log.error("请求方法错误: {} {} {}".format(error.status_line, request.method, request.fullpath))
    return R.error(resp=R.Code.cus_code(405, '请求方法错误: {}'.format(error.status_line)))

  @app.error(500)
  def internal_error(error):
    response.status = 500
    log.error("系统发生错误: {} {} {}".format(error.body, request.method, request.fullpath))
    return R.error(msg='系统发生错误: {}'.format(error.exception))

  @app.hook('after_request')
  def after_request():
    enable_cors()

  app.install(params_resolve)
  return app


def enable_cors():
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
  request_headers = request.headers.get('Access-Control-Request-Headers')
  response.headers['Access-Control-Allow-Headers'] = request_headers if request_headers else ''
  response.headers['Access-Control-Expose-Headers'] = '*'


# annotation
def before_intercept(order=0):
  def decorator(func):
    log.info("add before interceptor: {}".format(func.__name__))
    GlobalState.interceptors.append({'order': order, 'func': func})
    GlobalState.interceptors = sorted(GlobalState.interceptors, key=lambda x: x['order'])

  return decorator


# annotation
def rule(key):
  def return_func(func):
    @wraps(func)
    def decorated(*args, **kwargs):
      # if GlobalState.licenseInfo is not None and key not in GlobalState.licenseInfo.access_module:
      #   log.error("系统未授权! {} {}".format(request.fullpath, '当前请求的模块未授权!请联系管理员!'))
      #   return R.error(resp=R.Code.cus_code(9999, "系统未授权! {}".format('当前请求的模块未授权!请联系管理员!')))
      return func(*args, **kwargs)

    return decorated

  return return_func


# annotation or plugins, has auto install, don't need to call
def params_resolve(func):
  @wraps(func)
  def decorated(*args, **kwargs):
    if func_has_params.get(request.fullpath) is not None and not func_has_params.get(request.fullpath):
      return func(*args, **kwargs)
    if func_has_params.get(request.fullpath) is None:
      sig = inspect.signature(func)
      params = sig.parameters
      if not params.get('params'):
        func_has_params[request.fullpath] = False
        return func(*args, **kwargs)
      else:
        func_has_params[request.fullpath] = True
    if request.method == 'GET':
      queryStr = request.query.decode('utf-8')
      page_info = PageInfo(
        page_size=10 if request.headers.get('page_size') is None else int(request.headers.get('page_size')),
        page_index=1 if request.headers.get('page_index') is None else int(request.headers.get('page_index'))
      )
      queryStr.page_info = page_info
      return func(params=queryStr, *args, **kwargs)
    elif request.method == 'POST':
      query_params = request.query.decode('utf-8')
      content_type = request.get_header('content-type')
      if content_type == 'application/json':
        params = request.json or {}
        dict_wrapper = DictWrapper(params)
        dict_wrapper.update(query_params.dict)
        return func(params=dict_wrapper, *args, **kwargs)
      elif 'multipart/form-data' in content_type:
        form_data = request.forms.decode()
        form_files = request.files.decode()
        dict_wrapper = DictWrapper(form_data)
        dict_wrapper.update(query_params.dict)
        dict_wrapper.files = form_files
        return func(params=dict_wrapper, *args, **kwargs)
      elif 'application/x-www-form-urlencoded' in content_type:
        params = request.forms.decode()
        dict_wrapper = DictWrapper(params.dict)
        dict_wrapper.update(query_params.dict)
        return func(params=dict_wrapper, *args, **kwargs)
      elif 'text/plain' in content_type:
        params = request.body.read().decode('utf-8')
        dict_wrapper = DictWrapper({'body': params})
        dict_wrapper.update(query_params.dict)
        return func(params=dict_wrapper, *args, **kwargs)
    else:
      return func(*args, **kwargs)

  return decorated


class PageInfo:
  def __init__(self, page_size, page_index):
    self.page_size = page_size
    self.page_index = page_index


# 通用的鉴权方法
def common_auth_verify(aes_key):
  if request.path.startswith('/static') or request.path in GlobalState.withOutLoginURI:
    return R.ok(to_json_str=False)
  auth_token = request.get_header('Authorization')
  if auth_token is None:
    auth_token = request.get_cookie('Authorization')
  payload = ctoken.get_payload(auth_token, aes_key)
  if payload:
    return R.ok(to_json_str=False)
  return R.error(resp=R.Code.cus_code(401, "请登录!"), to_json_str=False)
