from selenium import webdriver
import logging
from logging.handlers import RotatingFileHandler
from .settings import Settings
import string

# Create a rotating logger
def create_rotating_log(path):
	# Create the logger
	logger = logging.getLogger("Main Logger")
	logger.setLevel(logging.DEBUG)
	# Create a rotating filehandler
	filehandler = RotatingFileHandler(path, maxBytes=1048576, backupCount=5)
	filehandler.setLevel(logging.DEBUG)
	# Create a streamhandler to print to console
	consolehandler = logging.StreamHandler()
	consolehandler.setLevel(logging.INFO)
	# Create a formatter and add to filehandler and consolehandler
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	filehandler.setFormatter(formatter)
	consolehandler.setFormatter(formatter)
	# Add the filehandler and consolehandler to the logger
	logger.addHandler(filehandler)
	logger.addHandler(consolehandler)
	return logger


def log(message: str) -> None:
	print(message)

def printable(text: str) -> str:
	return ''.join([x for x in text if x in string.printable])



def reconnect_firefox_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver
