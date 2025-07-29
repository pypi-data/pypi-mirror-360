import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sql.TableMutator import TableMutator

class MatMutator(TableMutator):
  
  _TABLE = 'naps_material'

  def __init__(self) -> None:
    super().__init__(self._TABLE)