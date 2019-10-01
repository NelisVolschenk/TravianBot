

from selenium.common.exceptions import NoSuchElementException
from .custom_driver import Client
from .utils import log
import time
from datetime import datetime
from random import randint


def start_farming_thread(browser: Client, farmlist_index: int, sleeptime: int) -> None:
    time.sleep(randint(3,7))
    while True:
        #for farmlist_index in raidlist:
        if send_farmlist(browser=browser, farmlist_index=farmlist_index):
            log("farmlist {} sent at {}".format(str(farmlist_index), str(datetime.now())))
        time.sleep(randint(0.85 * sleeptime, 1.15 * sleeptime))

def send_farmlist(browser: Client, farmlist_index: int) -> bool:

    # Navigate to raidlists
    # self.select_village(village)
    time.sleep(randint(3, 7))
    browser.get("https://ts15.travian.com/build.php?tt=99&id=39")
    raidlist = browser.find("//div[@id='raidList']")
    listentries = raidlist.find_elements_by_xpath("./div[@class= 'listEntry']")
    for entry in listentries:
        log(entry)
    # Check if the list to raid is the active list
    # todo fix opening the right tab
    open_close_button = listentries[farmlist_index].find_element_by_xpath(".//div[contains(@class, 'openedClosedSwitch')]")
    classes = open_close_button.get_attribute("class")
    log(classes)
    # Make active if not
    if "openedClosedSwitch switchClosed" in classes:
        log('raidlist closed: Opening')
        open_close_button.click()
        time.sleep(2)
    # Raid all farms on the list
    raidlist = browser.find("//div[@id='raidList']")
    listentries = raidlist.find_elements_by_xpath("./div[@class= 'listEntry']")
    list_to_raid = listentries[farmlist_index].find_element_by_xpath(".//div[contains(@class, 'listContent')]")
    raid_all_box = list_to_raid.find_element_by_xpath(".//div[@class='markAll']").find_element_by_xpath(".//input")
    time.sleep(randint(3, 7))
    raid_all_box.click()
    raid_button = list_to_raid.find_element_by_xpath(".//button[@value='Start raid']")
    raid_button.click()
    # Check if raid was successfu and sleep if it was
    try:
        raidlist = browser.find("//div[@id='raidList']")
        listentries = raidlist.find_elements_by_xpath("./div[@class= 'listEntry']")
        list_to_raid = listentries[farmlist_index].find_element_by_xpath(".//div[contains(@class, 'listContent')]")
        para = list_to_raid.find_element_by_xpath(".//p")
        print('Raid successful')
        return True
    except NoSuchElementException:
        return False
