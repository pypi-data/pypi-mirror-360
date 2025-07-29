import sys,os,re
from abc import ABC
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.model.Model import Model
from behavior.BhvExecutor import BhvExecutor
from util.BluesOS import BluesOS

class AIQuery(ABC):

  max_retry_time = 2
  
  def __init__(self,browser,schema):
    # { AIQASchema }
    self.schema = schema
    # {BluesLoginChrome}
    self.browser = browser
    # {int}
    self.retry_time = 0

  def execute(self):
    '''
    Fianl tempalte method
    Input question and return answer
    Returns {json} : json string
    '''
    try:
      value = self._ask()
      return self._retry(value)
    except Exception as e:
      raise Exception('ai error: '+str(e))
    finally:
      self.browser.quit()
      
  def _ask(self):
    BluesOS.clear()
    self._open()
    self._prepare()
    stdout = self._execute()
    value = self._read(stdout)
    if not value:
      value = self._copy()
    self._clean()
    return value

  def _open(self):
    url = self.schema.basic.get('url')
    current_url = self.browser.interactor.document.get_url() 
    if current_url!=url:
      self.browser.open(url)
  
  def _prepare(self):
    if self.schema.preparation:
      model = Model(self.schema.preparation)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def _execute(self):
    if self.schema.execution:
      model = Model(self.schema.execution)
      executor = BhvExecutor(model,self.browser)
      return executor.execute()

  def _read(self,stdout):
    # read content from the document element
    if stdout.data:
      content = stdout.data.get('content')
      if content:
        return self._extract(content)
    return None

  def _copy(self): 
    # copy content by click the copy button, it may be useless in DouBao
    text = BluesOS.copy()
    if not text:
      return None
    return self._extract(text)

  def _clean(self):
    if self.schema.cleanup:
      model = Model(self.schema.cleanup)
      executor = BhvExecutor(model,self.browser)
      executor.execute()
    
  def _extract(self,text):
    return text
  
  def _retry(self,value):
    if value:
      return value
    if self.retry_time<self.max_retry_time:
      self.retry_time+=1
      return self._ask()
    return None
