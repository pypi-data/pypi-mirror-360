import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from cleaner.controller.CleanerFlow import CleanerFlow 

class CleanerCMD(Command):

  name = __name__

  def execute(self):
    flow = CleanerFlow()
    stdout = flow.execute()
    if stdout.code!=200:
      raise Exception('[Cleaner] flow error: %s' % stdout.message)
    