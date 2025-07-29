import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from material.dao.mat.MatMutator import MatMutator

class PersisterCMD(Command):

  name = __name__
  
  mutator = MatMutator()

  def execute(self):

    material = self._context['ai'].get('material')
    conditions = [
      {
        'field':'material_id',
        'comparator':'=',
        'value':material['material_id']
      }
    ]
    entity = {
      'material_ai_title':material['material_ai_title'],
      'material_ai_body_text':material['material_ai_body_text'],
    }
    response = self.mutator.update(entity,conditions)
    self._context['ai']['persister'] = response

    if response['code'] != 200:
      raise Exception('[AI] Failed to update the ai writed fields to the DB!')
    