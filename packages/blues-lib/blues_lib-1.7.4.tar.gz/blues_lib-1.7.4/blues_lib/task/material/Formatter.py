import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.normalizer.Normalizer import Normalizer
from material.validator.Validator import Validator
from material.deduplicator.Deduplicator import Deduplicator

class Formatter(AllMatchHandler):
  
  def resolve(self)->STDOut:
    chain = self._get_chain()
    stdout = chain.handle()
    # parse the request entities
    if stdout.code!=200:
      return stdout
    
    return STDOut(200,'ok',self._request['entities'])
  
  def _get_chain(self)->AllMatchHandler:
    normalizer = Normalizer(self._request)
    deduplicator = Deduplicator(self._request)
    validator = Validator(self._request)
    
    normalizer.set_next(deduplicator).set_next(validator)
    return normalizer
