from abc import ABC, abstractmethod
from typing import List
import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser

class Behavior(ABC):
  def __init__(self,model:Model,browser:Browser=None)->None:
    self._meta = model.meta
    self._bizdata = model.bizdata
    self._config = model.config
    self._browser = browser

  @abstractmethod
  def execute(self)->STDOut:
    pass

  def set_model(self,model:Model)->None:
    self._model = model

  def set_browser(self,browser:Browser)->None:
    self._browser = browser

  def _get_kwargs(self,keys:List[str],config=None)->dict:
    '''
    Extract specified keys from configuration dictionary
    @param {List[str]} keys: list of keys to extract from config
    @param {dict} config: optional config dict to merge with self._config (config takes precedence)
    @return {dict}: dictionary containing only the specified keys and their values
    '''
    conf = {**self._config,**config} if config else self._config
    return {key:conf.get(key) for key in keys}