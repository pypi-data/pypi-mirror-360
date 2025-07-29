import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from task.crawler.DepthCrawler import DepthCrawler
from task.material.Formatter import Formatter
from material.asseter.Localizer import Localizer

class MatCrawler(DepthCrawler):

  URL_KEY_IN_ENTITY = 'material_url'
        
  def _get_fmt_entities(self,entities:List[dict],parent_entity:dict=None):
    '''
    Cover the super template : format the entities
    '''
    combined_entities = []
    if parent_entity:
      # append the brief's fields to the detail
      for entity in entities:
        combined_entities.append({**parent_entity,**entity})
    else:
      combined_entities = entities

    request = {
      'model':self._model,
      'entities':combined_entities,
    }
    formatter = Formatter(request)
    stdout = formatter.handle()
    if stdout.code!=200:
      return []
    return request['entities']
  
  def _get_asset_entities(self,entities:List[dict]):
    '''
    Cover the super template : localize the entities
    '''
    request = {
      'entities':entities,
      'model':self._model,
    }
    localizer = Localizer(request)
    localizer.handle()
    return request['entities']

  def _get_avail_message(self,entities:List[dict])->str:
    titles = []
    for entity in entities:
      titles.append(entity['material_title'])
    return f'[MatCrawler] Managed to crawl {len(entities)} entities:\n{titles}'