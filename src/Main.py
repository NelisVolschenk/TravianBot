#!/usr/bin/env python3
import copy
import time
import random
from .custom_driver import Client
from .settings import Settings
from .utils import log
from threading import Thread
import json



class TravBot:

    def __init__(self, url: str, username: str, password: str, start_args: list, debug: bool = False, startmethod: str = 'firefox') -> None:
        self.fieldlist: list = []
        self.townlist: list = []
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
            pass

        if manual_login is True:
            self.browser.get(self.url)
            time.sleep(login_sleeptime)


    def login(self) -> None:

        # self.browser.get('file:///home/nelis/Desktop/Travian/01 fields.html')
        self.browser.get(Settings.loginurl)
        self.browser.find("//input[@name='name']").send_keys(Settings.username)
        self.browser.find("//input[@name='password']").send_keys(Settings.password)
        self.browser.find("//button[@value='Login']").click()
        # wait until login completes
        time.sleep(10)


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

    def updatebuildlistfiles(self):
        builddict = {'fieldlist': copy.deepcopy(self.fieldlist), 'townlist': copy.deepcopy(self.townlist)}
        with open("buildlists.json", "w") as outfile:
            json.dump(builddict, outfile, indent=4)

    def buildlist(self, village: int, sleeptime: int) -> None:
        # Load the buildlists
        # self.fieldlist = [
        #     [
        #         (1, 3),
        #         (2, 3),
        #         (3, 3),
        #         (4, 3),
        #         (5, 3),
        #         (6, 3),
        #         (7, 3),
        #         (8, 3),
        #         (9, 3),
        #         (10, 3),
        #         (11, 3),
        #         (12, 3),
        #         (13, 3),
        #         (14, 3),
        #         (15, 3),
        #         (16, 3),
        #         (17, 3),
        #         (18, 3),
        #     ],
        #     [
        #         (8, 4),
        #         (9, 4)
        #     ]
        # ]
        # self.townlist = [[],[]]
        # self.updatebuildlistfiles()
        with open("buildlists.json") as json_file:
            buildlists = json.load(json_file)
            self.fieldlist = copy.deepcopy(buildlists['fieldlist'])
            self.townlist = copy.deepcopy(buildlists['townlist'])
        while True:
            log(f'Fieldlist')
            log(f'{self.fieldlist}')
            log(f'Townlist')
            log(f'{self.townlist}')
            # If both buildlists are empty exit
            if self.fieldlist == [] and self.townlist == []:
                log(f'Both fieldlist and townlist are empty')
                break
            # Check if buildlists both have empty first priority groups
            if self.fieldlist[0] == [] and self.townlist[0] == []:
                del self.fieldlist[0]
                del self.townlist [0]
                self.updatebuildlistfiles()
            # Build fields if first buildgroup is not empty
            elif self.fieldlist[0] != []:
                self.browser.get(Settings.loginurl + 'dorf1.php')
                # self.browser.get('file:///home/nelis/Desktop/Travian/01 fields.html')
                fields_xpath = '//*[@id="resourceFieldContainer"]'
                constructing_xpath = fields_xpath + '/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
                constructing = False
                try:
                    constructing = self.browser.find(constructing_xpath)
                except:
                    pass
                if constructing:
                    log(f'Field already under construction')
                else:
                    buildgroup = self.fieldlist[0]
                    for order in buildgroup:
                        log(f'{order}')
                        id = order[0]
                        tolevel = order[1]
                        order_xpath = fields_xpath + '/a[contains(concat(" ", normalize-space(@class), " "), " buildingSlot' + str(id) + ' ")]'
                        try:
                            order_element = self.browser.find(order_xpath)
                            order_classes = order_element.get_attribute('class')
                            # Check the level and remove if already reached
                            lvl_xpath = order_xpath + '/div'
                            lvl = self.browser.find(lvl_xpath).text
                            if int(lvl) >= tolevel:
                                log(f'The field is already at the required level, removing build order')
                                self.fieldlist[0].remove(order)
                                self.updatebuildlistfiles()
                                break
                            try:
                                buildable_xpath = fields_xpath \
                                                  + '/a[contains(concat(" ", normalize-space(@class), " "), " buildingSlot' \
                                                  + str(id) \
                                                  + ' ")' \
                                                  +'and contains(concat(" ", normalize-space(@class), " "), " good' \
                                                  + ' ")' \
                                                  + ']'
                                buildable = self.browser.find(buildable_xpath)
                                if buildable:
                                    log(f'Building field {id}')
                                    buildable.click()
                                    # self.browser.get('file:///home/nelis/Desktop/Travian/02 build.html')
                                    button_xpath = '//div[@id="build"]' \
                                                   + '/div[@class="upgradeBuilding "]' \
                                                   + '/div[contains(concat(" ", normalize-space(@class), " "), " upgradeButtonsContainer ")]' \
                                                   + '/div[@class="section1"]' \
                                                   + '/button[contains(concat(" ", normalize-space(@class), " "), " green ")]'
                                    self.browser.find(button_xpath).click()
                                    # self.browser.get('file:///home/nelis/Desktop/Travian/04 constructing.html')
                                    success_xpath = fields_xpath \
                                                  + '/a[contains(concat(" ", normalize-space(@class), " "), " buildingSlot' \
                                                  + str(id) \
                                                  + ' ")' \
                                                  +'and contains(concat(" ", normalize-space(@class), " "), " underConstruction' \
                                                  + ' ")' \
                                                  + ']'
                                    success = self.browser.find(success_xpath)
                                    if success:
                                        log(f'Successfully built field {id}')
                                        break
                            except:
                                log(f'Field {id} not upgradeable, classes: {order_classes}')
                        except:
                            log(f'Field number {id} not found')

            # Build Town if first buildgroup is not empty
            elif self.townlist[0] != []:
                self.browser.get(Settings.loginurl + 'dorf2.php')
                # self.browser.get('file:///home/nelis/Desktop/Travian/01 fields.html')
                town_xpath = '//*[@id="villageContent"]'
                constructing_xpath = town_xpath + '/div/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
                constructing = False
                try:
                    constructing = self.browser.find(constructing_xpath)
                except:
                    pass
                if constructing:
                    log(f'Town already under construction')
                else:
                    buildgroup = self.townlist[0]
                    for order in buildgroup:
                        log(f'Townlist {order}')
                        id = order[0]
                        tolevel = order[1]
                        order_xpath = town_xpath + '/div[@data-aid="' + id + '"]/a'
                        try:
                            order_element = self.browser.find(order_xpath)
                            order_classes = order_element.get_attribute('class')
                            # Check the level and remove if already reached
                            lvl = self.browser.find(order_xpath).getattribute('data-level')
                            if int(lvl) >= tolevel:
                                log(f'The building is already at the required level, removing build order')
                                self.townlist[0].remove(order)
                                self.updatebuildlistfiles()
                                break
                            try:
                                buildable_xpath = town_xpath + '/div[@data-aid="' + id + '"]'\
                                                  +'/a[contains(concat(" ", normalize-space(@class), " "), " good ")]'
                                buildable = self.browser.find(buildable_xpath)
                                if buildable:
                                    log(f'Building field {id}')
                                    buildable.click()
                                    # self.browser.get('file:///home/nelis/Desktop/Travian/02 build.html')
                                    button_xpath = '//div[@id="build"]' \
                                                   + '/div[@class="upgradeBuilding "]' \
                                                   + '/div[contains(concat(" ", normalize-space(@class), " "), " upgradeButtonsContainer ")]' \
                                                   + '/div[@class="section1"]' \
                                                   + '/button[contains(concat(" ", normalize-space(@class), " "), " green ")]'
                                    self.browser.find(button_xpath).click()
                                    # self.browser.get('file:///home/nelis/Desktop/Travian/04 constructing.html')
                                    success_xpath = town_xpath + '/div[@data-aid="' + id + '"]'\
                                                  +'/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
                                    success = self.browser.find(success_xpath)
                                    if success:
                                        log(f'Successfully built field {id}')
                                        break
                            except:
                                log(f'Field {id} not upgradeable, classes: {order_classes}')
                        except:
                            log(f'Field number {id} not found')


            # Sleep for the required amount of time
            time.sleep(random.randint(Settings.build_minsleeptime, Settings.build_maxsleeptime))



    def farm(self, village: int, sleeptime: int, raidlist_index: int) -> None:
        while True:
            self.select_village(village)
            time.sleep(random.randint(300,700)/100)
            self.browser.get("https://ts15.travian.com/build.php?tt=99&id=39")
            raidlist = self.browser.find("//div[@id='raidList']")
            listentries = raidlist.find_elements_by_xpath(".//div")
            list_to_raid = listentries[raidlist_index].find_element_by_xpath(".//div[@class='listContent ']")
            classes = list_to_raid.get_attribute("class")
            if "hide" in classes:
                # todo handle nonactive raidlists
                pass
            c_box = list_to_raid.find_element_by_xpath(".//div[@class='markAll']").find_element_by_xpath(".//input")
            time.sleep(random.randint(300,700)/100)
            c_box.click()
            raid_button = list_to_raid.find_element_by_xpath(".//button[@value='Start raid']")
            raid_button.click()
            # sleep after farming
            time.sleep(sleeptime + random.randint(-0.15 * sleeptime, 0.15 * sleeptime))

    def run(self):
        self.buildlist(village=0,sleeptime=900)
