import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from sele.browser.BrowserFactory import BrowserFactory   

class BrowserCMD(Command):

  name = __name__

  def execute(self):
    executor_schema = self._context['ai']['schema'].get('executor')
    executable_path = executor_schema.browser.get('path')
    browser_mode = executor_schema.browser.get('mode') # login or headlesslogin

    loginer_schema = self._context['ai']['schema'].get('loginer')
    browser = BrowserFactory(browser_mode).create(executable_path=executable_path,loginer_schema=loginer_schema)

    if not browser:
      raise Exception('[AI] Failed to create the browser!')

    self._context['ai']['browser'] = browser
