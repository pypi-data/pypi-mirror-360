import os,re,sys
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.file.ResReader import ResReader

class TmplReader(ResReader):
  
  ROOT = 'meta.template'
  EXT = 'conf'
  
  @classmethod
  def read(cls,addr:str):
    """
    Read metadata from a specified address.
    Args:
      addr (str): The address specifying the package and file to read metadata from.
    Returns:
      The loaded metadata.
    """
    return super().read(addr,cls.ROOT,cls.EXT)
  