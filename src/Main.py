#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
from .utils import log
from .custom_driver import Client
from threading import Thread


class TravBot:

    def __init__(self, url: str, username: str, password: str, start_args: list, debug: bool = False,
                 startmethod: str = "") -> None:
        self.url = url
        self.browser = Client(debug=debug)
        self.username = username
        self.password = password
        self.driver = None
        self.initialise()
        self.startmethod = startmethod

    def initialise(self):

        if self.startmethod == 'remote':
            self.browser.remote()
        elif self.startmethod == 'headless':
            self.browser.headless()

        if self.browser.driver is None:
            self.driver = webdriver.Firefox()

    def login(self) -> None:

        self.browser.get(self.url)
        self.browser.find("//input[@name='name']").send_keys(self.username)
        self.browser.find("//input[@name='password']").send_keys(self.password)
        self.browser.find("//button[@value='Login'][@name='s1']").click()
        '''
        self.driver.find_element(By.NAME, "name").click()
        self.driver.find_element(By.NAME, "name").send_keys("fieryfrost")
        self.driver.find_element(By.NAME, "password").send_keys("342256")
        self.driver.find_element(By.ID, "s1").click()
        '''

    def select_village(self, id: int) -> None:
        index = id

        # check selected village
        ul = self.browser.find("//div[@id='sidebarBoxVillagelist']")
        ul = ul.find_element_by_xpath(".//div[@class='content']")
        ul = ul.find_element_by_xpath(".//ul")
        lis = ul.find_elements_by_xpath(".//li")
        classes = lis[index].get_attribute("class")
        if "active" in classes:
            pass
        else:
            link = lis[index].find_element_by_xpath(".//a")
            link.click()

    def farm(self, sleeptime) -> None:
        while True:
            # sleep after farming
            time.sleep(sleeptime + random.randint(-0.15 * sleeptime, 0.15 * sleeptime))

    def run(self):
        self.login()
        time.sleep(10)
        self.select_village(2)


if __name__ == "__main__":
    bot = TravBot(url='https://ts15.travian.com', username='Fieryfrost', password='342256', start_args=[], debug=False)
    bot.run()
