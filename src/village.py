from .custom_driver import Client

def select_village(browser: Client, village_id: int) -> None:
    index = village_id
    # check selected village
    ul = browser.find("//div[@id='sidebarBoxVillagelist']")
    ul = ul.find_element_by_xpath(".//div[@class='content']")
    ul = ul.find_element_by_xpath(".//ul")
    lis = ul.find_elements_by_xpath(".//li")
    classes = lis[index].get_attribute("class")
    if "active" in classes:
        pass
    else:
        link = lis[index].find_element_by_xpath(".//a")
        link.click()
