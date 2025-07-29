class AIPrompt:
  
  def __init__(self,stereotype,article):
    self._stereotype = stereotype
    self._article = article
    
  def get(self):
    rule = self.get_rule()
    limit = self.get_limit()
    article = self.get_article()
    return "%s %s %s" % (rule,limit,article)
  
  def get_article(self):
    return "原文如下："+self._article
  
  def get_rule(self):
    texts = self._stereotype.get('rule')
    return self._get_text(texts)
    
  def get_limit(self):
    texts = self._stereotype.get('limit')
    return self._get_text(texts)
    
  def _get_text(self,texts):
    total = ""
    if not texts:
      return total

    for text in texts:
      total+=text
    return total
    