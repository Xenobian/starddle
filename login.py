from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import pyotp

class Login:

    def __init__(self) -> None:
        self.API_KEY    = 'cjqx8u4zedif6m4i'
        self.API_SECRET = 'y2q7xt151teakfs1qebnforcmouutekw'
        self.USER_ID    = 'CS7249'
        self.PWD        = 'QGe_@7A9'
        self.twoFAKey   = '733SF4CUBDJIS7HKRA4LJWGM4HNIH5KB'

        self.request_token = None

    def generate_request_token(self):
        
        driver = uc.Chrome()
        driver.get(f'https://kite.trade/connect/login?api_key={self.API_KEY}&v=3')
        login_id = WebDriverWait(driver, 10).until(
            lambda x: x.find_element(by=By.XPATH, value='//*[@id="userid"]'))
        login_id.send_keys(self.USER_ID)

        pwd = WebDriverWait(driver, 10).until(
            lambda x: x.find_element(by=By.XPATH, value='//*[@id="password"]'))
        pwd.send_keys(self.PWD)

        submit = WebDriverWait(driver, 10).until(lambda x: x.find_element(
            by=By.XPATH,
            value='//*[@id="container"]/div/div/div[2]/form/div[4]/button'))
        submit.click()
        time.sleep(1)

        totp = WebDriverWait(driver, 10).until(lambda x: x.find_element(
            by=By.XPATH,
            value = '/html/body/div[1]/div/div/div[1]/div[2]/div/div/form/div[1]/input'))
        authkey = pyotp.TOTP(self.twoFAKey)
        totp.send_keys(authkey.now())

    
        time.sleep(2)
        
        url = driver.current_url
        initial_token = url.split('request_token=')[1]
        request_token = initial_token.split('&')[0]

        driver.close()

        self.request_token = request_token
        
    def generate_kite_object(self):

        kite = KiteConnect(api_key=self.API_KEY)
       
        data = kite.generate_session(self.request_token, self.API_SECRET)
       
        self.access_token = data['access_token']
    
        kite.set_access_token(self.access_token)
        
        return kite

    def generate_ticker(self):
        
        kws = KiteTicker(self.API_KEY,self.access_token)

        return kws

if __name__ == '__main__':

   pass
