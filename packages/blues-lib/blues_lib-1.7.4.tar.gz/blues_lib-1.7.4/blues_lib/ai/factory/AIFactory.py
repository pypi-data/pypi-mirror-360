import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from ai.writer.AIWriter import AIWriter

class AIFactory(Factory):
  def __init__(self,browser,schema):
    self._browser = browser
    self._schema = schema

  def create_writer(self):
    return AIWriter(self._browser,self._schema)
  