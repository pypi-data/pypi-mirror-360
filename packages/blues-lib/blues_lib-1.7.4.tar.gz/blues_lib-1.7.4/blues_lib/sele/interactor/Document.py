class Document():
 
  def __init__(self,driver):
    self.__driver = driver

  def get_title(self):
    # Return the document's title
    return self.__driver.title
  
  def get_name(self):
    # Return the document's name
    return self.__driver.name
  
  def get_url(self):
    # Return the document's url
    return self.__driver.current_url
  
  def get_source(self):
    # Return the document's page source
    return self.__driver.page_source
  
