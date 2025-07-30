import os
import shutil

from sqlalchemy.sql import text

from ctools import database


class Patch:

  def __init__(self, oldVersion, newVersion, pythonPath, playwrightPath, driverPath) -> None:
    super().__init__()
    self.oldV = oldVersion[len('V'):].replace('.', '').replace('-snapshot', '')
    self.currentV = newVersion[len('V'):].replace('.', '').replace('-snapshot', '')
    self.snapshot = '-snapshot' in newVersion or '-snapshot' in oldVersion
    self.pythonPath = pythonPath
    self.playwrightPath = playwrightPath
    self.driverPath = driverPath
    self.deleteSDK, self.deleteHPL, self.deleteDriver = False, False, False

  def apply_patch(self):
    patch_methods = [method for method in dir(self) if callable(getattr(self, method)) and method.startswith('patch_V')]
    patch_methods.sort(key=lambda x: int(x[len('patch_V'):]))
    max_method_name = patch_methods[-1]
    exec_max_method = False
    for method_name in patch_methods:
      slVersion = method_name[len('patch_V'):]
      if int(self.currentV) > int(slVersion) >= int(self.oldV):
        if max_method_name == method_name: exec_max_method = True
        method = getattr(self, method_name)
        print('start exec patch {}'.format(method_name))
        method()
        print('patch {} update success'.format(method_name))
    if self.snapshot and not exec_max_method:
      print('start exec snapshot patch {}'.format(max_method_name))
      method = getattr(self, max_method_name)
      method()
      print('snapshot patch {} update success'.format(max_method_name))

  def patch_V220(self):
    pass

  def run_sqls(self, sqls):
    with database.get_session() as s:
      for sql in sqls.split(";"):
        try:
          s.execute(text(sql.strip()))
          s.commit()
        except Exception as e:
          print('结构升级错误, 请检查!!! {}'.format(e.__cause__))

  def remove_sdk(self):
    if self.deleteSDK: return
    try:
      self.deleteSDK = True
      if os.path.exists(self.pythonPath): shutil.rmtree(self.pythonPath)
    except Exception as e:
      print('删除SDK错误: {}'.format(e))

  def remove_hpl(self):
    if self.deleteHPL: return
    try:
      self.deleteHPL = True
      if os.path.exists(self.playwrightPath): shutil.rmtree(self.playwrightPath)
    except Exception as e:
      print('删除HPL错误: {}'.format(e))

  def remove_driver(self):
    if self.deleteDriver: return
    try:
      self.deleteDriver = True
      if os.path.exists(self.driverPath): shutil.rmtree(self.driverPath)
    except Exception as e:
      print('删除Driver错误: {}'.format(e))
