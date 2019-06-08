import re

from bs4 import BeautifulSoup
from collections import namedtuple
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


Shopping_List = namedtuple("ShoppingList", ["item_name", "item_price", "item_url"])


class MakroBot:
    """
        Selenium bot that searches makro website for items defined in a file and gets the
        price, name and url, in order to create a Google spreadsheet.
    """

    def __init__(self, items, headless=False, timeout=60):
        """Setup bot for makro URL."""
        self.makro_url = "https://www.makro.co.za/"
        self.items = items
        self.timeout = timeout

        self._profile = self._disable_Images_Firefox_Profile()
        self._options = Options()
        self._options.headless = headless

        self.driver = webdriver.Firefox(
            firefox_profile=self._profile,
            firefox_options=self._options,
            timeout=self.timeout,
        )

        if self._options.headless:
            print("Headless Firefox Initialized")

        try:
            # Navigate to the makro URL.
            print(f"Navigating to {self.makro_url}")
            self.driver.get(self.makro_url)
        except TimeoutException:
            print("Timeout loading page")
            self.close_session()
        else:
            # Obtain the source
            self.html = self.driver.page_source
            self.soup = BeautifulSoup(self.html, "html.parser")
            self.html_source = self.soup.prettify("utf-8")

    def _disable_Images_Firefox_Profile(self):
        # get the Firefox profile object
        firefoxProfile = webdriver.FirefoxProfile()
        # Disable images
        firefoxProfile.set_preference("permissions.default.image", 2)
        # Disable Flash
        firefoxProfile.set_preference(
            "dom.ipc.plugins.enabled.libflashplayer.so", "false"
        )
        # Set the modified profile while creating the browser object
        return firefoxProfile

    def search_items(self):
        """Searches through the list of items obtained from spreadsheet and
        obtains name, price, and URL information for each item."""
        shopping_list = []
        for count, item in enumerate(self.items, 1):
            print(f"Searching for item #{count}: {item}...")
            # self.driver.get(self.makro_url)
            # insert items on search bar
            search_id = "js-site-search-input"
            try:
                search_input = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.ID, search_id))
                )
            finally:
                search_input = self.driver.find_element_by_id(search_id)
                search_input.send_keys(item)

            # Click on search button, using xpath
            xpath = "/html/body/main/div[2]/div/div[2]/div/div/div[4]/div/div/div/div/div[2]/div/form/span[2]/a/i"
            try:
                search_button = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            finally:
                search_button = self.driver.find_element_by_xpath(xpath)
                search_button.click()

            # Select first result and open link, using xpath
            first_result_xpath = "/html/body/main/div[9]/div[3]/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]"
            try:
                first_res = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, first_result_xpath))
                )
            finally:
                first_res = self.driver.find_element_by_xpath(first_result_xpath)
                first_res.click()

            name = self.get_product_name()
            price = self.get_product_price()
            current_url = self.driver.current_url
            if "/p/" in current_url:
                current_url = self.makro_url + "p/" + current_url.split("/p/")[-1]

            shopping_list.append(
                Shopping_List(
                    item_name=name.title(), item_price=price, item_url=current_url
                )
            )

        self.close_session()
        return shopping_list

    def get_product_price(self):
        """Gets and cleans product item price on the makro page."""
        price = None
        try:
            price = self.driver.find_element_by_class_name(
                "product-PromotionSection"
            ).text
            assert isinstance(price, str) and price != ""
        except AssertionError:
            price = self.driver.find_element_by_class_name(
                "product-ProductNamePrice"
            ).text

        try:
            price = (
                re.sub("\D", "", price.split("\n")[0])
                if "\n" in price
                else "Not available"
            )
            return "ZAR %.2f" % (float(price) / 100)
        except Exception as err:
            print(f"Failed to retrieve price: {err}")
            return "Not available"

    def get_product_name(self):
        """Returns the product item name on the makro page."""
        product_name = None
        try:
            product_name = self.driver.find_element_by_class_name("name").text.split(
                "\n"
            )[0]
            assert isinstance(product_name, str) and product_name != ""
        except Exception:
            product_name = self.driver.title.split("|")[0].strip()

        if not product_name:
            product_name = "Not Available"
        return product_name

    def close_session(self):
        """Close the browser session."""
        self.driver.close()


if __name__ == "__main__":

    items = ["pampers", "golden cloud self raising flour", "jungle oats"]
    try:
        makro = MakroBot(items)
        shopping_list = makro.search_items()
    except Exception:
        makro.close_session()
    else:
        print(shopping_list, end="\n")
