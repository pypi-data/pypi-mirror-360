import sys,os,re
from abc import ABC, abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from logger.LoggerFactory import LoggerFactory
from util.BluesMailer import BluesMailer  
from material.dao.login.LoginMutator import LoginMutator
from util.BluesURL import BluesURL

class LoginerForm(ABC):
  
  name = __name__

  def __init__(self,schema):
    # { LoginerSchema } 
    self.schema = schema
    # { Browser }
    self.browser = None
    # {logger}
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()
    # { LoginMutator }
    self.io = LoginMutator()

    #  { str } the site's main domain
    self.domain = BluesURL.get_main_domain(self.schema.basic.get('login_url'))

  def _mail(self,args:dict):

    mailer = BluesMailer.get_instance()
    subject = mailer.get_title_with_time(args['subject'])
    content = mailer.get_html_body('ICPS',args['para'],args['url'],args['url_text'])
    payload={
      'subject':subject,
      'content':content,
      'images':args.get('images'),
      'addressee':['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }
    result = mailer.send(payload)
    if result.get('code') == 200:
      self._logger.info('Sent the notify mail')
    else:
      self._logger.error('The notify mail was sent failed')