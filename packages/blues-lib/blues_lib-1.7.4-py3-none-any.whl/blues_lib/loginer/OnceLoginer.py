import sys,os,re
from .Loginer import Loginer
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.browser.BluesStandardChrome import BluesStandardChrome     
from sele.browser.BluesHeadlessChrome import BluesHeadlessChrome     

class OnceLoginer(Loginer):
  '''
  @description: In a single login, the Browser instance is returned without saving the cookie
  '''
  def set_browser(self):
    # only support standard and headless mode
    browser_mode = self.schema.browser.get('mode')
    executable_path = self.schema.browser.get('path')
    if browser_mode=='headless':
      self.browser = BluesHeadlessChrome(executable_path=executable_path)
    else:
      self.browser = BluesStandardChrome(executable_path=executable_path)

  def success(self):
    self._logger.info('Login successfully')
    return self.browser
