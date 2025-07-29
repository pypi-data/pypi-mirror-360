import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
# sele
from sele.interactor.Interactor import Interactor  
from sele.element.Element import Element  
from sele.waiter.Waiter import Waiter  
from sele.action.Action import Action  

# script
from sele.script.Script import Script 

# parse
from sele.parser.BluesParser import BluesParser  

class Browser():

  def __init__(self,driver):
    self.driver = driver
    self.interactor = Interactor(driver)  
    self.element = Element(driver)  
    self.waiter = Waiter(driver)  
    self.action = Action(driver)  
    self.script = Script(driver)  
    self.parser = BluesParser(driver)  

  def open(self,url):
    self.interactor.navi.open(url)
      
  def quit(self):
    self.interactor.navi.quit()

