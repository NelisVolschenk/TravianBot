from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from threading import RLock
import time
from .utils import log
from .utils import reconnect_firefox_session
from .settings import Settings


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

    def firefox(self,) -> None:
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox()
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

    def headless(self):
        # Todo implement headless mode
        log('Headless not implemented yet')
        pass

    def set_config(self) -> None:
        # set timeout to find an element in seconds
        self.driver.implicitly_wait(5 * Settings.browser_speed)
        # set page load timeout in seconds
        self.driver.set_page_load_timeout(15 + Settings.browser_speed)

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

        # doubles the sleep time, proxys are normaly way slower
        if self.proxy:
            seconds = seconds * 2

        time.sleep(seconds)

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
