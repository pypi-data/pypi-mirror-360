import sys,os,re,time
from abc import ABC
from .LoginerForm import LoginerForm 

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.model.Model import Model
from behavior.BhvExecutor import BhvExecutor
from util.BluesDateTime import BluesDateTime

class QRCodeLoginerForm(LoginerForm,ABC):
  
  name = __name__

  def __init__(self,schema):

    super().__init__(schema)
    
    # { int } Verification code expiration seconds
    self.verify_max_time = self.schema.basic.get('verify_max_time')
  
    # { int } the last mail sent timestamp 
    self.mail_sent_ts = 0
    # shot imge local file
    self.qrcode_image = ''
  
  # template method
  def perform(self,browser):
    self.browser = browser
    self.prepare() 
    self.execute() 
    self.mail()
    self.wait()
    self.clean()
  
  # === step methods ===
  def prepare(self):
    if self.schema.preparation:
      model = Model(self.schema.preparation)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def execute(self):
    model = Model(self.schema.execution)
    executor = BhvExecutor(model,self.browser)
    outcome = executor.execute()
    if outcome.data:
      self.qrcode_image = outcome.data.get('shot')
      self._logger.info('The qrcode image: %s' % self.qrcode_image)
    else:
      self._logger.error('Shot the qrcode failed')

  def clean(self):
    if self.schema.cleanup:
      model = Model(self.schema.cleanup)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def mail(self):
    if not self.qrcode_image:
      return

    self.mail_sent_ts = BluesDateTime.get_timestamp()
    para = 'The %s account needs to be re-logged in, a auth QRCode has been sent, please scan it by WeChat within %s seconds.' % (self.domain,self.verify_max_time)
    url = 'http://deepbluenet.com/naps-upload-code.html?site=%s&ts=%s' % (self.domain,self.mail_sent_ts)
    payload={
      'subject':'NAPS: Sacn QRCode by WeChat',
      'para':para,
      'url':url,
      'url_text':'Click here to open the upload page.',
      'images':[self.qrcode_image],
    }
    self._mail(payload)

  def wait(self):
    if not self.qrcode_image:
      return 

    step = 10
    login_element = self.schema.basic.get('login_element')
    time_nodes =  list(range(0,self.verify_max_time,step)) 
    i = 0
    for time_node in time_nodes:
      i+=1
      has_landed = not self.browser.element.finder.find(login_element)
      if has_landed:
        break

      BluesDateTime.count_down({
        'duration':step,
        'title':'Waiting for scanning .[%s/%s] ...' % (i*step,self.verify_max_time)
      })