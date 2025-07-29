import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from material.DBMaterial import DBMaterial     

class MaterialCMD(Command):

  name = __name__

  def execute(self):
    executor_schema = self._context['ai']['schema'].get('executor')
    material_mode = executor_schema.material.get('mode')
    query_condition = {
      'mode':'latest',
      'material_type':material_mode,
      'count':1,
    }
    material = DBMaterial().first(query_condition)
    if not material:
      raise Exception('[AI] Failed to get available materials from the DB!')

    self._context['ai']['material'] = material
