import sys,os,re,time
from .driver.proxy.Cookie import Cookie 
from .BluesStandardChrome import BluesStandardChrome   

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from loginer.factory.PersistentLoginerFactory import PersistentLoginerFactory    
from util.BluesConsole import BluesConsole   

class BluesLoginChrome(BluesStandardChrome,Cookie):
  '''
  This class is used exclusively to open pages that can only be accessed after login
  There are three ways to complete automatic login:
    1. Login by a cookie string
    2. Login by a cookie file path
    3. Login by the BluesLoginer class
  '''
  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} driver.exe path: 'env' - using the env; 'config' - the local path; 'manager' | None - using the driver manager
      loginer_schema = None, # {Schema} : the atomed loginer schema
    ):
    '''
    Parameter:
      url {str} : the url will be opened
      loginer_or_cookie {Loginer|str} : 
        - when as str: it is the cookie string or local cookie file, don't support relogin
        - when as Loginer : it supports to relogin
      anchor {str} : the login page's element css selector
        some site will don't redirect, need this CS to ensure is login succesfully
    '''
    super().__init__(
      std_args,
      exp_args,
      cdp_args,
      sel_args,
      ext_args,
      executable_path
    )
    
    # {Loginer} : three kinds of mode, use schema
    self.loginer_schema = loginer_schema
    self.loginer = self._get_loginer()


    # {int} : relogin time
    self.relogin_time = 0
    # login
    self._login()
    
  def _get_loginer(self):
    mode = self.loginer_schema.basic.get('mode')
    return PersistentLoginerFactory(self.loginer_schema).create(mode)
    
  def _login(self):
    # read cookie need get the domain from the url
    login_url = self.loginer_schema.basic.get('login_url')
    self.open(login_url)

    # read the cookie
    cookies = self.read_cookies()
    if cookies and self._login_with_cookies(cookies):
      BluesConsole.success('Success to login by the cookie')
    else: 
      BluesConsole.info('Fail to login by the cookie, relogin...')
      self._relogin()

  def _login_with_cookies(self,cookies):
    # add cookie to the browser
    self.interactor.cookie.set(cookies) 
    # Must open the logged in page ,Otherwise, you cannot tell if you have logged in
    landing_url = self.loginer_schema.basic.get('landing_url')
    self.open(landing_url) 
    
    # Check if login successfully
    return self.loginer.is_landing_url_unchanged(self) 

  def _relogin(self):
    login_max_retries = self.loginer_schema.basic.get('login_max_retries',1)
    if self.relogin_time>=login_max_retries:
      return

    self.relogin_time+=1
    # Relogin and save the new cookies to the local file
    BluesConsole.info('Relogining [%s/%s] ...' % (self.relogin_time,login_max_retries))
    self.loginer.login()

    # Reopen the page using the new cookies
    self._login()

