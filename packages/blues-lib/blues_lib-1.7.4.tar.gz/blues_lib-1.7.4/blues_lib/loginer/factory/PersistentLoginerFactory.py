import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from loginer.PersistentLoginer import PersistentLoginer   
from loginer.factory.LoginerFactory import LoginerFactory   

from loginer.form.AccountLoginerForm import AccountLoginerForm   
from loginer.form.MACLoginerForm import MACLoginerForm   
from loginer.form.QRCodeLoginerForm import QRCodeLoginerForm   

class PersistentLoginerFactory(LoginerFactory):

  def create_account(self):
    form = AccountLoginerForm(self._schema)
    return PersistentLoginer(self._schema,form)
  
  def create_mac(self):
    form = MACLoginerForm(self._schema)
    return PersistentLoginer(self._schema,form)

  def create_qrc(self):
    form = QRCodeLoginerForm(self._schema)
    return PersistentLoginer(self._schema,form)

