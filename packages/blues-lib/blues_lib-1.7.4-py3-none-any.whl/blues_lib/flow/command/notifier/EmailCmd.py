import sys,os,re
from typing import List

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from util.BluesMailer import BluesMailer  
from type.command.Command import Command

class EmailCmd(Command):

  name = __name__

  def execute(self):
    entities = None
    output:STDOut = self._context.get('output')
    if output and output.code==200:
      entities = output.data

    title = self._get_subject(entities)
    content = self._get_content(title,entities)
    subject = BluesMailer.get_title_with_time(title)
    stdout =  self._send(subject,content)
    self._context['email'] = stdout
    if stdout.code==200:
      message = f'[{self.__class__.__name__}] Managed to send a notification email'
      self._logger.info(message)
    else:
      message = f'[{self.__class__.__name__}] Failed to send a notification email'
      self._logger.error(message)

  def _get_subject(self,entities:List[dict])->str:
    subject = ''
    if entities:
      count = len(entities)
      subject = f'Managed to crawl and persist {count} entities'
    else:
      subject = 'Failed to crawl and persist entities'
    return subject

  def _get_content(self,title:str,entities:List[dict])->str:
    para = self._get_para(entities)
    url = self._logger.file
    url_text = f'Log File: {url}'
    return BluesMailer.get_html_body(title,para,url,url_text)
  
  def _get_para(self,entities:List[dict])->str:
    para = ''
    if not entities:
      return 'Failed to crawl entities'

    para = f'There are {len(entities)} entities:<br/>'

    for idx,entity in enumerate(entities):
      para+=f"{idx+1}. {entity['material_title']}</br>"
    return para

  def _send(self,subject:str,content:str)->STDOut:
    mailer = BluesMailer.get_instance()
    payload={
      'subject':subject,
      'content':content,
      'images':None,
      'addressee':['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }
    return mailer.send(payload)