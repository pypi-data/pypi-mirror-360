import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from schema.factory.LoginerSchemaFactory import LoginerSchemaFactory
from schema.factory.AISchemaFactory import AISchemaFactory

class SchemaCMD(Command):

  name = __name__

  def execute(self):
    loginer_stereotype = self._context['ai']['stereotype'].get('loginer')
    loginer_mode = loginer_stereotype['basic'].get('mode')
    loginer_schema = LoginerSchemaFactory(loginer_stereotype).create(loginer_mode)
    if not loginer_schema:
      raise Exception('[AI] Failed to create the loginer schema!')

    executor_stereotype = self._context['ai']['stereotype'].get('executor')
    executor_mode = executor_stereotype['basic'].get('mode')
    executor_schema = AISchemaFactory(executor_stereotype).create(executor_mode)
    if not executor_schema:
      raise Exception('[AI] Failed to create the executor schema!')

    self._context['ai']['schema'] = {
      'loginer':loginer_schema,
      'executor':executor_schema,
    }
