import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from ai.flow.AIWriterFlow import AIWriterFlow

class WriterCMD(Command):

  name = __name__

  def execute(self):
    flow = AIWriterFlow(self._context)
    stdout = flow.execute()
    if stdout.code!=200:
      raise Exception('[AI] flow error: %s' % stdout.message)
    