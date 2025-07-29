import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.output.STDOut import STDOut
from material.dao.mat.MatMutator import MatMutator 

class PersisterCmd(Command):

  name = __name__
  mutator = MatMutator()

  def execute(self):
    model = self._context['input']
    node_config = model.config.get('persister',{})
    preview = int(node_config.get('preview',0))

    if preview == 1:
      message = f'[Persister] Managed to preview'
      self._logger.info(message)
      self._context['persister'] = STDOut(200,message)
      return 

    crawler_output = self._context.get('crawler')
    if not crawler_output:
      message = f'[Persister] Failed to persist - no crawler output'
      self._logger.warning(message)
      return

    entities = crawler_output.data
    stdout = self.mutator.insert(entities)
    self._context['persister'] = stdout

    if stdout.code != 200:
      message = f'[PersisterCmd] Failed to persist - {stdout.message}'
      raise Exception(message)
    else:
      message = f'[Persister] Managed to persist'
      self._logger.info(message)


