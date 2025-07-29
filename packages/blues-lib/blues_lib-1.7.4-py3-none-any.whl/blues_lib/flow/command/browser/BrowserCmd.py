import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.output.STDOut import STDOut
from sele.browser.BrowserFactory import BrowserFactory   

class BrowserCmd(Command):

  def execute(self):

    model = self._context['input']
    node_config = model.config.get('browser')

    browser_mode = node_config.get('mode')
    executable_path = node_config.get('path')

    browser = BrowserFactory(browser_mode).create(executable_path=executable_path)

    if browser:
      message = f'[BrowserCmd] Managed to create a browser!'
      self._context['browser'] = STDOut(200,message,browser)
      self._logger.info(message)
    else:
      raise Exception(f'[BrowserCmd] Failed to create a browser!')