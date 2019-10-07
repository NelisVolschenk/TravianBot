from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.remote import webelement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from typing import Any
from threading import RLock
import time
from .utils import log
from .utils import reconnect_firefox_session
from .settings import Settings


def use_browser(org_func: Any):
    def wrapper(*args, **kwargs):
        browser = None
        for arg in args:
            if type(arg) is Client:
                browser = arg
                break

        for _, value in kwargs.items():
            if type(value) is Client:
                browser = value
                break

        if browser != None:
            rv = None
            browser.use()

            try:
                rv = org_func(*args, **kwargs)
            except Exception as e:
                rv = None
                log("exception in function: {} exception: {}".format(
                    org_func.__name__, str(e)))

                log("reloading world")
                url = browser.driver.current_url
                world = url.split('//')
                world = world[1]
                world = world.split('.')
                world = world[0]

                browser.get('https://{}.travian.com/dorf1.php'.format(world))
            finally:
                browser.done()

                return rv

        else:
            return org_func(*args, **kwargs)

    return wrapper



class Client:
    def __init__(self, debug: bool = False) -> None:
        self.driver: webdriver = None
        self.delay = None
        self._headless: bool = False
        self.lock = RLock()     # For later
        self.proxy: bool = False  # For later
        self.debug: bool = debug
        self.current_session_path: str = Settings.current_session_path
        pass

    def firefox(self) -> None:
        options = webdriver.FirefoxOptions()
        fp = FirefoxProfile(profile_directory=Settings.firefox_profile_path)
        #fp.set_preference('')
        self.driver = webdriver.Firefox(firefox_profile=fp)
        self.set_config()
        self.save_session()

    def remote(self) -> None:
        if self.debug is False:
            log("debug mode is turned off, can't reuse old session")
            return
        file = open(self.current_session_path, "r")
        content = file.read()
        lines = content.split(";")
        url = lines[0]
        session = lines[1]
        self.driver = reconnect_firefox_session(session, url)
        self.set_config()

    def headless(self) -> None:
        # Todo implement headless mode
        log('Headless not implemented yet')
        pass

    def set_config(self) -> None:
        #todo check these out
        # set timeout to find an element in seconds
        self.driver.implicitly_wait(5 * Settings.browser_speed)
        # set page load timeout in seconds
        self.driver.set_page_load_timeout(60 + Settings.browser_speed)

    # region locks
    def use(self) -> None:
        self.lock.acquire()

    def done(self) -> None:
        self.lock.release()
    # endregion

    # region browser functions
    def get(self, page: str) -> None:
        self.driver.get(page)

    def find(self, xpath: str, wait: float = 0) -> webelement:
        # todo wait x seconds until presencd of element
        wait = wait * Settings.browser_speed
        self.sleep(wait)
        return self.driver.find_element_by_xpath(xpath)

    def finds(self, xpath: str, wait: float = 0) -> webelement:
        # todo wait x seconds until presencd of element
        wait = wait * Settings.browser_speed
        self.sleep(wait)
        return self.driver.find_elements_by_xpath(xpath)

    def sleep(self, seconds: float) -> None:
        seconds = seconds * Settings.browser_speed

        # reduce sleep time if in headless mode
        if self._headless:
            seconds = seconds / 2

        # doubles the sleep time, proxys are normally way slower
        if self.proxy:
            seconds = seconds * 2

        time.sleep(seconds)

    def xwait(self, xpath: str, timeout: int = 10) -> webelement:
        timeout = timeout * Settings.browser_speed
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def xwait_click(self, xpath: str, timeout: int = 10) -> webelement:
        timeout = timeout * Settings.browser_speed
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def click(self, element: webelement, wait: float = 0.5) -> None:
        ActionChains(self.driver).move_to_element(element).click().perform()

        wait = wait * Settings.browser_speed
        self.sleep(wait)

    def click_v2(self, element: webelement, wait: float = 0.5) -> None:
        ActionChains(self.driver).move_to_element(element).click(element).perform()

        wait = wait * Settings.browser_speed
        self.sleep(wait)

    def hover(self, element: webelement, wait: float = 0.5) -> None:
        ActionChains(self.driver).move_to_element(element).perform()

        wait = wait * Settings.browser_speed
        self.sleep(wait)

    def scroll_down(self, element: webelement) -> None:
        element.send_keys(Keys.PAGE_DOWN)

    def refresh(self) -> None:
        self.driver.refresh()

    def current_url(self) -> str:
        return self.driver.current_url
    # endregion browser functions

    # region sessions
    def save_session(self) -> None:
        if self.debug is False:
            return

        url = self.driver.command_executor._url
        session = self.driver.session_id

        filename = self.current_session_path
        semi = ';'

        content = url + semi + session

        try:
            file = open(filename, "w")
            file.write(content)
            file.close()
        except:
            log('Error saving Session')
    #endregion sessions
