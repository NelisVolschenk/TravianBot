#!/usr/bin/env python3
import copy
import time
import datetime
import random
from .custom_driver import Client
from .settings import Settings, Gameconstants
from .utils import log, printable
from .buildings import costandupkeepcalc
from threading import Thread
import json
import math
import logging
mainlogger = logging.getLogger("Main Logger")



class TravBot:

    def __init__(self, debug: bool = False, startmethod: str = 'firefox') -> None:
        #TODO Change this once more villages start to be used
        self.villagelist: list = copy.deepcopy(Gameconstants.villagelist)
        self.currentvillage: int = 0
        self.fieldlist: list = self.villagelist[self.currentvillage]['fieldlist']
        self.townlist: list = self.villagelist[self.currentvillage]['townlist']
        self.buildable_fieldlist: list = self.villagelist[self.currentvillage]['buildable_fieldlist']
        self.buildable_townlist: list = self.villagelist[self.currentvillage]['buildable_townlist']
        self.buildqueue: list = self.villagelist[self.currentvillage]['buildqueue']
        self.resources: dict = self.villagelist[self.currentvillage]['resources']
        self.res_prod: dict = self.villagelist[self.currentvillage]['res_prod']
        self.layout: list = self.villagelist[self.currentvillage]['layout']
        self.hero_resources: dict = copy.deepcopy(Gameconstants.hero_resources_dict)
        self.account_timers: dict = copy.deepcopy(Gameconstants.account_timers)
        self.browser = Client(debug=debug)
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
            self.browser.get(Settings.loginurl)
            time.sleep(login_sleeptime)

    def login(self) -> None:

        # self.browser.get('file:///home/nelis/Desktop/Travian/01 fields.html')
        # self.browser.get('file:///home/nelis/Desktop/Travian/06 buildqueue.html')
        self.browser.get(Settings.loginurl)
        self.browser.find("//input[@name='name']").send_keys(Settings.username)
        self.browser.find("//input[@name='password']").send_keys(Settings.password)
        self.browser.find("//button[@value='Login']").click()
        # wait until login completes
        time.sleep(10)

    def select_village(self, village_num: int) -> None:

        # Update the pointers to point to the current village
        self.currentvillage = village_num
        self.fieldlist: list = self.villagelist[self.currentvillage]['fieldlist']
        self.townlist: list = self.villagelist[self.currentvillage]['townlist']
        self.buildable_fieldlist: list = self.villagelist[self.currentvillage]['buildable_fieldlist']
        self.buildable_townlist: list = self.villagelist[self.currentvillage]['buildable_townlist']
        self.buildqueue: list = self.villagelist[self.currentvillage]['buildqueue']
        self.resources: dict = self.villagelist[self.currentvillage]['resources']
        self.res_prod: dict = self.villagelist[self.currentvillage]['res_prod']
        self.layout: list = self.villagelist[self.currentvillage]['layout']

    def activate_village(self, village_num: int) -> None:

        # For now we can skip actually changing the village

        # index = village_id
        # # check selected village
        # ul = self.browser.find("//div[@id='sidebarBoxVillagelist']")
        # ul = ul.find_element_by_xpath(".//div[@class='content']")
        # ul = ul.find_element_by_xpath(".//ul")
        # lis = ul.find_elements_by_xpath(".//li")
        # classes = lis[index].get_attribute("class")
        # if "active" in classes:
        #     pass
        # else:
        #     link = lis[index].find_element_by_xpath(".//a")
        #     link.click()
        self.select_village(village_num)

    def updatebuildlistfiles(self):
        builddict = {'fieldlist': copy.deepcopy(self.fieldlist), 'townlist': copy.deepcopy(self.townlist)}
        with open("buildlists.json", "w") as outfile:
            json.dump(builddict, outfile, indent=4)

    def buildlist(self, village: int, sleeptime: int) -> None:
        # Load the buildlists
        with open("buildlists.json") as json_file:
            buildlists = json.load(json_file)
            self.fieldlist = copy.deepcopy(buildlists['fieldlist'])
            self.townlist = copy.deepcopy(buildlists['townlist'])
            # # Analyze the village
            # self.analyzevillage()
        while True:
            mainlogger.debug(f'Fieldlist: {self.fieldlist}')
            mainlogger.debug(f'Townlist: {self.townlist}')
            # If both buildlists are empty exit
            if self.fieldlist == [] and self.townlist == []:
                mainlogger.debug(f'Both fieldlist and townlist are empty')
                break
            # Check if buildlists both have empty first priority groups
            if self.fieldlist[0] == [] and self.townlist[0] == []:
                mainlogger.debug(f'Both fieldlist and townlists first entries are empty')
                del self.fieldlist[0]
                del self.townlist [0]
                self.updatebuildlistfiles()
            # Check the timers that need to run
            self.check_timers()
            # Check current constructions that are underway
            self.updatebuildqueue()
            # # Update the resources
            # self.updateres()
            # # Update the production
            # self.updateprod()
            # Check if there are adventures available
            self.do_adventure()
            # Check if there is enough res for an upgrade
            self.checkbuildlists()
            # Check if quests are available
            self.collect_quests()
            # Check if the hero's points need to be spent
            self.upgrade_hero('res')
            # If there are not enough resources for any construction then try with hero resources
            self.check_hero_resources_needed()
            # Check if the tribe is roman (which has two independent buildslots)
            if Settings.tribe == 'roman':
                # Check if there are items to be built and no ongoing construction in the fields
                if (self.buildable_fieldlist != []) and (self.buildqueue[0] == 0):
                    self.buildfields(self.buildable_fieldlist)
                # Update the buildlists to account for the spent resources in constructing the field
                self.checkbuildlists()
                # Check if there are items to be built and no ongoing construction in the town
                if (self.buildable_townlist != []) and (self.buildqueue[1] == 0):
                    self.buildvillage(self.buildable_townlist)
            # Or a different tribe
            else:
                # Check if there are items to be built and no ongoing construction
                if (self.buildable_fieldlist != []) and (sum(self.buildqueue) == 0):
                    self.buildfields(self.buildable_fieldlist)
                # Check if there are items to be built and no ongoing construction
                if (self.buildable_townlist != []) and (sum(self.buildqueue) == 0):
                    self.buildvillage(self.buildable_townlist)

            sleeptime = random.randint(Settings.bot_minsleeptime, Settings.bot_maxsleeptime)
            mainlogger.info(f'Sleeping for {sleeptime}')
            time.sleep(sleeptime)

    def updatebuildqueue(self, village_num: int) -> None:
        self.activate_village(village_num)
        mainlogger.info(f'Updating the buildqueue for {self.currentvillage}')
        # Go to dorf1 if not on dorf1 or dorf2
        current_url = self.browser.current_url()
        if (current_url != Settings.loginurl + 'dorf1.php') and (current_url != Settings.loginurl + 'dorf2.php'):
            mainlogger.debug(f'Going to dorf1 to find buildqueue')
            self.browser.get(Settings.loginurl + 'dorf1.php')
        # Check if buildqueue is visible
        buildqueue_xpath = '//div[@class="buildingList"]/ul'
        fields_under_construction = 0
        buildings_under_construction = 0
        fieldtimer = 0
        towntimer = 0
        try:
            buildlist = self.browser.finds(buildqueue_xpath + '/li')
            for construction_order in buildlist:
                namediv = construction_order.find_element_by_xpath('.//div[@class="name"]')
                namespan = namediv.find_element_by_xpath('./span[@class="lvl"]')
                name = namediv.text.replace(namespan.text, "").strip()
                timediv = construction_order.find_element_by_xpath('.//div[@class="buildDuration"]')
                timespan = timediv.find_element_by_xpath('./span[@class="timer"]')
                timerval = timespan.get_attribute('class')
                if name in Gameconstants.fieldnames.keys():
                    fields_under_construction += 1
                    fieldtimer = timerval
                else:
                    buildings_under_construction += 1
                    towntimer = timerval
                mainlogger.debug(f'{name} currently in buildqueue')
        except:
            mainlogger.debug(f'Nothing currently in buildqueue')
        self.buildqueue = [fields_under_construction, buildings_under_construction]
        timerlist =[fieldtimer, towntimer]
        nztimerlist = [value for value in timerlist if value!=0]
        if nztimerlist != []:
            mintime = datetime.timedelta(seconds=min(nztimerlist))
        else:
            mintime = datetime.timedelta(seconds=0)
        self.villagelist[self.currentvillage]['timers']['buildqueue'] = datetime.datetime.now() + mintime

    def updateres(self, village_num: int) -> None:
        self.activate_village(village_num)
        mainlogger.debug(f'Updating resources for {self.currentvillage}')
        # Go to dorf1 or 2 if not there
        current_url = self.browser.current_url()
        if (current_url != Settings.loginurl + 'dorf1.php') and (current_url != Settings.loginurl + 'dorf2.php'):
            self.browser.get(Settings.loginurl + 'dorf1.php')
        try:
            warehouse_xpath = '//*[@id="stockBar"]/div[@class="warehouse"]/div/div'
            granary_xpath = '//*[@id="stockBar"]/div[@class="granary"]/div/div'
            self.resources['Warehouse'] = int(printable(self.browser.find(warehouse_xpath).text.replace(',', '')))
            self.resources['Granary'] = int(printable(self.browser.find(granary_xpath).text.replace(',', '')))
            self.resources['Lumber'] = int(printable(self.browser.find('//*[@id="l1"]').text.replace(',', '')))
            self.resources['Clay'] = int(printable(self.browser.find('//*[@id="l2"]').text.replace(',', '')))
            self.resources['Iron'] = int(printable(self.browser.find('//*[@id="l3"]').text.replace(',', '')))
            self.resources['Crop'] = int(printable(self.browser.find('//*[@id="l4"]').text.replace(',', '')))
            self.resources['Free Crop'] = int(printable(self.browser.find('//*[@id="stockBarFreeCrop"]').text.replace(',', '')))
            self.resources['update_time'] = datetime.datetime.now()
            mainlogger.debug(f'Resources: {self.resources}')
        except:
            mainlogger.error(f'Unable to update resources')

    def updateprod(self, village_num: int) -> None:
        self.activate_village(village_num)
        mainlogger.debug(f'Updating production for {self.currentvillage}')
        # Make sure to be on dorf 1
        current_url = self.browser.current_url()
        if current_url != Settings.loginurl + 'dorf1.php':
            self.browser.get(Settings.loginurl + 'dorf1.php')
        try:
            prod_xpath = '//*[@id="production"]/tbody'
            lumber_xpath = prod_xpath + '/tr/td[@class="res"][text()[contains(.,"Lumber")]]/../td[@class="num"]'
            clay_xpath = prod_xpath + '/tr/td[@class="res"][text()[contains(.,"Clay")]]/../td[@class="num"]'
            iron_xpath = prod_xpath + '/tr/td[@class="res"][text()[contains(.,"Iron")]]/../td[@class="num"]'
            crop_xpath = prod_xpath + '/tr/td[@class="res"][text()[contains(.,"Crop")]]/../td[@class="num"]'
            self.res_prod['Lumber'] = int(printable(self.browser.find(lumber_xpath).text.replace(',', '')))
            self.res_prod['Clay'] = int(printable(self.browser.find(clay_xpath).text.replace(',', '')))
            self.res_prod['Iron'] = int(printable(self.browser.find(iron_xpath).text.replace(',', '')))
            self.res_prod['Crop'] = int(printable(self.browser.find(crop_xpath).text.replace(',', '')))
        except:
            mainlogger.error(f'Unable to update production')

    def calc_curr_res(self, village_num: int) -> dict:
        self.select_village(village_num)
        curr_res = {}
        for res in self.res_prod.keys():
            timediff = datetime.datetime.now() - self.resources['update_time']
            days, seconds = timediff.days, timediff.seconds
            hours = days * 24 + seconds / 3600
            curr_res[res] = self.resources[res] + int(self.res_prod[res] * hours)
            if res == 'Crop':
                curr_res[res] = min(curr_res[res], self.resources['Granary'])
            else:
                curr_res[res] = min(curr_res[res], self.resources['Warehouse'])
        curr_res['Free Crop'] = self.resources['Free Crop']
        return curr_res

    def checkbuildlists(self, village_num: int, available_res = None) -> list:
        mainlogger.info(f'Checking the buildlists for possible upgrades with available res of {available_res}')
        self.select_village(village_num)

        mainlogger.debug(f'Fieldlist: {self.fieldlist}')
        mainlogger.debug(f'Townlist: {self.townlist}')
        # If both buildlists are empty exit
        if self.fieldlist == [] and self.townlist == []:
            mainlogger.debug(f'Both fieldlist and townlist are empty')
            return [{},{}]
        # Check if buildlists both have empty first priority groups
        if self.fieldlist[0] == [] and self.townlist[0] == []:
            mainlogger.debug(f'Both fieldlist and townlists first entries are empty')
            del self.fieldlist[0]
            del self.townlist[0]
            self.updatebuildlistfiles()
            return [{},{}]

        if available_res == None:
            available_res = self.calc_curr_res(village_num)
        self.buildable_fieldlist = []
        self.buildable_townlist = []
        fieldres = {}
        townres = {}
        reslist = Gameconstants.reslist
        # Loop through fieldlist to check if upgrades are possible
        for order in self.fieldlist[0]:
            if order[0] == 'All Fields':
                # Check if any field is upgradeable
                for buildingslot in range(1,19):
                    nextlevel = self.layout[buildingslot]['level'] + 1
                    # Go to next buildingslot if this one is already at the right level
                    if nextlevel > order[1]:
                        continue
                    gid = self.layout[buildingslot]['gid']
                    cost = costandupkeepcalc(gid,nextlevel)
                    # Check if all 5 requirements are met for upgrade
                    buildable = True
                    for i in range(5):
                        check = available_res[reslist[i]] >= cost[i]
                        buildable *= check
                    if buildable:
                        # Append the item to the buildable list
                        self.buildable_fieldlist.append(order)
                        # Add the rescost of the first buildable item to the fieldres list
                        if fieldres == {}:
                            for i in range(4):
                                fieldres[reslist[i]] = cost[i]
                        break
            elif order[0] in Gameconstants.fieldnames.keys():
                # Check if a field of that type is upgradeable
                for buildingslot in range(1, 19):
                    gid = self.layout[buildingslot]['gid']
                    if gid != Gameconstants.fieldnames[order[0]]:
                        continue
                    nextlevel = self.layout[buildingslot]['level'] + 1
                    # Go to next buildingslot if this one is already at the right level
                    if nextlevel > order[1]:
                        continue
                    cost = costandupkeepcalc(gid, nextlevel)
                    buildable = True
                    for i in range(5):
                        check = available_res[reslist[i]] >= cost[i]
                        buildable *= check
                    if buildable:
                        # Append the item to the buildable list
                        self.buildable_fieldlist.append(order)
                        # Add the rescost of the first buildable item to the fieldres list
                        if fieldres == {}:
                            for i in range(4):
                                fieldres[reslist[i]] = cost[i]
                        break
            else:
                buildingslot = order[0]
                gid = self.layout[buildingslot]['gid']
                nextlevel = self.layout[buildingslot]['level'] + 1
                # Go to next buildingslot if this one is already at the right level
                if nextlevel > order[1]:
                    continue
                cost = costandupkeepcalc(gid, nextlevel)
                buildable = True
                for i in range(5):
                    check = available_res[reslist[i]] >= cost[i]
                    buildable *= check
                if buildable:
                    # Append the item to the buildable list
                    self.buildable_fieldlist.append(order)
                    # Add the rescost of the first buildable item to the fieldres list
                    if fieldres == {}:
                        for i in range(4):
                            fieldres[reslist[i]] = cost[i]

        # Loop through Townlist to check if upgrades are possible
        for order in self.townlist[0]:
            buildingslot = order[0]
            gid = order[2]
            nextlevel = self.layout[buildingslot]['level'] + 1
            # Go to next order if this one is already at the right level
            if nextlevel > order[1]:
                continue
            cost = costandupkeepcalc(gid, nextlevel)
            buildable = True
            for i in range(5):
                check = available_res[reslist[i]] >= cost[i]
                buildable *= check
            if buildable:
                # Append the item to the buildable list
                self.buildable_townlist.append(order)
                # Add the rescost of the first buildable item to the townres list
                if townres == {}:
                    for i in range(4):
                        townres[reslist[i]] = cost[i]
        return [fieldres, townres]

    def analyzevillage(self, village_num: int):
        self.select_village(village_num)
        mainlogger.info(f'Analyzing village {self.currentvillage}')
        # Analyze the fields
        mainlogger.debug(f'Analyzing the fields')
        # Go to dorf1 if not on dorf1
        current_url = self.browser.current_url()
        if current_url != Settings.loginurl + 'dorf1.php':
            mainlogger.debug(f'Not on Dorf1, going to Dorf1')
            self.browser.get(Settings.loginurl + 'dorf1.php')
        for buildingslot in range(1,19):
            buildingslot_xpath = '//*[@id="resourceFieldContainer"]' \
                             + '/a[contains(concat(" ", normalize-space(@class), " "), " buildingSlot' \
                             + str(buildingslot) \
                             + ' ")]'
            buildingslot_element = self.browser.find(buildingslot_xpath)
            class_list = buildingslot_element.get_attribute('class').split()
            # Get the slot's level
            slot_lvl = None
            for word in class_list:
                if 'level' in word and word != 'level':
                    slot_lvl = int(word.replace('level', ''))
                    break
            # Get the slot's gid
            slot_gid = None
            for word in class_list:
                if 'gid' in word:
                    slot_gid = int(word.replace('gid', ''))
                    break

            self.layout[buildingslot]['level'] = slot_lvl
            self.layout[buildingslot]['gid'] = slot_gid

        # Update the resources
        self.updateres(village_num)
        self.updateprod(village_num)

        # Analyze the town
        mainlogger.debug(f'Analyzing the town')
        self.browser.get(Settings.loginurl + 'dorf2.php')
        for buildingslot in range(19,41):
            buildingslot_xpath = '//*[@id="villageContent"]' + '/div[@data-aid="' + str(buildingslot) + '"]'
            buildingslot_element = self.browser.find(buildingslot_xpath)
            slot_gid = int(buildingslot_element.get_attribute('data-gid'))
            if slot_gid == 0:
                slot_lvl = 0
            else:
                lvl_xpath = buildingslot_xpath + '/a'
                lvl_element = self.browser.find(lvl_xpath)
                slot_lvl = int(lvl_element.get_attribute('data-level'))

            self.layout[buildingslot]['level'] = slot_lvl
            self.layout[buildingslot]['gid'] = slot_gid

        # Todo add this when buildqueue is no longer on the main loop
        # Update the buildqueue
        # self.updatebuildqueue()
        # Update the timer
        self.villagelist[self.currentvillage]['timers']['analyze'] = datetime.datetime.now()

    def buildfields(self, village_num: int, buildgroup: list = None):
        mainlogger.info(f'Building fields')
        self.activate_village(village_num)
        if self.browser.current_url() != Settings.loginurl + 'dorf1.php':
            mainlogger.debug(f'Going to fields to build')
            self.browser.get(Settings.loginurl + 'dorf1.php')

        fields_xpath = '//*[@id="resourceFieldContainer"]'
        constructing_xpath = fields_xpath + '/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
        constructing = False
        try:
            constructing = self.browser.find(constructing_xpath)
        except:
            pass
        if constructing:
            mainlogger.debug(f'Field already under construction')
            self.analyzevillage(village_num)
            return
        # No ongoing construction, can build the field
        if buildgroup == None:
            buildgroup = self.fieldlist[0]
        for order in buildgroup:
            mainlogger.debug(f'{order}')
            tolevel = order[1]

            if order[0] == 'All Fields':
                # Find the all fields
                elements_xpath = fields_xpath + '/a[contains(concat(" ", normalize-space(@class), " "), " level ")]'

            elif order[0] in Gameconstants.fieldnames.keys():
                # Find the fields with the correct gid
                gid = Gameconstants.fieldnames[order[0]]
                elements_xpath = fields_xpath + '/a[contains(concat(" ", normalize-space(@class), " "), " gid'\
                                 + str(gid) \
                                 + ' ")]'
            else:
                # Find the field
                elem_id = order[0]
                elements_xpath = fields_xpath + '/a[contains(concat(" ", normalize-space(@class), " "), " buildingSlot'\
                                 + str(elem_id)\
                                 + ' ")]'

            # Find the lowest level element in the list
            try:
                order_elements = self.browser.finds(elements_xpath)
                min_lvl = tolevel
                upg_elem = None
                for elem in order_elements:
                    lvl = elem.find_element_by_xpath('./div').text
                    if lvl == '':
                        lvl = 0
                    lvl = int(lvl)
                    if lvl < min_lvl:
                        min_lvl = lvl
                        upg_elem = elem
                if min_lvl >= tolevel:
                    # No fields left to upgrade
                    mainlogger.debug(f'The field is already at the required level, removing build order')
                    self.fieldlist[0].remove(order)
                    self.updatebuildlistfiles()
                    return
            except Exception as e:
                mainlogger.exception(f'Unable to find the elements in the order')
                return

            try:
                upg_elem_classes = upg_elem.get_attribute('class')
                # Find the id of the element
                upg_elem_class_list = upg_elem_classes.split()
                elem_id = None
                for word in upg_elem_class_list:
                    if 'buildingSlot' in word:
                        elem_id = word.replace('buildingSlot', '')
                        break
                if 'good' in upg_elem_classes:
                    mainlogger.debug(f'Building field {elem_id}')
                    upg_elem.click()
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
                                    + str(elem_id) \
                                    + ' ")' \
                                    + 'and contains(concat(" ", normalize-space(@class), " "), " underConstruction' \
                                    + ' ")' \
                                    + ']'
                    success = self.browser.find(success_xpath)
                    if success:
                        mainlogger.debug(f'Successfully built field {elem_id}')
                        self.buildqueue[0] += 1
                        # Update the resources
                        self.updateres(village_num)
                        self.updateprod(village_num)
                        self.updatebuildqueue(village_num)
                        break
            except:
                mainlogger.exception(f'Field {elem_id} not upgradeable, classes: {upg_elem_classes}')

    def buildvillage(self, village_num: int, buildgroup = None):
        mainlogger.info(f'Building town')
        self.activate_village(village_num)
        if self.browser.current_url() != Settings.loginurl + 'dorf2.php':
            mainlogger.debug(f'Going to town to build')
            self.browser.get(Settings.loginurl + 'dorf2.php')
        # self.browser.get('file:///home/nelis/Desktop/Travian/05 town.html')
        town_xpath = '//*[@id="villageContent"]'
        constructing_xpath = town_xpath + '/div/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
        constructing = False
        try:
            constructing = self.browser.find(constructing_xpath)
        except:
            pass
        if constructing:
            mainlogger.debug(f'Town already under construction')
            self.analyzevillage(village_num)
            return
        # No ongoing construction, can build the town
        if buildgroup == None:
            buildgroup = self.townlist[0]
        for order in buildgroup:
            # Go to dorf2 if not already there
            if self.browser.current_url() != Settings.loginurl + 'dorf2.php':
                self.browser.get(Settings.loginurl + 'dorf2.php')
            mainlogger.debug(f'Townlist {order}')
            buildlocation = order[0]
            tolevel = order[1]
            type_id = order[2]
            order_xpath = town_xpath + '/div[@data-aid="' + str(buildlocation) + '"]'
            try:
                order_div = self.browser.find(order_xpath)
                if int(order_div.get_attribute('data-gid')) != 0:
                    # Upgrade old building
                    # order_element = self.browser.find(order_xpath + '/a')
                    order_element = order_div.find_element_by_xpath('./a')
                    order_classes = order_element.get_attribute('class')
                    # Check the level and remove if already reached
                    lvl = order_element.get_attribute('data-level')
                    if int(lvl) >= tolevel:
                        mainlogger.debug(f'The building is already at the required level, removing build order')
                        self.townlist[0].remove(order)
                        self.updatebuildlistfiles()
                        break
                    try:
                        buildable_xpath = town_xpath + '/div[@data-aid="' + str(buildlocation) + '"]' \
                                          + '/a[contains(concat(" ", normalize-space(@class), " "), " good ")]'
                        buildable = self.browser.find(buildable_xpath)
                        if buildable:
                            mainlogger.debug(f'Upgrading building at {buildlocation}')
                            # building_xpath = buildable_xpath + '/../*[name()="svg"]/*[@class="highlightShape"]/*[name()="path"]'
                            # building = self.browser.find(building_xpath)
                            # self.browser.click_v2(building)
                            if buildlocation == 40:
                                self.browser.get(Settings.loginurl + 'build.php?id=40&gid=31')
                            else:
                                buildable.click()
                            # self.browser.get('file:///home/nelis/Desktop/Travian/02 build.html')
                            button_xpath = '//div[@id="build"]' \
                                           + '/div[@class="upgradeBuilding "]' \
                                           + '/div[contains(concat(" ", normalize-space(@class), " "), " upgradeButtonsContainer ")]' \
                                           + '/div[@class="section1"]' \
                                           + '/button[contains(concat(" ", normalize-space(@class), " "), " green ")]'
                            self.browser.find(button_xpath).click()
                            # self.browser.get('file:///home/nelis/Desktop/Travian/04 constructing.html')
                            success_xpath = town_xpath + '/div[@data-aid="' + str(buildlocation) + '"]' \
                                            + '/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
                            success = self.browser.find(success_xpath)
                            if success:
                                mainlogger.debug(f'Successfully upgraded building at {buildlocation}')
                                self.buildqueue[1] += 1
                                # Update the resources
                                self.updateres(village_num)
                                self.updateprod(village_num)
                                self.updatebuildqueue(village_num)
                                break
                    except:
                        mainlogger.exception(f'Building {buildlocation} not upgradeable, classes: {order_classes}')
                else:
                    # New building
                    mainlogger.debug(f'Constructing new building {type_id} at {buildlocation}')
                    try:
                        # Open the buildslot
                        if buildlocation == 40:
                            self.browser.get(Settings.loginurl + 'build.php?id=40')
                        else:
                            slot = order_div.find_element_by_xpath('./*[name()="svg"]/*[name()="path"]')
                            slot.click()
                            # Check which tab the building will be on
                            tab_name = Gameconstants.buildingtypes[type_id][1]
                            if tab_name in ['military', 'resources']:
                                tab_xpath = '//div[@id="build"]/div/div/div' \
                                            '/a[contains(concat(" ", normalize-space(@class), " "), " ' \
                                            + tab_name \
                                            + ' ")]'
                                self.browser.find(tab_xpath).click()
                    except:
                        mainlogger.exception(f'Building structure {type_id} at location {buildlocation} failed')
                        break
                    try:
                        div_xpath = '//div[@id="contract_building' \
                                    + str(type_id) \
                                    + '"]/div[@class="contractLink"]'
                        button_xpath =div_xpath + '/button'
                        button = self.browser.find(button_xpath)
                        if button.get_attribute('value') == "Construct building":
                            mainlogger.debug(f'Building building {type_id} at {buildlocation}')
                            button.click()
                            # Check if construction was successful
                            success_xpath = town_xpath + '/div[@data-aid="' + str(buildlocation) + '"]' \
                                            + '/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
                            success = self.browser.find(success_xpath)
                            if success:
                                mainlogger.info(f'Successfully built building {type_id} at {buildlocation}')
                                self.buildqueue[1] += 1
                                # Update the resources
                                self.updateres(village_num)
                                self.updateprod(village_num)
                                self.updatebuildqueue(village_num)
                                break
                        else:
                            mainlogger.debug(f'Not enough resources to construct {type_id}')
                    except Exception as e:
                        mainlogger.exception(f'Unable to build building {type_id}  at {buildlocation}')
            except:
                mainlogger.exception(f'Building number {buildlocation} not found')

    def check_hero_resources_needed(self, village_num: int):

        self.select_village(village_num)
        if Settings.tribe == 'roman':
            fieldcondition = self.buildable_fieldlist == [] and self.fieldlist[0] != [] and self.buildqueue[0] == 0
            towncondition = self.buildable_townlist == [] and self.townlist[0] != [] and self.buildqueue[1] == 0
        else:
            fieldcondition = self.buildable_fieldlist == [] and self.fieldlist[0] != [] and sum(self.buildqueue) == 0
            towncondition = self.buildable_townlist == [] and self.townlist[0] != [] and sum(self.buildqueue) == 0
        # Return if we do not need to use hero resources
        if not(fieldcondition or towncondition): return

        # Update the hero resource values
        total_res = {}
        curr_res = self.calc_curr_res(village_num)
        for res_type in self.hero_resources.keys():
            total_res[res_type] = max(self.hero_resources[res_type] - Settings.min_hero_resources[res_type], 0) + curr_res[res_type]
            if res_type == 'Crop':
                total_res[res_type] = min(total_res[res_type], self.resources['Granary'])
            else:
                total_res[res_type] = min(total_res[res_type], self.resources['Warehouse'])
        total_res['Free Crop'] = self.resources['Free Crop']
        buildcost_list = self.checkbuildlists(village_num, total_res)

        if (buildcost_list[0] == {}) and (buildcost_list[1] == {}):
            self.checkbuildlists(village_num)
            return

        if fieldcondition and (buildcost_list[0] != {}):
            buildcost = buildcost_list[0]
        # This elif is to make sure the field gets built first if there is enough res for either
        elif towncondition and (buildcost_list[1] != {}):
            buildcost = buildcost_list[1]
        else:
            # Not sure when this can happen, but just to be safe
            return

        res_needed = {}
        for res_type in Gameconstants.hero_resource_ids.keys():
            # Make sure only positive numbers are used
            res_shortfall = max(buildcost[res_type] - curr_res[res_type],0)
            # Round to next highest 100 resources
            res_needed[res_type] = math.ceil(res_shortfall/100) * 100
            # Ensure hero resources are more than the setting minimum
            usable_res = self.hero_resources[res_type] - Settings.min_hero_resources[res_type]
            res_needed[res_type] = min(res_needed[res_type], usable_res)
        self.use_hero_resources(res_needed)
        self.updateres(village_num)
        self.checkbuildlists(village_num)

    def check_timers(self):
        mainlogger.debug(f'Checking timers')
        # Check the account wide timers
        if self.account_timers['analyze_all'] < datetime.datetime.now():
            mainlogger.info('Analyzing all villages')
            # Save the new refresh time
            waittime = random.randint(Settings.analyze_all_minsleeptime, Settings.analyze_all_maxsleeptime)
            self.account_timers['analyze_all'] = datetime.datetime.now() + datetime.timedelta(seconds=waittime)
            self.update_hero_resources()
            for i in range(len(self.villagelist)):
                self.analyzevillage(i)

        # Check the village specific timers
        # for i in range(len(self.villagelist)):
        #     for timer, timervalue in self.villagelist[i]['timers'].items():
        #         if timervalue < datetime.datetime.now():
        #             if timer == 'buildqueue':
        #                 self.updatebuildqueue()

    def update_hero_resources(self):
        mainlogger.info(f'Updating hero resources')
        # Goto the correct page
        if self.browser.current_url() != Settings.loginurl + 'hero/inventory':
            mainlogger.debug(f'Going to hero page to update hero resources')
            self.browser.get(Settings.loginurl + 'hero/inventory')

        for res, res_id in Gameconstants.hero_resource_ids.items():
            xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " item' \
                    + str(res_id) \
                    + ' ")]/../div[@class="count"]'
            try:
                elem = self.browser.find(xpath)
                val = int(elem.text)
            except:
                mainlogger.debug(f'No more {res} available')
                val = 0
            self.hero_resources[res] = val

    def use_hero_resources(self,res_to_use):
        mainlogger.info(f'Using hero resources')
        mainlogger.debug(f'{res_to_use}')
        # Goto the correct page
        if self.browser.current_url() != Settings.loginurl + 'hero/inventory':
            mainlogger.debug(f'Going to hero inventory to use hero resources')
            self.browser.get(Settings.loginurl + 'hero/inventory')
        for res, res_id in Gameconstants.hero_resource_ids.items():
            if res_to_use[res] == 0: continue
            resource_xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " item' \
                    + str(res_id) \
                    + ' ")]/..'
            try:
                time.sleep(Settings.browser_speed/2)
                self.browser.find(resource_xpath).click()
            except:
                mainlogger.warning(f'Unable to find {res}')
                continue
            base_xpath = '//div[@id="consumableHeroItem"]'
            input_xpath = base_xpath + '/label/input'
            button_xpath = base_xpath \
                           + '/..'\
                           +'/div[@class="buttonsWrapper"]'\
                           +'/button[contains(concat(" ", normalize-space(@class), " "), " green ")]'
            try:
                time.sleep(Settings.browser_speed/2)
                self.browser.find(input_xpath).clear()
                self.browser.find(input_xpath).send_keys(res_to_use[res])
            except:
                continue
            try:
                time.sleep(Settings.browser_speed/2)
                self.browser.find(button_xpath).click()
            except:
                pass
        self.update_hero_resources()

    def collect_quests(self, experience_required = 0) -> None:
        if Settings.use_quests_for_resources is False and experience_required == 0:
            return
        mainlogger.info(f'Collecting quests')
        base_xpath = '//button[@id="questmasterButton"]'
        speech_bubble_xpath = base_xpath + '/div'
        try:
            self.browser.find(speech_bubble_xpath).click()
        except:
            mainlogger.debug(f'No quests to collect')
            return
        collectable_xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " achieved ")]'
        res_value_xpath = collectable_xpath + '//div[@class="reward resources "]/span'
        xp_value_xpath = collectable_xpath + '//div[@class="reward experience "]/span'
        button_xpath = './../../../../div/button'

        if experience_required == 0:
            try:
                collectable_list = self.browser.finds(xp_value_xpath)
            except:
                return
            for item in collectable_list:
                try:
                    button = item.find_element_by_xpath(button_xpath)
                    button.click()
                except:
                    pass
            self.update_hero_resources()
        else:
            xp_collected = 0
            try:
                collectable_list = self.browser.finds(xp_value_xpath)
            except:
                return
            for item in collectable_list:
                try:
                    xp = int(item.text())
                    item.find_element_by_xpath(button_xpath).click()
                    xp_collected += xp
                    if xp_collected >= experience_required: return
                except:
                    pass
            self.update_hero_resources()

    def upgrade_hero(self, pointallocation_type = 'res'):
        # Check if the hero has levelled up
        lvlup_xpath = '//div[@id="topBarHero"]/i[@class="levelUp show"]'
        hero_xpath = '//a[@id="heroImageButton"]'
        try:
            self.browser.find(lvlup_xpath)
        except:
            mainlogger.debug(f'No hero points available')
            return
        mainlogger.info(f'Allocating hero resources to {pointallocation_type}')
        try:
            if self.browser.current_url() != Settings.loginurl + 'hero/inventory':
                self.browser.find(hero_xpath).click()
        except:
            mainlogger.exception('Unable to open hero frame')
            return
        tab_xpath = '//div[@id="heroV2"]/div/div/div/div/a[@data-tab="2"]'
        try:
            self.browser.find(tab_xpath).click()
        except:
            mainlogger.exception('Unable to find the attributes tab')
            return
        points_available_xpath = '//div[@class="pointsAvailable"]'
        points_allocated_xpath = '//input[@name="' + Gameconstants.hero_points_dict[pointallocation_type] + '"]'
        save_points_button_xpath = '//button[@id="savePoints"]'
        try:
            points_available = self.browser.find(points_available_xpath).text
            points_available = int(points_available)
            inputelem = self.browser.find(points_allocated_xpath)
            points_allocated = inputelem.get_attribute("value")
            points_allocated = int(points_allocated)
            total_points = points_allocated + points_available
            inputelem.clear()
            inputelem.send_keys(total_points)
            self.browser.xwait_click(save_points_button_xpath)
            self.browser.find(save_points_button_xpath).click()
            # This is to wait for the button click to go through
            self.browser.find('//button[@id="savePoints"][@disabled=""]')
        except:
            mainlogger.exception('Unable to find the amount of points available')
            return

    def do_adventure(self):
        adventure_xpath = '//a[@class="layoutButton buttonFramed withIcon round adventure green    attention"]'
        adventure_num_xpath = adventure_xpath + '/div[@class="content"]'
        herolocation_xpath = '//*[@id="topBarHero"]/div/a/i[@class="heroHome"]'
        try:
            adventure_num = int(self.browser.find(adventure_num_xpath).text)
        except:
            mainlogger.debug(f'Unable to find adventure count')
            return
        try:
            self.browser.find(herolocation_xpath)
        except:
            mainlogger.debug(f'Hero not home')
            return
        if adventure_num >= 0:
            mainlogger.info(f'Sending hero on adventure')
            try:
                self.browser.find(adventure_xpath).click()
                adventure_button_xpath = '//*[@id="heroAdventure"]/table/tbody/tr/td[@class="button"]/button'
                self.browser.find(adventure_button_xpath).click()
                continue_xpath = '//button[@class="textButtonV2 buttonFramed continue rectangle withText green"]'
                self.browser.find(continue_xpath).click()
            except:
                mainlogger.error(f'Unable to click adventure button')

    def run(self):
        # Load the buildlists
        with open("buildlists.json") as json_file:
            buildlists = json.load(json_file)
            self.fieldlist = copy.deepcopy(buildlists['fieldlist'])
            self.townlist = copy.deepcopy(buildlists['townlist'])
        # Loop continually
        while True:
            # Check the timers and act accordingly
            self.check_timers()

            # Check if there are adventures available
            self.do_adventure()
            # Check if quests are available
            self.collect_quests()
            # Check if the hero's points need to be spent
            self.upgrade_hero('res')

            # Loop through the villages to check if anything can be built
            for village_num in range(len(self.villagelist)):
                # Check if there is enough res for an upgrade
                self.checkbuildlists(village_num)
                # If there are not enough resources for any construction then try with hero resources
                self.check_hero_resources_needed(village_num)
                if Settings.tribe == 'roman':
                    # Check if there are items to be built and no ongoing construction in the fields
                    if (self.buildable_fieldlist != []) and (self.buildqueue[0] == 0):
                        self.buildfields(village_num, self.buildable_fieldlist)
                    # Update the buildlists to account for the spent resources in constructing the field
                    self.checkbuildlists(village_num)
                    # Check if there are items to be built and no ongoing construction in the town
                    if (self.buildable_townlist != []) and (self.buildqueue[1] == 0):
                        self.buildvillage(village_num, self.buildable_townlist)
                # Or a different tribe
                else:
                    # Check if there are items to be built and no ongoing construction
                    if (self.buildable_fieldlist != []) and (sum(self.buildqueue) == 0):
                        self.buildfields(village_num, self.buildable_fieldlist)
                    # Check if there are items to be built and no ongoing construction
                    if (self.buildable_townlist != []) and (sum(self.buildqueue) == 0):
                        self.buildvillage(village_num, self.buildable_townlist)

            sleeptime = random.randint(Settings.bot_minsleeptime, Settings.bot_maxsleeptime)
            mainlogger.debug(f'Sleeping for {sleeptime}')
            time.sleep(sleeptime)

    # def farm(self, village: int, sleeptime: int, raidlist_index: int) -> None:
    #     while True:
    #         self.select_village(village)
    #         time.sleep(random.randint(300,700)/100)
    #         self.browser.get("https://ts15.travian.com/build.php?tt=99&id=39")
    #         raidlist = self.browser.find("//div[@id='raidList']")
    #         listentries = raidlist.find_elements_by_xpath(".//div")
    #         list_to_raid = listentries[raidlist_index].find_element_by_xpath(".//div[@class='listContent ']")
    #         classes = list_to_raid.get_attribute("class")
    #         if "hide" in classes:
    #             # todo handle nonactive raidlists
    #             pass
    #         c_box = list_to_raid.find_element_by_xpath(".//div[@class='markAll']").find_element_by_xpath(".//input")
    #         time.sleep(random.randint(300,700)/100)
    #         c_box.click()
    #         raid_button = list_to_raid.find_element_by_xpath(".//button[@value='Start raid']")
    #         raid_button.click()
    #         # sleep after farming
    #         time.sleep(sleeptime + random.randint(-0.15 * sleeptime, 0.15 * sleeptime))