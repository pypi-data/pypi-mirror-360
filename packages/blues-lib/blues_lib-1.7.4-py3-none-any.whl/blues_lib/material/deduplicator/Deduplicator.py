import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.dao.mat.MatQuerier import MatQuerier

class Deduplicator(AllMatchHandler):

  def resolve(self):
    avail_entities = []
    entities = self._request.get('entities')
    if not entities:
      message = f'[Deduplicator] Received an empty entity'
      self._logger.error(message)
      return STDOut(400,message)

    querier = MatQuerier()

    for entity in entities:
      if querier.exist(entity):
        self._logger.warning(f'[Deduplicator] Skip a existing entity - {entity["material_title"]}')
      else:
        avail_entities.append(entity)

    self._request['entities'] = avail_entities
    
    if avail_entities:
      message = f'[Deduplicator] Managed to retain {len(avail_entities)} valid entities'
      self._logger.info(message)
      return STDOut(200,message)
    else:
      message = f'[Deduplicator] Failed to retain any valid entities - all exist'
      self._logger.error(message)
      return STDOut(500,message)