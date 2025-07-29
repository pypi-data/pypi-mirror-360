import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command

class OutputCmd(Command):

  name = __name__

  def execute(self):
    # point the core commands' last output
    self._context['output'] = self._context.get('crawler')

