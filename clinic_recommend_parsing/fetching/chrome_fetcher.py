from selenium import webdriver
from time import sleep


class ChromeHtmlFetcher:
    def __init__(self):
        service = webdriver.ChromeService()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)

    def get_html(self, uri):
        self.driver.get(uri)
        sleep(2)
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        self.driver.close()
        return html
