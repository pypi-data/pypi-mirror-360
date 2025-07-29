import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from reporter.controller.ReporterFlow import ReporterFlow

class ReporterCMD(Command):

  name = __name__

  def execute(self):
    flow = ReporterFlow(self._context)
    stdout = flow.execute()
    if stdout.code!=200:
      raise Exception('[Reporter] flow error: %s' % stdout.message)
    