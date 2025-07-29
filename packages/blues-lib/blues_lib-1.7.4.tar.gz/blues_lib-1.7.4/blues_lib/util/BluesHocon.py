from importlib import resources
from pyhocon import ConfigFactory
import os
import re
from functools import lru_cache

class BluesHocon:
  '''
  @description : support hocon file read from package resources
    - package: package name
    - resource_name: resource name
    - as_dict: return dict or ConfigFactory
  '''
  @staticmethod
  def parse_file(package, resource_name):
    content = resources.read_text(package, resource_name)
    base_dir = os.path.dirname(resource_name)
    processed = BluesHocon._process_includes(content, package, base_dir)
    return ConfigFactory.parse_string(processed)

  @staticmethod
  @lru_cache(maxsize=128)
  def _read_resource(package, resource_name):
    try:
      return resources.read_text(package, resource_name)
    except FileNotFoundError as e:
      raise ValueError(f"Resource not found: {package}.{resource_name}") from e
    except Exception as e:
      raise ValueError(f"Failed to read resource: {package}.{resource_name}") from e

  @staticmethod
  def _process_includes(content, package, base_dir):
    content = BluesHocon._clean_content(content)
    
    while True:
      match = BluesHocon._find_next_include(content)
      if not match:
        return content

      include_path = match.group(2)  # 修正：使用第二个捕获组（路径）
      include_type = BluesHocon._determine_include_type(include_path)
      
      if include_type != "file":
        raise ValueError(f"Unsupported include type: {include_type}")
      
      resolved_path = BluesHocon._resolve_include_path(include_path, base_dir)
      include_package, include_resource = BluesHocon._get_resource_info(resolved_path, package)
      
      try:
        included_content = BluesHocon._read_resource(include_package, include_resource)
        processed_include = BluesHocon._process_includes(
          included_content, include_package, os.path.dirname(include_resource)
        )
        
        # 确保处理后的内容不为 None
        if processed_include is None:
          processed_include = ""
          
        processed_include = BluesHocon._format_included_content(processed_include)
        content = BluesHocon._replace_include(content, match, processed_include)
      except Exception as e:
        raise ValueError(f"Failed to include {include_path} from {package}.{os.path.basename(base_dir)}: {str(e)}") from e

  @staticmethod
  def _clean_content(content):
    content = re.sub(r'#.*$', '', content, flags=re.M)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    return content.strip()

  @staticmethod
  def _find_next_include(content):
    # 修正：正则表达式捕获组
    pattern = re.compile(r'include\s+(required|override)?\s*"?([^"\n]+)"?')
    return pattern.search(content)

  @staticmethod
  def _determine_include_type(include_path):
    if include_path.startswith(('http://', 'https://')):
      return "url"
    elif include_path.startswith(('classpath:', 'resource:')):
      return "resource"
    else:
      return "file"

  @staticmethod
  def _resolve_include_path(include_path, base_dir):
    if base_dir and not os.path.isabs(include_path):
      return os.path.normpath(os.path.join(base_dir, include_path))
    return include_path

  @staticmethod
  def _get_resource_info(resolved_path, package):
    parts = resolved_path.split(os.sep)
    include_package = ".".join([package] + parts[:-1])
    include_resource = parts[-1]
    return include_package, include_resource

  @staticmethod
  def _format_included_content(content):
    """格式化包含的内容，确保不为 None 并正确处理边界"""
    if content is None:
      return ""
      
    content = content.strip()
    
    # 处理空内容
    if not content:
      return ""
      
    # 处理完整对象
    if content.startswith('{') and content.endswith('}'):
      content = content[1:-1].strip()
    
    # 添加换行符确保内容分隔
    return f"\n{content}\n"

  @staticmethod
  def _replace_include(content, match, include_content):
    return content[:match.start()] + include_content + content[match.end():]