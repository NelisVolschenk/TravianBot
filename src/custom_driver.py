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
from .settings import Settings


class Client:
    def __init__(self, debug: bool = False) -> None:
        self.driver: webdriver = None
        self.options = webdriver.FirefoxOptions()
        self.delay = None
        self._headless: bool = False
        self.lock = RLock()     # For later
        self.proxy: bool = False  # For later
        self.debug: bool = debug
        pass

    def firefox(self) -> None:
        profile = FirefoxProfile(profile_directory=Settings.firefox_profile_dir)
        self.driver = webdriver.Firefox(executable_path=Settings.geckodriver_dir,
                                        firefox_binary=Settings.firefox_dir,
                                        firefox_profile=profile,
                                        options=self.options)
        self.set_config()

    def headless(self) -> None:
        self.options.headless = True
        self.firefox()


    def set_config(self) -> None:
        #todo: check these out
        # set timeout to find an element in seconds
        self.driver.implicitly_wait(5 * Settings.browser_speed)
        # set page load timeout in seconds
        self.driver.set_page_load_timeout(120 + Settings.browser_speed)

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
        self.sleep(wait)
        return self.driver.find_element_by_xpath(xpath)

    def finds(self, xpath: str, wait: float = 0) -> webelement:
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

    # def click(self, element: webelement, wait: float = 0.5) -> None:
    #     ActionChains(self.driver).move_to_element(element).click().perform()
    #     self.sleep(wait)

    def click_v2(self, element: webelement, wait: float = 0.5) -> None:
        element = self.driver.find_element(By.CSS_SELECTOR, "body")
        actions = ActionChains(self.driver)
        actions.move_to_element(element, 0, 0).perform()
        element = self.driver.find_element(By.CSS_SELECTOR, ".g31Bottom > .highlightShape > path")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.CSS_SELECTOR, ".g31Bottom > .highlightShape > path").click()
        # ActionChains(self.driver).move_to_element(element).click(element).perform()
        # self.sleep(wait)

    def hover(self, element: webelement, wait: float = 0.5) -> None:
        ActionChains(self.driver).move_to_element(element).perform()
        self.sleep(wait)

    def scroll_down(self, element: webelement) -> None:
        element.send_keys(Keys.PAGE_DOWN)

    def refresh(self) -> None:
        self.driver.refresh()

    def current_url(self) -> str:
        return self.driver.current_url

    def quit(self) -> None:
        self.driver.quit()
    # endregion browser functions
