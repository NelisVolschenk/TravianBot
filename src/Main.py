#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
from .custom_driver import Client
from threading import Thread


class TravBot:

    def __init__(self, url: str, username: str, password: str, start_args: list, debug: bool = False, startmethod: str = 'firefox') -> None:
        self.url = url
        self.browser = Client(debug=debug)
        self.username = username
        self.password = password
        self.start_method = startmethod
        self.initialise()


    def initialise(self):
        login_req = True
        login_sleeptime = 0
        manual_login = False

        if self.start_method == 'remote':
            self.browser.remote()
            #login_req = False
        elif self.start_method == 'headless':
            self.browser.headless()
        elif self.start_method == 'manual':
            login_sleeptime = 120
            login_req = False

        if self.browser.driver is None:
            self.browser.firefox()

        if login_req is True:
            self.login()

        if manual_login is True:
            self.browser.get(self.url)
            time.sleep(login_sleeptime)


    def login(self) -> None:

        self.browser.get(self.url)
        self.browser.find("//input[@name='name']").send_keys(self.username)
        self.browser.find("//input[@name='password']").send_keys(self.password)
        self.browser.find("//button[@value='Login'][@name='s1']").click()


    def select_village(self, village_id: int) -> None:
        index = village_id
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

    def farm(self, village: int, sleeptime: int, raidlist_index: int) -> None:
        while True:
            self.select_village(village)
            time.sleep(random.randint(300,700)/100)
            self.browser.get("https://ts15.travian.com/build.php?tt=99&id=39")
            raidlist = self.browser.find("//div[@id='raidList']")
            listentries = raidlist.find_elements_by_xpath(".//div")
            list_to_raid = listentries[raidlist_index].find_element_by_xpath(".//div[contains(@class, 'listContent')]")
            classes = list_to_raid.get_attribute("class")
            if "listContent hide" in classes:
                # todo handle nonactive raidlists
                #open raid list
                listentries[raidlist_index].find_element_by_xpath(".//div[@class='openedClosedSwitch switchClosed')]").click()

            else:
                c_box = list_to_raid.find_element_by_xpath(".//div[@class='markAll']").find_element_by_xpath(".//input")
                time.sleep(random.randint(300,700)/100)
                c_box.click()
                raid_button = list_to_raid.find_element_by_xpath(".//button[@value='Start raid']")
                raid_button.click()
                # sleep after farming
                time.sleep(sleeptime + random.randint(-0.15 * sleeptime, 0.15 * sleeptime))
            time.sleep(random.randint(2,5))
    def run(self):
        self.farm(village=0,sleeptime=900,raidlist_index=0)
