from typing import Union
import re

class Model:
  def __init__(self, meta: Union[dict, list], bizdata: dict = None) -> None:
    self.meta = meta
    self.bizdata = bizdata
    self.config = self.interpolate(self.meta,self.bizdata)

  def interpolate(self, meta: Union[dict, list], bizdata: dict) -> Union[dict, list]:
    """
    递归替换meta中的占位符(${key})为bizdata中对应的值，不修改原对象
    
    Args:
      meta: 包含占位符的字典或列表
      bizdata: 用于替换占位符的数据字典
    
    Returns:
      替换后的新结构
    """
    if not bizdata:
      return meta

    if isinstance(meta, dict):
      return self._process_dict(meta, bizdata)
    elif isinstance(meta, list):
      return self._process_list(meta, bizdata)
    else:
      return meta  # 非容器类型直接返回

  def _process_dict(self, obj: dict, data: dict) -> dict:
    """递归处理字典，创建新对象"""
    result = {}
    for key, value in obj.items():
      if isinstance(value, dict):
        result[key] = self._process_dict(value, data)
      elif isinstance(value, list):
        result[key] = self._process_list(value, data)
      elif isinstance(value, str):
        result[key] = self._replace_placeholders(value, data)
      else:
        result[key] = value  # 非字符串类型保持原样
    return result

  def _process_list(self, arr: list, data: dict) -> list:
    """递归处理列表，创建新对象"""
    result = []
    for item in arr:
      if isinstance(item, dict):
        result.append(self._process_dict(item, data))
      elif isinstance(item, list):
        result.append(self._process_list(item, data))
      elif isinstance(item, str):
        result.append(self._replace_placeholders(item, data))
      else:
        result.append(item)  # 非字符串类型保持原样
    return result

  def _replace_placeholders(self, s: str, data: dict) -> str:
    """替换字符串中的占位符"""
    if not isinstance(s, str):
      return s
      
    def replace_match(match):
      expr = match.group(1)
      
      # 处理带默认值的情况: ${key:default}
      if ':' in expr:
        key, default = expr.split(':', 1)
        return str(data.get(key, default))
      
      # 处理简单占位符
      return str(data.get(expr, match.group(0)))
    
    return re.sub(r'\$\{([^}]+)\}', replace_match, s)