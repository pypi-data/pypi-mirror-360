import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command

class InputCMD(Command):

  name = __name__

  def execute(self):

    if not self._context.get('spider'):
      raise Exception('[SAP] The param spider is missing!')
      
    if not self._context.get('ai'):
      raise Exception('[SAP] The param ai is missing!')

    if not self._context.get('publisher'):
      raise Exception('[SAP] The param publisher is missing!')





