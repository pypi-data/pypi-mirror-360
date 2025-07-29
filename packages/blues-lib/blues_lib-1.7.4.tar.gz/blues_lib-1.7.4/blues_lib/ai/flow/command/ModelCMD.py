import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from model.ReplacerModel import ReplacerModel

class ModelCMD(Command):

  name = __name__

  def execute(self):
    executor_schema = self._context['ai']['schema'].get('executor')
    # append query by the PromptCMD
    material = self._context['ai'].get('material')
    
    model = ReplacerModel(executor_schema,material).first()
    # override the placeholder schema
    model_schema = model.get('schema')

    if not model_schema:
      raise Exception('[AI] Failed to create a model schema!')

    self._context['ai']['schema']['executor'] = model_schema 
    