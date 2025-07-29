import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.output.STDOut import STDOut
from logger.LoggerFactory import LoggerFactory

class Flow():
  
  def __init__(self):
    self._pre_commands:List[Command] = []
    self._commands:List[Command] = []
    self._post_commands:List[Command] = []
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()
  
  @property
  def pre_commands(self)->List[Command]:
    return self._pre_commands

  @property
  def commands(self)->List[Command]:
    return self._commands
  
  @property
  def post_commands(self)->List[Command]:
    return self._post_commands
    
  def add(self,command:Command):
    self._commands.append(command)

  def add_command(self,command:Command):
    self._commands.append(command)

  def add_pre_command(self,command:Command):
    self._pre_commands.append(command)  
    
  def add_post_command(self,command:Command):
    self._post_commands.append(command)
   
  def execute(self)->STDOut:
    try:
      if self._pre_commands:
        self._execute_cmds(self._pre_commands)
        message = f'[{self.__class__.__name__}] Managed to execute the flow - pre commands'
        self._logger.info(message)

      if self._commands:
        self._execute_cmds(self._commands)
      else:
        message = f'[{self.__class__.__name__}] Failed to execute the flow - no commands'
        self._logger.error(message)
        return STDOut(500,message)


      message = f'[{self.__class__.__name__}] Managed to execute the flow - core commands'
      self._logger.info(message)
      return STDOut(200,message)
    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to execute the flow - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    finally:
      self._post_execute()
        
  def _post_execute(self):
    if not self._post_commands:
      return

    try:
      self._execute_cmds(self._post_commands)
      message = f'[{self.__class__.__name__}] Managed to execute the flow - post commands'
      self._logger.info(message)
    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to execute the flow - post commands - {e}'
      self._logger.error(message)

  def _execute_cmds(self,commands:List[Command])->STDOut:
    for command in commands:
      command.execute()
