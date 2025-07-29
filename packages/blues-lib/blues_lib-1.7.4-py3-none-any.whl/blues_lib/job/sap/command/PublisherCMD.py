import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from publisher.flow.PublisherFlow import PublisherFlow 

class PublisherCMD(Command):

  name = __name__

  def execute(self):
    flow = PublisherFlow(self._context)
    stdout = flow.execute()
    if stdout.code!=200:
      raise Exception('[Publisher] flow error: %s' % stdout.message)
    