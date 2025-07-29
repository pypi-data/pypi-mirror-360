import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.output.STDOut import STDOut

class BrowserQuitCmd(Command):

  def execute(self):

    browser_output = self._context.get('browser')
    if browser_output:
      browser = browser_output.data
      browser.quit()
      message = f'[{self.__class__.__name__}] Managed to quit the browser!'
      self._logger.info(message)
      self._context['browser_quit'] = STDOut(200,message)
