import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from material.dao.mat.MatQuerier import MatQuerier
from util.BluesConsole import BluesConsole

class PublishPlan():

  querier = MatQuerier()

  def __init__(self,platform,excepted_quota,daily_limit_quota):
    # {str} the publish platform
    self.platform = platform
    # {dict} channel's count dict {'events':1,'article':1}
    self.excepted_quota = excepted_quota
    # {dict} daily channels' limit quota
    self.daily_limit_quota = daily_limit_quota
    # {dict}
    self.pub_quota = None
    # {dict}
    self.avail_quota = None
    # {dict}
    self.current_quota = None
    # {int}
    self.current_total = 0

    self.__set()
    self.__console()

  def __set(self):
    pub_quota = {}
    avail_quota = {}
    current_quota = {}
    current_total = 0
    for channel,excepted_count in self.excepted_quota.items():

      limit_count = self.daily_limit_quota.get(channel,0)
      pub_count = self.querier.get_today_pubed_count(self.platform,channel)['count']
      avail_count = limit_count - pub_count if limit_count > pub_count else 0
      current_count = excepted_count if avail_count > excepted_count else avail_count

      pub_quota[channel] = pub_count
      avail_quota[channel] = avail_count
      current_quota[channel] = current_count

      current_total += current_count

    self.pub_quota = pub_quota
    self.avail_quota = avail_quota
    self.current_quota = current_quota
    self.current_total = current_total

  def __console(self):
    BluesConsole.info('limit_quota: %s' % self.daily_limit_quota)
    BluesConsole.info('excepted_quota: %s' % self.excepted_quota)
    BluesConsole.info('pub_quota: %s' % self.pub_quota)
    BluesConsole.info('current_quota: %s' % self.current_quota)
    BluesConsole.info('current_total: %s' % self.current_total)

