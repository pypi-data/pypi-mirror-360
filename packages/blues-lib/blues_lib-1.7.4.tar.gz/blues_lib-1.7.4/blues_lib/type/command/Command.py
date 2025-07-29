import sys,os,re
from abc import ABC,abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from logger.LoggerFactory import LoggerFactory

class Command(ABC):

  name = __name__
  
  def __init__(self,context):
    self._context = context
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()

  @property
  def context(self):
    return self._context

  @abstractmethod  
  def execute(self):
    pass

