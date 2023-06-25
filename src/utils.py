from selenium import webdriver
import logging
from logging.handlers import RotatingFileHandler
from .settings import Settings
import string

# Create a rotating logger
def create_rotating_log(path):
	# Create the logger
	logger = logging.getLogger("Main Logger")
	logger.setLevel(logging.INFO)
	# Create a rotating handler
	handler = RotatingFileHandler(path, maxBytes=1048576, backupCount=5)
	# Create a formatter and add to handler
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	# Add the handler to the logger
	logger.addHandler(handler)
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
