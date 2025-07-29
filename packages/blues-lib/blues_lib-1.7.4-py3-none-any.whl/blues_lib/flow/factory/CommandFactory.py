import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory

from flow.command.input.InputCmd import InputCmd

from flow.command.browser.BrowserCmd import BrowserCmd
from flow.command.browser.BrowserQuitCmd import BrowserQuitCmd

from flow.command.crawler.DepthCrawlerCmd import DepthCrawlerCmd
from flow.command.crawler.MatCrawlerCmd import MatCrawlerCmd

from flow.command.persister.PersisterCmd import PersisterCmd
from flow.command.output.OutputCmd import OutputCmd

from flow.command.notifier.EmailCmd import EmailCmd

class CommandFactory(Factory):
  
  def __init__(self,context:dict) -> None:
    self._context = context
    
  def create_input(self):
    return InputCmd(self._context)
    
  def create_browser(self):
    return BrowserCmd(self._context)
   
  def create_browser_quit(self):
    return BrowserQuitCmd(self._context)
  
  def create_depth_crawler(self):
    return DepthCrawlerCmd(self._context)
  
  def create_mat_crawler(self):
    return MatCrawlerCmd(self._context)
  
  def create_persister(self):
    return PersisterCmd(self._context)
  
  def create_output(self):
    return OutputCmd(self._context)
  
  def create_email(self):
    return EmailCmd(self._context)
  