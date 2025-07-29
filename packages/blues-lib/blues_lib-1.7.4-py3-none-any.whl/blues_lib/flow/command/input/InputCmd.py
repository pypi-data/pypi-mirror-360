import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command

class InputCmd(Command):

  name = __name__

  def execute(self):

    model = self._context.get('input')
    if not model:
      raise Exception('[InputCmd] The param input is missing!')

    if not model.config.get('browser'):
      raise Exception('[InputCmd] The param input.browser is missing!')

    if not model.config.get('crawler'):
      raise Exception('[InputCmd] The param input.crawler is missing!')

    if not model.config.get('persister'):
      raise Exception('[InputCmd] The param input.persister is missing!')
