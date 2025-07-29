from abc import ABC,abstractmethod

class LoginerFactory(ABC):
  '''
  Abstract Factory Mode, use best practices:
  1. Each specific class is created using an independent method
  2. Use instance usage and parameters as class fields
  '''
  
  def __init__(self,schema):
    self._schema = schema

  def create(self,mode:str):
    if mode == 'account':
      return self.create_account()
    elif mode == 'mac':
      return self.create_mac()
    elif mode == 'qrc':
      return self.create_qrc()
    else:
      return None

  @abstractmethod
  def create_account(self):
    pass
  
  @abstractmethod
  def create_mac(self):
    pass

  @abstractmethod
  def create_qrc(self):
    pass
