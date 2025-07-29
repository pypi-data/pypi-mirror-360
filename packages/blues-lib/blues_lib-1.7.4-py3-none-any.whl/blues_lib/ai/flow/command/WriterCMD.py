import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from ai.factory.AIFactory import AIFactory   

class WriterCMD(Command):

  name = __name__

  def execute(self):
    browser = self._context['ai'].get('browser')
    executor_schema = self._context['ai']['schema'].get('executor')
    mode = executor_schema.basic.get('mode')

    executor = AIFactory(browser,executor_schema).create(mode)
    if not executor:
      raise Exception('[AI] Failed to create a writer executor!')

    entity = executor.execute()
    if not entity:
      raise Exception('[AI] Failed to write by the AI!')

    self._context['ai']['material'].update(entity)


