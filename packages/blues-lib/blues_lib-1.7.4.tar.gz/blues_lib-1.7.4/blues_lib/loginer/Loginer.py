import sys,os,re
from abc import ABC, abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesDateTime import BluesDateTime      
from logger.LoggerFactory import LoggerFactory

class Loginer(ABC):
  def __init__(self,schema,form):
    # { LoginerSchema } 
    self.schema = schema
    # {LoginerForm}
    self.form = form
    # { Browser }
    self.browser = None
    # {bool}
    self.is_landed = False
    # {logger}
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()
    
  def login(self):
    '''
    Template method
    '''
    try:
      self.set_browser()
      self.open_page()
      self.form.perform(self.browser)
      self.verify()

      if self.is_landed:
        return self.success()
      else:
        return self.fail('not landed')

    except Exception as e:
      return self.fail(e)
      
  def fail(self,message):
    self.browser.interactor.navi.quit()
    self._logger.error('Login failure: %s' % message)
    return False

  @abstractmethod
  def set_browser(self):
    pass
  
  @abstractmethod
  def success(self):
    pass

  def open_page(self):
    login_url = self.schema.basic.get('login_url')
    self.browser.interactor.navi.open(login_url)

  def verify(self):
    '''
    Whether the login was successful
    
    @returns {bool}
    '''
    if self.schema.basic.get('login_element'):
      self.is_landed = self.is_login_element_present()
    else:
      self.is_landed = self.is_login_url_changed()

  def is_login_url_changed(self,cur_browser=None):
    '''
    Whether the page url changes after executing the loggin 
    - changed : login successful
    - unchanged : login failure

    @param {Browser} cur_browser : the active broswer, in this case the loginer as a tool
    
    @returns {bool}
    '''
    browser = cur_browser if cur_browser else self.browser
    login_url = self.schema.basic.get('login_url')
    login_max_time = self.schema.basic.get('login_max_time')
    return browser.waiter.ec.url_changes(login_url,login_max_time)

  def is_login_element_present(self,cur_browser=None):
    '''
    Whether the element in the login page present after executing the loggin 
    - not present : login successful (the page redirected after logged in)
    - present : login failure

    @param {Browser} cur_browser : the active broswer, in this case the loginer as a tool
    
    @returns {bool}
    '''
    browser = cur_browser if cur_browser else self.browser
    login_element = self.schema.basic.get('login_element')
    login_max_time = self.schema.basic.get('login_max_time')
    BluesDateTime.count_down({
      'duration':login_max_time,
      'title':'Landing...'
    })
    return not browser.element.finder.find(login_element)

  def is_landing_url_unchanged(self,login_browser=None):
    '''
    Whether the page url unchanges after open a page with cookies
    - unchanged : login successful
    - changed : login failure

    @param {Browser} cur_browser : the active broswer, in this case the loginer as a tool
    
    @returns {bool}
    '''
    browser = login_browser if login_browser else self.browser
    login_max_time = self.schema.basic.get('login_max_time')
    landing_url = self.schema.basic.get('landing_url')
    return not browser.waiter.ec.url_changes(landing_url,login_max_time)
