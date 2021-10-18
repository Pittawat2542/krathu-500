from selenium import webdriver
from selenium.webdriver.chrome.service import Service

BASE_URL = 'https://pantip.com/tag/มนุษย์เงินเดือน'
CHROME_DRIVER_PATH = './chromedriver'

service = Service(CHROME_DRIVER_PATH)
browser = webdriver.Chrome(service=service)

if __name__ == '__main__':
    browser.get(f'{BASE_URL}')

    browser.quit()