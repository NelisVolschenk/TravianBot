#!/usr/bin/env python3

from selenium import webdriver

import time
from .custom_driver import Client
from.farm import start_farming_thread
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


    def run(self):
        start_farming_thread(browser=self.browser, farmlist_index=1, sleeptime=900)
