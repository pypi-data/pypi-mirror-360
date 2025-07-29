import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser
from task.crawler.Crawler import Crawler
from logger.LoggerFactory import LoggerFactory

class DepthCrawler():
  
  URL_KEY_IN_ENTITY = 'url'

  def __init__(self,model:Model,browser:Browser,keep_alive:bool=True) -> None:

    '''
    @param model {Model} : the model of page crawler
    @param browser {Browser} : the browser instance to use
    @param keep_alive {bool} : whether to keep the browser alive after crawl
    '''
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()

    self._browser = browser
    self._keep_alive = keep_alive

    self._model = model 
    self._bizdata = model.bizdata

    self._config = model.config
    self._count = int(self._config.get('count',0))
    self._url_key_in_entity = self._config.get('url_key_in_entity',self.URL_KEY_IN_ENTITY)

    self._meta = model.meta
    self._layers = self._meta.get('layers')
    self._max_depth = len(self._layers)
    
    self._entities = []
    self._visited_urls = set()

  def crawl(self)->STDOut:
    try:
      self._dfs()
      if self._entities:
        entities = self._entities[:self._count]
        message = self._get_avail_message(entities)
        self._logger.info(message)
        return STDOut(200,message,entities)
      else:
        message = '[DepthCrawler] Failed to crawl any entities!'
        self._logger.error(message)
        return STDOut(400,message)
    except Exception as e:
      message = f'[DepthCrawler] Failed to crawl any entities - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    finally:
      if self._browser and not self._keep_alive:
        self._browser.quit()

  def _get_avail_message(self,entities:List[dict])->str:
    return f'[DepthCrawler] Managed to crawl {len(entities)} entities'

  def _get_bizdata(self,parent_entity):
    if not parent_entity:
      return self._bizdata

    # cover the parent url value
    url = parent_entity.get(self._url_key_in_entity)
    if not url:
      return None

    return {
      **self._bizdata,
      'url':url,
    }

  def _crawl(self,depth,parent_entity:dict=None)->List[dict]:
    meta = self._layers[depth-1] 
    bizdata = self._get_bizdata(parent_entity)
    if not bizdata:
      return []
    
    if bizdata['url'] in self._visited_urls:
      return []

    model = Model(meta,bizdata)
    self._visited_urls.add(bizdata['url'])

    crawler = Crawler(model,self._browser)
    stdout = crawler.crawl()
    return stdout.data if stdout.data else []
    
  def _dfs(self,depth:int=1,parent_entity:dict=None):
      
    if self._should_stop():
      return

    entities = self._crawl(depth,parent_entity)
    if not entities:
      return

    # Validate the legitimacy and format the data before storing the value and entering the next iteration.
    fmt_entities = self._get_fmt_entities(entities,parent_entity)
    if not fmt_entities:
      return

    if depth == self._max_depth:
      asset_entities = self._get_asset_entities(fmt_entities)
      if asset_entities:
        self._entities.extend(asset_entities)

    if depth < self._max_depth:
      for entity in fmt_entities:
        self._dfs(depth+1,entity)
        
  def _should_stop(self):
    return self._count > 0 and len(self._entities) >= self._count
        
  def _get_asset_entities(self,entities:List[dict]):
    '''
    This is a template method, the sub class will localize or cloudifer the entities
    '''
    return entities

  def _get_fmt_entities(self,entities:List[dict],parent_entity:dict=None):
    '''
    This is a template method, the sub class will cover this formatter method
    '''
    return entities