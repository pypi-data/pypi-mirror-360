import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from spider.flow.SpiderFlow import SpiderFlow 
from spider.flow.SpiderFlowScheduler import SpiderFlowScheduler

class SpiderCMD(Command):

  name = __name__

  def execute(self):

    if self._context['spider'].get('contexts'):
      flow = SpiderFlowScheduler(self._context['spider'])
    else:
      flow = SpiderFlow(self._context)
    stdout = flow.execute()
    if stdout.code!=200:
      raise Exception('[Spider] flow error: %s' % stdout.message)
    