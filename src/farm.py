

from selenium.common.exceptions import TimeoutException
from .custom_driver import Client, use_browser
from .utils import log
import time
from datetime import datetime
from random import randint


def start_farming_thread(browser: Client, raidlist: list, sleeptime: int) -> None:
    # Sleep for a while when starting bot
    time.sleep(randint(3,7))
    while True:
        for farmlist_index in raidlist:
            # Retry farming up to 5 times before proceeding
            for i in range(5):
                if send_farmlist(browser=browser, farmlist_index=farmlist_index):
                    log("farmlist {} sent at {}".format(str(farmlist_index), str(datetime.now())))
                    time.sleep(randint(0.85 * sleeptime, 1.15 * sleeptime))
                    break
                else:
                    log("sending farmlist {} unsuccessful at {}".format(str(farmlist_index), str(datetime.now())))
                    time.sleep(randint(1, 5))

@use_browser
def send_farmlist(browser: Client, farmlist_index: int) -> bool:

    # Navigate to farmlist
    browser.get("https://ts15.travian.com/build.php?tt=99&id=39")

    # xpath strings for elements
    listentries_xpath = "//div[@id='raidList']/div[@class= 'listEntry']"
    list_to_raid_xpath = listentries_xpath + "[" + str(farmlist_index) + "]"
    list_content_xpath = list_to_raid_xpath + "//div[contains(@class, 'listContent')]"
    open_close_button_xpath = list_to_raid_xpath + "//div[contains(@class, 'openedClosedSwitch')]"
    raid_all_box_xpath = list_content_xpath + "//div[contains(@class, 'markAll')]//input"
    raid_button_xpath = list_content_xpath + "//button[@value='Start raid']"
    success_paragraph = list_content_xpath + "//p"

    # Check if the list to raid is the active list and make active if not
    open_close_button = browser.find(open_close_button_xpath)
    open_close_class = open_close_button.get_attribute("class")
    if "openedClosedSwitch switchClosed" in open_close_class:
        open_close_button.click()
    try:
        # Select all farms on the list
        browser.xwait(raid_all_box_xpath).click()
        # Send all selected farms
        browser.xwait(raid_button_xpath).click()
        # Check if raid was successful
        if browser.xwait(success_paragraph):
            return True
    except TimeoutException:
        return False
