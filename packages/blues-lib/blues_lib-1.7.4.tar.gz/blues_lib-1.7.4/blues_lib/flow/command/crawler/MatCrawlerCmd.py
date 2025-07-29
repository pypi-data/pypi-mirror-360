import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.model.Model import Model
from task.crawler.MatCrawler import MatCrawler

class MatCrawlerCmd(Command):

  name = __name__

  def execute(self):

    model = self._context['input']
    node_meta = model.meta.get('crawler')
    browser = self._context['browser'].data

    node_model = Model(node_meta,model.bizdata)
    crawler = MatCrawler(node_model,browser)
    stdout = crawler.crawl()
    self._context['crawler'] = stdout

    if stdout.code!=200 or not stdout.data:
      raise Exception('[MatCrawlerCmd] Failed to crawl available entities!')
    else:
      self._logger.info('[MatCrawlerCmd] Managed to crawl available entities!')


