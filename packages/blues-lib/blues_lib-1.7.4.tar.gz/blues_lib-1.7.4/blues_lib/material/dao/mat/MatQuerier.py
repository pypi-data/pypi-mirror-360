import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.SQLSTDOut import SQLSTDOut
from sql.TableQuerier import TableQuerier

class MatQuerier(TableQuerier):

  _TABLE = 'naps_material'

  def __init__(self) -> None:
    super().__init__(self._TABLE)

  def exist(self,entity:dict)->bool:
    fields = ['material_id','material_title']
    id = entity.get('material_id')
    title = entity.get('material_title')
    conditions = [
      {
        'field':'material_id',
        'comparator':'=',
        'value':id,
      },
      {
        'operator':'or',
        'field':'material_title',
        'comparator':'like',
        'value':f'%{title}%',
      } 
    ]
    stdout:SQLSTDOut = self.get(fields,conditions)
    return stdout.count>0

  def random(self)->SQLSTDOut:
    '''
    Get a random row
    '''
    # get all fields
    fields = '*' 
    conditions = [
      {'field':'material_body_text','comparator':'!=','value':''}, 
      {'field':'material_type','comparator':'=','value':'article'}, 
    ]
    # get the latest
    orders = [{
      'field':'rand()',
      'sort':''
    }]
    # get one row
    pagination = {
      'no':1,
      'size':1
    }
    return self.get(fields,conditions,orders,pagination)

  def latest(self,count=1,material_type='')->SQLSTDOut:
    '''
    Get the latest inserted row
    '''
    # get all fields
    fields = None 
    # only get the available row
    conditions = [{
      'field':'material_status',
      'comparator':'=',
      'value':'available'
    }]
    
    if material_type:
      conditions.append({
        'field':'material_type',
        'comparator':'=',
        'value':material_type
      })
      
    # get the latest
    orders = [{
      'field':'material_collect_date',
      'sort':'desc'
    }]
    # get one row
    pagination = {
      'no':1,
      'size':count
    }
    return self.get(fields,conditions,orders,pagination)
