import sys,os,re
from urllib.parse import urlparse
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from material.file.MatFile import MatFile

class Localizer(AllMatchHandler):

  def resolve(self)->STDOut:

    entities = self._request.get('entities')
    if not entities:
      message = f'[Localize] Received a empty entity'
      self._logger.error(message)
      return STDOut(400,message)

    try:
      avail_entities = []
      for entity in entities:
        is_success = self._set_asset(entity)
        if is_success:
          avail_entities.append(entity)
        else:
          self._logger.warning(f'[Localizer] Skip a unlocalized entity - {entity["material_title"]}')

      self._request['entities'] = avail_entities

      if avail_entities:
        message = f'[Localize] Managed to retain {len(avail_entities)} valid entities'
        self._logger.info(message)
        return STDOut(200,message)
      else:
        message = f'[Localize] Failed to reatin any entities - all are unlocalized'
        self._logger.error(message)
        return STDOut(500,message)
    except Exception as e:
      message = f'[Localize] Failed to localize - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    
  def _is_http_url(self,url: str) -> bool:
    try:
      result = urlparse(url)
      # 检查 scheme 是否为 http 或 https，并且 netloc（域名）不为空
      return result.scheme in ('http', 'https') and bool(result.netloc)
    except ValueError:
      return False
    
  def _set_asset(self,entity:dict)->bool:
    config = self._request.get('model').config
    max_image_count = int(config.get('max_image_count',0))
    self._set_thumbnail(entity)
    is_success = self._set_body_images(entity,max_image_count)
    if is_success and entity.get('material_thumbnail'):
      return True
    else:
      return False
    
  def _set_thumbnail(self,entity)->bool:
      # convert online image to local image
      url = entity.get('material_thumbnail')
      if not self._is_http_url(url):
        return False

      site = entity.get('material_site')
      id = entity.get('material_id') 
      stdout = MatFile.get_download_image(site,id,url)
      if stdout.code==200:
        entity['material_thumbnail'] = stdout.data
        return True 
      else:
        self._logger.warning(f'[Localize] {stdout.message} - {stdout.data}')
        return False

  def _set_body_images(self,entity:dict,max_image_count:int)->bool:
    paras = entity.get('material_body')
    if not paras:
      return True # don't need to set body images

    image_count = 0

    images:List[str] = [] 
    for para in paras:
      # download and deal image
      success = self._download(entity,para,images)
      if success:
        image_count+=1
      if max_image_count and image_count>=max_image_count:
        break

    self._pad_image(entity,images)
    self._pad_thumbnail(entity,images)
    return image_count>0
    
  def _download(self,entity:dict,para:dict,images:List[str])->bool:
    if para['type'] != 'image':
      return False

    site = entity.get('material_site')
    id = entity.get('material_id')
    url = para['value']
    if not self._is_http_url(url):
      return False
    stdout = MatFile.get_download_image(site,id,url)
    if stdout.code!=200:
      self._logger.error(f'[Localize] {stdout.message} - {stdout.data}')
      return False

    para['value'] = stdout.data
    images.append(stdout.data)
    return True

  def _pad_image(self,entity:dict,images:List[str]):
    material_thumbnail = entity.get('material_thumbnail')
    paras = entity.get('material_body')
    if not images and material_thumbnail:
      paras.append({'type':'image','value':material_thumbnail})
  
  def _pad_thumbnail(self,entity:dict,images:List[str]):
    if not entity.get('material_thumbnail') and images:
      entity['material_thumbnail'] = images[0]
