import sys,os,re

from .command.InputCMD import InputCMD
from .command.PromptCMD import PromptCMD
from .command.MaterialCMD import MaterialCMD
from .command.SchemaCMD import SchemaCMD
from .command.ModelCMD import ModelCMD
from .command.BrowserCMD import BrowserCMD
from .command.WriterCMD import WriterCMD
from .command.PersisterCMD import PersisterCMD

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.CommandFlow import CommandFlow

class AIWriterFlow(CommandFlow):
  
  def load(self):
    '''
    Template method: This method will be executed before the commands executed.
    '''
    input_cmd = InputCMD(self._context)
    schema_cmd = SchemaCMD(self._context)
    material_cmd = MaterialCMD(self._context)
    prompt_cmd = PromptCMD(self._context)
    model_cmd = ModelCMD(self._context)
    browser_cmd = BrowserCMD(self._context)
    writer_cmd = WriterCMD(self._context)
    persister_cmd = PersisterCMD(self._context)

    # check if the input is legal
    self.add(input_cmd)

    # add context.schema
    self.add(schema_cmd)
    
    # add context.material
    self.add(material_cmd)

    # add context.material.query
    self.add(prompt_cmd)

    # replace the context_schema
    self.add(model_cmd)
    
    # add the context.browser
    self.add(browser_cmd)
    
    # ask and copy the answer
    self.add(writer_cmd)

    # insert ai fields to the DB
    self.add(persister_cmd)
    