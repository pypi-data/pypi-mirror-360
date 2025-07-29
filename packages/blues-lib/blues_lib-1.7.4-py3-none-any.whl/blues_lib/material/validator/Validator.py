import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from util.BluesType import BluesType

class Validator(AllMatchHandler):
  
  REQUIRED_BRIEF_FIELDS = ['material_id','material_site','material_title','material_url']
  REQUIRED_DETAIL_FIELDS = ['material_id','material_site','material_title','material_url','material_thumbnail','material_body']

  def resolve(self):
    entities = self._request.get('entities')
    if not entities:
      message = f'[Validator] Received an empty entity'
      self._logger.error(message)
      return STDOut(400,message)

    avail_entities = []
    for entity in entities:
      if not self._is_field_satisfied(entity):
        self._logger.warning(f'[Validator] Skip a field-not-satisfied entity')
      elif not self._is_length_valid(entity):
        self._logger.error(f'[Validator] Skip a content-too-long-or-short entity')
      else:
        avail_entities.append(entity)

    self._request['entities'] = avail_entities

    if avail_entities:
      message = f'[Validator] Managed to retain {len(avail_entities)} valid entities'
      self._logger.info(message)
      return STDOut(200,message)
    else:
      message = f'[Validator] Failed to retain any valid entities - all are invalid'
      self._logger.error(message)
      return STDOut(500,message)
    
  def _is_field_satisfied(self,entity)->bool:
    fields = None
    if entity.get('material_body'):
      fields = self.REQUIRED_DETAIL_FIELDS
    else:
      fields = self.REQUIRED_BRIEF_FIELDS
    return BluesType.is_field_satisfied_dict(entity,fields,True)

  def _is_length_valid(self,entity:dict)->bool:
    if not entity.get('material_body'):
      return True

    config = self._request.get('model').config
    if not config:
      return True

    text_length = self._get_text_length(entity)

    min_text_length = int(config.get('min_text_length',0))
    if min_text_length and text_length<min_text_length:
      return False

    max_text_length = int(config.get('max_text_length',0))
    if max_text_length and text_length>max_text_length:
      return False

    return True
  
  def _get_text_length(self,entity:dict)->int:
    paras:List[str] = entity.get('material_body')
    size = 0
    if not paras:
      return size
    
    for para in paras:
      if para['type'] == 'text':
        size+=len(para['value'])
    return size
    
    


