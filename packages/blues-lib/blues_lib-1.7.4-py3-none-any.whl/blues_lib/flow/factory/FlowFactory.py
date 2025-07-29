import sys,os,re
from typing import Union,List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.flow.Flow import Flow
from flow.factory.CommandFactory import CommandFactory

class FlowFactory(Factory):
  
  def __init__(self,context:dict) -> None:
    self._context = context
    
  def create(self,arg:Union[List[str],str])->Flow:
    if isinstance(arg,str):
      return super().create(arg)
    else:
      return self.make(arg)
    
  def make(self,pre_names:List[str],core_names:List[str],post_names:List[str])->Flow:
    flow = Flow()

    self._add_cmd(flow,pre_names,'pre')
    self._add_cmd(flow,core_names,'core')
    self._add_cmd(flow,post_names,'post')

    return flow

  def _add_cmd(self,flow:Flow,names:List[str],hook:str):
    if not names:
      return

    for name in names:
      command = CommandFactory(self._context).create(name)
      if not command:
        continue
      
      if hook == 'pre':
        flow.add_pre_command(command)
      elif hook == 'core':
        flow.add_command(command)
      elif hook == 'post':
        flow.add_post_command(command)
  
  def create_mat_spider(self):
    core_names = ['input','browser','mat_crawler','persister','output']
    post_names = ['browser_quit','email']
    flow = self.make(None,core_names,post_names)
    return flow

  def create_step(self):
    core_names = ['input','browser','persister','output']
    flow = self.make(None,core_names,None)
    return flow
