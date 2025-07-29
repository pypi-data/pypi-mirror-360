import sys,os,re
from .command.InputCMD import InputCMD
from .command.SpiderCMD import SpiderCMD
from .command.WriterCMD import WriterCMD
from .command.PublisherCMD import PublisherCMD
from .command.ReporterCMD import ReporterCMD
from .command.CleanerCMD import CleanerCMD

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.CommandFlow import CommandFlow

# spide and ai an publish flow
class SAPFlow(CommandFlow):

  def load(self):
    input_cmd = InputCMD(self._context)
    spider_cmd = SpiderCMD(self._context)
    writer_cmd = WriterCMD(self._context)
    publisher_cmd = PublisherCMD(self._context)
    reporter_cmd = ReporterCMD(self._context)
    cleaner_cmd = CleanerCMD(self._context)

    # check if the input is legal
    self.add(input_cmd)

    # spide athe materials
    self.add(spider_cmd)

    # revise the material
    self.add(writer_cmd)

    # publish the material
    self.add(publisher_cmd)

    # send a rerpot
    self.add(reporter_cmd)

    # clean the file and db
    self.add(cleaner_cmd)