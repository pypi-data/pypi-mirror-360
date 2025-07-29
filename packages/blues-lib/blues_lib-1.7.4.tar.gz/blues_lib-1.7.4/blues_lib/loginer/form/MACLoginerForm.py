import sys,os,re
from abc import ABC
from .LoginerForm import LoginerForm 

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.model.Model import Model
from behavior.BhvExecutor import BhvExecutor
from util.BluesDateTime import BluesDateTime

class MACLoginerForm(LoginerForm,ABC):
  
  name = __name__

  def __init__(self,schema):

    super().__init__(schema)
    
    # { int } Verification code expiration seconds
    self.verify_max_time = self.schema.basic.get('verify_max_time')
  
    # { int } the last mail sent timestamp 
    self.mail_sent_ts = 0
    # { str } the dynamic sms auth code
    self.auth_code = ''
  
  # template method
  def perform(self,browser):
    self.browser = browser
    self.prepare() 
    self.execute() 
    self.mail()
    self.wait()
    self.verify() 
    self.clean()
  
  # === step methods ===
  def prepare(self):
    if self.schema.preparation:
      model = Model(self.schema.preparation)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def execute(self):
    if self.schema.execution:
      model = Model(self.schema.execution)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def clean(self):
    if self.schema.cleanup:
      model = Model(self.schema.cleanup)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  def mail(self):
    self.mail_sent_ts = BluesDateTime.get_timestamp()
    para = 'The %s account needs to be re-logged in, a verification code has been sent, please upload it within %s seconds.' % (self.domain,self.verify_max_time)
    url = 'http://deepbluenet.com/naps-upload-code.html?site=%s&ts=%s' % (self.domain,self.mail_sent_ts)
    payload={
      'subject':'NAPS: Submit the auth code',
      'para':para,
      'url':url,
      'url_text':'Click here to open the upload page.',
    }
    self._mail(payload)

  def wait(self):
    '''
    Wait the code upload and continue
    '''
    step = 10
    time_nodes =  list(range(0,self.verify_max_time,step)) 
    i = 0
    for time_node in time_nodes:
      i+=1
      auth_code = self.__get_auth_code()
      if auth_code:
        self.auth_code = auth_code
        self._logger.info('The captcha codes: %s' % auth_code)
        break

      BluesDateTime.count_down({
        'duration':step,
        'title':'Wait the captcha codes [%s/%s] ...' % (i*step,self.verify_max_time)
      })

    if not self.auth_code:
      self._logger.error('Timeout for the captcha codes')

  def verify(self):
    # add dynamic sms auth code to atom's value
    if self.schema.verification:
      # set captcha codes
      vali_atoms:dict = self.schema.verification.get_value()
      input_atom = vali_atoms.get('input')
      input_atom.set_value(self.auth_code)

      # input and send
      model = Model(self.schema.verification)
      executor = BhvExecutor(model,self.browser)
      executor.execute()

  # === tool method ==
  def __get_auth_code(self):
    conditions = [
      {'field':'login_ts','comparator':'=','value':self.mail_sent_ts},
      {'field':'login_site','comparator':'=','value':self.domain},
    ]
    result = self.io.get('*',conditions)
    data = result.get('data')
    if data:
      return data[0]['login_sms_code']
    else:
      return None


