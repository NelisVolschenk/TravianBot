#!/usr/bin/env python3
import copy
import time
import datetime
import random
from .custom_driver import Client
from .settings import Settings, Gameconstants
from .utils import log, printable
from .utils import create_rotating_log
from .buildings import costandupkeepcalc
from threading import Thread
import json
import math



class TravBot:

    def __init__(self, debug: bool = False, startmethod: str = 'firefox') -> None:
        self.fieldlist: list = []
        self.townlist: list = []
        self.buildable_fieldlist: list = []
        self.buildable_townlist: list = []
        self.buildqueue: list = []
        self.resources: dict = copy.deepcopy(Gameconstants.resources_dict)
        self.hero_resources: dict = copy.deepcopy(Gameconstants.hero_resources_dict)
        self.layout: list = copy.deepcopy(Gameconstants.layout_list)
        self.timers: dict = {'refresh': datetime.datetime.now()}
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
        with open("buildlists.json") as json_file:
            buildlists = json.load(json_file)
            self.fieldlist = copy.deepcopy(buildlists['fieldlist'])
            self.townlist = copy.deepcopy(buildlists['townlist'])
            # Analyze the village
            self.analyzevillage()
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
            # Check the timers that need to run
            self.check_timers()
            # Check current constructions that are underway
            self.updatebuildqueue()
            # Update the resources
            self.updateres()
            # Check if there is enough res for an upgrade
            self.checkbuildlists()
            # If there are not enough resources for any construction then try with hero resources
            self.check_hero_resources_needed()
            # Check if the tribe is roman (which has two independent buildslots)
            if Settings.tribe == 'roman':
                # Check if there are items to be built and no ongoing construction in the fields
                if (self.buildable_fieldlist != []) and (self.buildqueue[0] == 0):
                    self.buildfields(self.buildable_fieldlist)
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

            sleeptime = random.randint(Settings.build_minsleeptime, Settings.build_maxsleeptime)
            log(f'Sleeping for {sleeptime}')
            time.sleep(sleeptime)

    def updatebuildqueue(self):
        # Check if buildqueue is visible
        buildqueue_xpath = '//div[@class="buildingList"]/ul'
        buildqueue_exists = False
        fields_under_construction = 0
        buildings_under_construction = 0
        try:
            buildqueue_exists = self.browser.find(buildqueue_xpath)
        except:
            pass
        if not buildqueue_exists:
            # Go to dorf1 if not on dorf1 or dorf2
            current_url = self.browser.current_url()
            if (current_url != Settings.loginurl + 'dorf1.php') and (current_url != Settings.loginurl + 'dorf2.php'):
                log(f'Going to dorf1 to find buildqueue')
                self.browser.get(Settings.loginurl + 'dorf1.php')
        try:
            buildlist = self.browser.finds(buildqueue_xpath + '/li')
            for construction_order in buildlist:
                namediv = construction_order.find_element_by_xpath('.//div[@class="name"]')
                namespan = namediv.find_element_by_xpath('./span[@class="lvl"]')
                name = namediv.text.replace(namespan.text, "").strip()
                if name in Gameconstants.fieldnames.keys():
                    fields_under_construction += 1
                else:
                    buildings_under_construction += 1
                log(f'{name} currently in buildqueue')
        except Exception as e:
            log(f'Nothing currently in buildqueue')
        self.buildqueue = [fields_under_construction, buildings_under_construction]

    def updateres(self):

        current_url = self.browser.current_url()
        if (current_url != Settings.loginurl + 'dorf1.php') and (current_url != Settings.loginurl + 'dorf2.php'):
            log(f'Going to dorf1 to update resources')
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
            log(self.resources)
        except:
            log('Unable to update resources')

    def checkbuildlists(self, available_res = None):
        if available_res == None:
            available_res = self.resources
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
                    gid = self.layout[buildingslot]['gid']
                    cost = costandupkeepcalc(gid,nextlevel)
                    buildable = True
                    for i in range(5):
                        check = available_res[reslist[i]] >= cost[i]
                        buildable *= check
                    if buildable:
                        self.buildable_fieldlist.append(order)
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
                    cost = costandupkeepcalc(gid, nextlevel)
                    buildable = True
                    for i in range(5):
                        check = available_res[reslist[i]] >= cost[i]
                        buildable *= check
                    if buildable:
                        self.buildable_fieldlist.append(order)
                        if fieldres == {}:
                            for i in range(4):
                                fieldres[reslist[i]] = cost[i]
                        break
            else:
                buildingslot = order[0]
                gid = self.layout[buildingslot]['gid']
                nextlevel = self.layout[buildingslot]['level'] + 1
                cost = costandupkeepcalc(gid, nextlevel)
                buildable = True
                for i in range(5):
                    check = available_res[reslist[i]] >= cost[i]
                    buildable *= check
                if buildable:
                    self.buildable_fieldlist.append(order)
                    if fieldres == {}:
                        for i in range(4):
                            fieldres[reslist[i]] = cost[i]

        # Loop through Townlist to check if upgrades are possible
        for order in self.townlist[0]:
            buildingslot = order[0]
            gid = order[2]
            nextlevel = self.layout[buildingslot]['level'] + 1
            cost = costandupkeepcalc(gid, nextlevel)
            buildable = True
            for i in range(5):
                check = available_res[reslist[i]] >= cost[i]
                buildable *= check
            if buildable:
                self.buildable_townlist.append(order)
                if townres == {}:
                    for i in range(4):
                        townres[reslist[i]] = cost[i]
        return [fieldres, townres]

    def analyzevillage(self):
        # Analyze the fields
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

        # Analyze the town
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

    def buildfields(self, buildgroup = None):

        if self.browser.current_url() != Settings.loginurl + 'dorf1.php':
            self.browser.get(Settings.loginurl + 'dorf1.php')

        fields_xpath = '//*[@id="resourceFieldContainer"]'
        constructing_xpath = fields_xpath + '/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
        constructing = False
        try:
            constructing = self.browser.find(constructing_xpath)
        except:
            pass
        if constructing:
            log(f'Field already under construction')
            return
        # No ongoing construction, can build the field
        if buildgroup == None:
            buildgroup = self.fieldlist[0]
        for order in buildgroup:
            log(f'{order}')
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
                    log(f'The field is already at the required level, removing build order')
                    self.fieldlist[0].remove(order)
                    self.updatebuildlistfiles()
                    return
            except Exception as e:
                log(f'Unable to find the elements in the order')
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
                    log(f'Building field {elem_id}')
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
                        log(f'Successfully built field {elem_id}')
                        self.buildqueue[0] += 1
                        break
            except Exception as e:
                log(f'Field {elem_id} not upgradeable, classes: {upg_elem_classes}')

    def buildvillage(self, buildgroup = None):
        if self.browser.current_url() != Settings.loginurl + 'dorf2.php':
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
            log(f'Town already under construction')
        else:
            if buildgroup == None:
                buildgroup = self.townlist[0]
            for order in buildgroup:
                # Go to dorf2 if not already there
                if self.browser.current_url() != Settings.loginurl + 'dorf2.php':
                    self.browser.get(Settings.loginurl + 'dorf2.php')
                log(f'Townlist {order}')
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
                            log(f'The building is already at the required level, removing build order')
                            self.townlist[0].remove(order)
                            self.updatebuildlistfiles()
                            break
                        try:
                            buildable_xpath = town_xpath + '/div[@data-aid="' + str(buildlocation) + '"]' \
                                              + '/a[contains(concat(" ", normalize-space(@class), " "), " good ")]'
                            buildable = self.browser.find(buildable_xpath)
                            if buildable:
                                log(f'Upgrading building at {buildlocation}')
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
                                    log(f'Successfully upgraded building at {buildlocation}')
                                    self.buildqueue[1] += 1
                                    break
                        except Exception as e:
                            log(f'Building {buildlocation} not upgradeable, classes: {order_classes}')
                    else:
                        # New building
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
                            div_xpath = '//div[@id="contract_building' \
                                        + str(type_id) \
                                        + '"]/div[@class="contractLink"]'
                            button_xpath =div_xpath + '/button'
                        except Exception as e:
                            log(f'Building structure {type_id} at location {buildlocation} failed')
                            break
                        try:
                            button = self.browser.find(button_xpath)
                            if button.get_attribute('value') == "Construct building":
                                log(f'Building building {type_id} at {buildlocation}')
                                button.click()
                                # Check if construction was successful
                                success_xpath = town_xpath + '/div[@data-aid="' + str(buildlocation) + '"]' \
                                                + '/a[contains(concat(" ", normalize-space(@class), " "), " underConstruction ")]'
                                success = self.browser.find(success_xpath)
                                if success:
                                    log(f'Successfully built building {type_id} at {buildlocation}')
                                    self.buildqueue[1] += 1
                                    break
                            else:
                                log(f'Not enough resources to construct {type_id}')
                        except Exception as e:
                            log(f'Unable to build building {type_id}  at {buildlocation}')
                except Exception as e:
                    log(f'Building number {buildlocation} not found')

    def check_hero_resources_needed(self):
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
        for res in self.hero_resources.keys():
            total_res[res] = self.hero_resources[res] - Settings.min_hero_resources[res] + self.resources[res]
            if res == 'Crop':
                total_res[res] = min(total_res[res], self.resources['Granary'])
            else:
                total_res[res] = min(total_res[res], self.resources['Warehouse'])
        total_res['Free Crop'] = self.resources['Free Crop']
        buildcost_list = self.checkbuildlists(total_res)
        if fieldcondition:
            buildcost = buildcost_list[0]
        else:
            buildcost = buildcost_list[1]
        res_needed = {}
        for res_type in Gameconstants.hero_resource_ids.keys():
            res_needed[res_type] = math.ceil((buildcost[res_type] - self.resources[res_type])/100) * 100
            # Ensure hero resources are more than the setting minimum
            usable_res = self.hero_resources[res_type] - Settings.min_hero_resources[res_type]
            res_needed[res_type] = min(res_needed[res_type], usable_res)
        self.use_hero_resources(res_needed)
        self.updateres()
        self.checkbuildlists()

    def check_timers(self):
        if self.timers['refresh'] < datetime.datetime.now():
            waittime = random.randint(Settings.refresh_minsleeptime, Settings.refresh_maxsleeptime)
            self.timers['refresh'] = datetime.datetime.now() + datetime.timedelta(seconds=waittime)
            self.analyzevillage()
            self.update_hero_resources()

    def update_hero_resources(self):
        # Goto the correct page
        if self.browser.current_url() != Settings.loginurl + 'hero/inventory':
            self.browser.get(Settings.loginurl + 'hero/inventory')

        for res, res_id in Gameconstants.hero_resource_ids.items():
            xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " item' \
                    + str(res_id) \
                    + ' ")]/../div[@class="count"]'
            try:
                elem = self.browser.find(xpath)
                val = int(elem.text)
            except:
                log(f'No more {res} available')
                val = 0
            self.hero_resources[res] = val

    def use_hero_resources(self,res_to_use):
        # Goto the correct page
        if self.browser.current_url() != Settings.loginurl + 'hero/inventory':
            self.browser.get(Settings.loginurl + 'hero/inventory')
        for res, res_id in Gameconstants.hero_resource_ids.items():
            if res_to_use[res] == 0: continue
            xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " item' \
                    + str(res_id) \
                    + ' ")]/..'
            try:
                elem = self.browser.find(xpath)
                elem.click()
            except:
                log(f'Unable to find {res}')
                continue
            base_xpath = '//div[@id="consumableHeroItem"]'
            input_xpath = base_xpath + '/label/input'
            button_xpath = base_xpath \
                           + '/..'\
                           +'/div[@class="buttonsWrapper"]'\
                           +'/button[contains(concat(" ", normalize-space(@class), " "), " green ")]'
            try:
                self.browser.find(input_xpath).send_keys(res_to_use[res])
            except:
                continue
            try:
                self.browser.find(button_xpath).click()

            except:
                pass
        self.update_hero_resources()

    def collect_quests(self) -> None:
        base_xpath = '//button[@id="questmasterButton"]'
        speech_bubble_xpath = base_xpath + '/div'

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

    def run(self):
        self.buildlist(village=0,sleeptime=900)
