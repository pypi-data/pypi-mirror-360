import sys,os,re
from abc import ABC,abstractmethod
from .LoginerForm import LoginerForm
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.model.Model import Model
from behavior.BhvExecutor import BhvExecutor

class AccountLoginerForm(LoginerForm,ABC):

  name = __name__

  def perform(self,browser):
    '''
    Implement the template method
    '''
    self.browser = browser
    self.prepare() 
    self.execute() 
    self.clean()
  
  def prepare(self):
    if self.schema.preparation:
      model = Model(self.schema.preparation)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def execute(self):
    if self.schema.execution:
      model = Model(self.schema.execution)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def clean(self):
    if self.schema.cleanup:
      model = Model(self.schema.cleanup)
      executor = BhvExecutor(model,self.browser)
      executor.execute()
