
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from ai.prompt.AIPrompt import AIPrompt 

class PromptCMD(Command):

  name = __name__

  def execute(self):
    prompt_stereotype = self._context['ai']['stereotype'].get('prompt')

    material = self._context['ai']['material']
    if not material:
      raise Exception('[AI] The param ai.material is missing!')

    if not material['material_body_text']:
      raise Exception('[AI] The param ai.material.material_body_text is missing!')

    article = ''.join(material['material_body_text'])
    prompt = AIPrompt(prompt_stereotype,article)
    query = prompt.get()

    material['query'] = query
  