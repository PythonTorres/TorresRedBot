from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import requests
import time
import json
import sys
from Database import Database
import settings

class BankTransactions:
  def __init__(self):
      self.dataBase = Database()

  def solve_captcha(self, sitekey):
    api_key = '77d49d92df1415ec99d9185ca17fdce1'
    data_post = {'key': api_key, 'method': 'userrecaptcha', 'googlekey': sitekey, "pageurl": 'https://www.advance-rp.ru/login/', 'json': 1}
    response = requests.post(url = 'https://2captcha.com/in.php', data = data_post)
    id = eval(response.text)['request']
    print('The request is sent to 2captcha, response: ' + str(response.status_code) + ", request id: " + str(id))
    
    print('Waiting for captcha to be resolved')
    get_data = {'key': api_key, 'action': 'get', 'id': id, 'json': 1}
    time.sleep(20)
    response_recieved = False
    while response_recieved is not True:
      captcha_response = requests.get(url = f'http://2captcha.com/res.php?key={api_key}&action=get&id={id}&json=1')
      print(captcha_response.text)
      if eval(captcha_response.text)['status'] == 0:
        response_recieved = False
        time.sleep(5)
      else:
        response_recieved = True
        captcha_response_key = eval(captcha_response.text)['request']
  
    return captcha_response_key
  
  def send_keys(self, elem, keys):
    for key in keys:
      elem.send_keys(key)
  
  def getAllTransactions(self, driver):
      show = driver.find_element_by_class_name("show")
      show.click()
  
      while True:
          try:
              time.sleep(3)
              elementAtTheTop = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'statement_desc')))
              time.sleep(3)
              elementAtTheBottom = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[style="height: 74px;"]')))
              time.sleep(3)
              break
          except TimeoutException:
              pass
  
      transactionsGroup = driver.find_element_by_class_name("statement")
      transactions = transactionsGroup.find_elements_by_class_name("statement_item")
  
      allTransactions = []
      count = 1
      for elem in transactions:
          try:
              amountInner = elem.find_element_by_class_name("plus").get_attribute('innerHTML')
              amount = int(amountInner[2:])
              try:
                accountInner = elem.find_element_by_class_name("statement_desc").get_attribute('innerHTML')
                account = int(accountInner[19:])
              except ValueError:
                continue
          except NoSuchElementException:
              amountInner = elem.find_element_by_class_name("minus").get_attribute('innerHTML')
              amount = -int(amountInner[2:])
              try:
                accountInner = elem.find_element_by_class_name("statement_desc").get_attribute('innerHTML')
                account = int(accountInner[18:])
              except ValueError:
                continue
          date = elem.find_element_by_class_name("statement_date").get_attribute('innerHTML')
          transaction = {}
          transaction['id'] = count
          transaction['date'] = date
          transaction['amount'] = amount
          transaction['account'] = account
          allTransactions.append(transaction)
          count += 1
      return allTransactions
  
  def getDriverOnTransactionsPage(self):
      chromedriver = settings.bankTransactions['driverPath']

      print('Buiding a chrome driver using path: ' + chromedriver)
      chrome_options = Options()
      chrome_options.add_argument("--disable-extensions")
      chrome_options.add_argument("--disable-gpu")
      chrome_options.add_argument("--no-sandbox")
      chrome_options.add_argument("--headless")
      browser = webdriver.Chrome(executable_path=chromedriver, options=chrome_options)
  
      print('Driver is ready, getting the login page')
      browser.get('https://www.advance-rp.ru/login/')
  
      print('Page recieved, resolving the captcha')
      captcha = browser.find_element_by_id("recaptcha-login")
      sitekey = captcha.get_attribute("data-sitekey")
      captcha_response_key = self.solve_captcha(sitekey)
      captchaResponseText = browser.find_element_by_id("g-recaptcha-response")
      browser.execute_script(f"var ele=arguments[0]; ele.innerHTML = '{captcha_response_key}';", captchaResponseText)
  
      print('Captcha resolved, filling the login form fields')
      serverSelector = browser.find_element_by_class_name("select_server_button")
      serverSelector.click()
      time.sleep(3)
      redServer = browser.find_element_by_class_name("select_server_list")
      redServerOption = redServer.find_elements_by_css_selector("*")
      redServerOption[0].click()
      username = browser.find_element_by_name("nick")
      username.send_keys("Den_Torres")
      password = browser.find_element_by_name("password")
      password.send_keys("Njhnbkkf2@@9")
  
      print('Fields are filled, starting form submission')
      while True:
          password.submit()
          try:
              element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "full_info")))
              break
          except TimeoutException:
              continue
  
      print('Form successfully submitted, getting bank transactions')
      browser.get('https://www.advance-rp.ru/account/bank_statement/')
      bankacc = browser.find_element_by_name("bankacc")
      self.send_keys(bankacc, '86302')
      pin = browser.find_element_by_name("pin")
      self.send_keys(pin, '1856')
      
      print('Transactions show button is clicked, getting all transactions into list of dictionaries')
      return browser
  
  def main(self):
      errorCount = 0
      driverOnTransactionsPage = None
      while driverOnTransactionsPage is None and errorCount < 3:
          try:
              print("Starting process: login_and_fetch_all_transactions")
              self.driverOnTransactionsPage = self.getDriverOnTransactionsPage()
              print("Process finished successfully")
              return
          except:
              print("Error occured while trying to login and fetch all transactions")
              errorCount += 1
              print("Error count increased. Now: " + str(errorCount))
              print("Error details:")
              print(sys.exc_info()[0])
              if errorCount == 3:
                  raise

  def refreshTransactions(self):
    try:
        allTransactions = self.getAllTransactions(self.driverOnTransactionsPage)
        diff = len(allTransactions) - self.dataBase.getNumberOfTransactions()
        while diff > 0:
            self.dataBase.addNewTransaction(allTransactions[len(allTransactions) - diff])
            print(allTransactions[len(allTransactions) - diff])
            diff -= 1
        return
    except:
        print("Error in main cycle occured")
        print("Closing connection and cursor")
        self.dataBase.closeConnectionAndCursor()
        raise


bt = BankTransactions()
bt.main()
while True:
    bt.refreshTransactions()
    time.sleep(settings.bankTransactions['loopTime'])