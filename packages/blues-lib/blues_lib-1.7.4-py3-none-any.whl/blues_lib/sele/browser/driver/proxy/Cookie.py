import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesFiler import BluesFiler  
from type.file.File import File
from util.BluesConsole import BluesConsole   

class Cookie():

  def read_cookies(self,cookie_file=''):
    file_path = cookie_file if cookie_file else self.__get_default_file()
    BluesConsole.info('Read cookie file: %s' % file_path)
    return BluesFiler.read(file_path)

  def write_cookies(self,cookies,cookie_file=''):
    file_path = cookie_file if cookie_file else self.__get_default_file()
    BluesConsole.info('Write cookie file: %s' % file_path)
    return BluesFiler.write(file_path,cookies)

  def __get_default_file(self,extension='txt'):
    current_url = self.interactor.document.get_url()
    default_file = File.get_domain_file_path(current_url,'cookie',extension)
    return default_file 
