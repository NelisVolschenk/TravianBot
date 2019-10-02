

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .custom_driver import Client
from .utils import log
import time
from datetime import datetime
from random import randint


def start_farming_thread(browser: Client, raidlist: list, sleeptime: int) -> None:
    # Sleep for a while when starting bot
    time.sleep(randint(3,7))
    while True:
        for farmlist_index in raidlist:
            #retry farming up to 5 times then proceed
            for i in range(5):
                if send_farmlist(browser=browser, farmlist_index=farmlist_index):
                    log("farmlist {} sent at {}".format(str(farmlist_index), str(datetime.now())))
                    time.sleep(randint(0.85 * sleeptime, 1.15 * sleeptime))
                    break
                else:
                    log("sending farmlist {} unsuccessful at {}".format(str(farmlist_index), str(datetime.now())))
                    time.sleep(randint(1, 5))

def send_farmlist(browser: Client, farmlist_index: int) -> bool:
    browser.get("https://ts15.travian.com/build.php?tt=99&id=39")
    raidlist = browser.find("//div[@id='raidList']")
    listentries = raidlist.find_elements_by_xpath("./div[@class= 'listEntry']")
    # Check if the list to raid is the active list
    open_close_button = listentries[farmlist_index].find_element_by_xpath(".//div[contains(@class, 'openedClosedSwitch')]")
    classes = open_close_button.get_attribute("class")
    # Make active if not
    if "openedClosedSwitch switchClosed" in classes:
        open_close_button.click()
        time.sleep(randint(5, 7))
    try:
        # Raid all farms on the list
        raidlist = browser.find("//div[@id='raidList']")
        wait = WebDriverWait(browser, 30)
        # xpath strings for elements

        xpath_string = "//div[@id='raidList']/div[@class= 'listEntry'][" + str(farmlist_index) +\
                       "]//div[contains(@class, 'listContent')]//div[contains(@class, 'markAll')]"
        wait.until(EC.presence_of_element_located(By.XPATH(xpath_string)))
        listentries = raidlist.find_elements_by_xpath("./div[@class= 'listEntry']")
        list_to_raid = listentries[farmlist_index].find_element_by_xpath(".//div[contains(@class, 'listContent')]")
        raid_all_box = list_to_raid.find_element_by_xpath(".//div[contains(@class, 'markAll')]").find_element_by_xpath(".//input")
        time.sleep(randint(3, 7))
        raid_all_box.click()
        raid_button = list_to_raid.find_element_by_xpath(".//button[@value='Start raid']")
        raid_button.click()
        time.sleep(randint(5, 7))
        # Check if raid was successful and sleep if it was

        raidlist = browser.find("//div[@id='raidList']")
        listentries = raidlist.find_elements_by_xpath("./div[@class= 'listEntry']")
        list_to_raid = listentries[farmlist_index].find_element_by_xpath(".//div[contains(@class, 'listContent')]")
        para = list_to_raid.find_element_by_xpath(".//p")
        return True
    except NoSuchElementException:
        return False
