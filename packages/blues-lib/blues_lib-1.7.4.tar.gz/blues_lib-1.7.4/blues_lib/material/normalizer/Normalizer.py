import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from util.BluesAlgorithm import BluesAlgorithm 

class Normalizer(AllMatchHandler):

  def resolve(self)->STDOut:
    stdout = self._get_input_error()
    if stdout.code!=200:
      self._logger.error(f'[Normalizer] {stdout.msg}')
      return stdout

    try:
      entities = self._request.get('entities')
      avail_entities = []

      for entity in entities:
        stdout = self._get_entity_error(entity)
        if stdout.code==200:
          self._normalize(entity)
          avail_entities.append(entity)
        else:
          self._logger.warning(f'[Normalizer] Skip a invalid entity - {entity["material_title"]} - {stdout.message}')

      self._request['entities'] = avail_entities
      if avail_entities:
        message = f'[Normalizer] Managed to retain {len(avail_entities)} valid entities'
        self._logger.info(message)
        return STDOut(200,message)
      else:
        message = f'[Normalizer] Failed to retain any entities - all are invalid'
        self._logger.error(message)
        return STDOut(500,message)

    except Exception as e:
      message = f'[Normalizer] Failed to normalized any entities - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    
  def _get_entity_error(self,entity:dict):
    if not entity.get('material_url'):
      return STDOut(400,'Received an empty material_url')
    if not entity.get('material_title'):
      return STDOut(400,'Received an empty material_title')
    return STDOut(200,'ok')

  def _get_input_error(self)->STDOut:
    entities = self._request.get('entities')
    if not entities:
      return STDOut(400,'Received an empty entity')
    model = self._request.get('model')
    if not model:
      return STDOut(400,'Received an empty model')
    config = model.config
    if not config:
      return STDOut(400,'Received an empty model config')
    mode = config.get('mode')
    if not mode:
      return STDOut(400,'Received an empty model config mode')
    site = config.get('site')
    if not site:
      return STDOut(400,'Received an empty model config site')
    return STDOut(200,'ok')

  def _normalize(self,entity):
    self._set_system_fileds(entity)
    # set for detail only
    self._set_body(entity)
  
  def _set_system_fileds(self,entity):
    config = self._request.get('model').config
    entity['material_type'] = config.get('mode') # article gallery shortvideo qa
    entity['material_site'] = config.get('site') # ifeng bbc
    entity['material_lang'] = config.get('lang','cn') # cn en
    id = config.get('site')+'_'+BluesAlgorithm.md5(entity['material_url'])
    entity['material_id'] = id

  def _set_body(self,entity:dict):
    rows = entity.get('material_body')
    if not rows:
      return

    paras:List[dict] = []
    for row in rows: 
      image = row.get('image')
      text = row.get('text')
      if image:
        paras.append({'type':'image','value':image})
      else:
        paras.append({'type':'text','value':text})
    entity['material_body'] = paras

