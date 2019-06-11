import logging
import os
import re
import sys
import time
from collections import namedtuple

import coloredlogs
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

Shopping_List = namedtuple(
    "ShoppingList", ["shop_name", "item_name", "item_price", "item_url"]
)

TIMEOUT = 30
ids = {
    "makro": {
        "first_result_xpath": "/html/body/main/div[9]/div[3]/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]",
        "price_product": "product-ProductNamePrice",
        "price_promotion": "product-PromotionSection",
        "product_name": "name",
        "search_button_xpath": "/html/body/main/div[2]/div/div[2]/div/div/div[4]/div/div/div/div/div[2]/div/form/span[2]/a/i",
        "search_input_id": "js-site-search-input",
        "url_shortner_pattern": "/p/",
        "url_shortner_linker": "",
    },
    "game": {
        "first_result_xpath": "/html/body/main/div[3]/div[2]/div[2]/div/div/div/ul/div[1]/a/div",
        "price_product": "pdp_price",
        "price_promotion": "pdp_price",
        "product_name": "name",
        "search_button_xpath": "/html/body/main/header/nav[1]/div/div[2]/div[2]/div/div/div/form/div/span/button",
        "search_input_id": "js-site-search-input",
        "url_shortner_pattern": "/p/",
        "url_shortner_linker": "",
    },
    "pnp": {
        "first_result_xpath": "/html/body/main/div[4]/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[1]/ul/div[1]/div/div[3]/a/div[1]",
        "price_product": "normalPrice",
        "price_promotion": "pricedata-Save",
        "product_name": "fed-pdp-product-details-title",
        "search_button_xpath": "/html/body/main/header/div[1]/div[2]/div/div[7]/div/form/div/span/button/span",
        "search_input_id": "js-site-search-input",
        "url_shortner_pattern": "/p/",
        "url_shortner_linker": "",
    },
    "woolworths": {
        "first_result_xpath": "/html/body/div/div/div/main/div/div/div/div[1]/div[1]/div[3]/div[1]/article/div[2]/a/h2",
        "price_product": "price",
        "price_promotion": "price",
        "product_name": "ffont-graphic heading--400 heading--sub no-wrap--ellipsis",
        "search_button_xpath": "/html/body/div/div/header/div[2]/div/section[3]/div/div/form/input[3]",
        "search_input_id": "fldSearch",
        "url_shortner_pattern": "_/",
        "url_shortner_linker": "prod/",
    },
    "takealot": {
        "first_result_xpath": '//*[@id="pos_link_0"]',
        "price_product": "sf-price",
        "price_promotion": "sf-price",
        "product_name": "product-title",
        "search_button_xpath": "/html/body/div[3]/div/div[2]/form/fieldset/input[5]",
        "search_input_id": "search",
        "url_shortner_pattern": "/",
        "url_shortner_linker": "",
    },
}


class LoggingClass:
    @property
    def logger(self):
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s - "
            "%(pathname)s : %(lineno)d - %(message)s"
        )
        name = ".".join([os.path.basename(sys.argv[0]), self.__class__.__name__])
        logging.basicConfig(format=log_format)
        return logging.getLogger(name)


class WebDriverSetup:
    def __init__(self):
        self._timeout = TIMEOUT
        self._options = Options()
        self._options.headless = True
        self._profile = self._disable_Images_Firefox_Profile()

        self.driver = webdriver.Firefox(
            firefox_profile=self._profile, options=self._options, timeout=self._timeout
        )

        if self._options.headless:
            self.logger.info("Headless Firefox Initialized")

        try:
            # Navigate to the makro URL.
            self.logger.info(f"Navigating to {url}")
            self.driver.get(url)
        except TimeoutException:
            self.logger.exception("Timeout loading page")
            self.close_session()
            sys.exit(1)
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


class ShoppingBot(WebDriverSetup, LoggingClass):
    """
        Selenium bot that searches makro website for items defined in a file and gets the
        price, name and url, in order to create a Google spreadsheet.
    """

    def __init__(self, items, url, ids, log_level="INFO"):
        assert isinstance(items, list)
        self.items = items
        assert isinstance(url, str)
        self.url = url
        assert isinstance(ids, dict)
        self.ids = ids
        self.item = None
        self.logger.setLevel(log_level.upper())
        coloredlogs.install(level=log_level.upper())
        super().__init__()

    def search_items(self):
        """Searches through the list of items obtained from spreadsheet and
        obtains name, price, and URL information for each item."""
        shopping_list = []
        for count, self.item in enumerate(self.items, 1):
            self.driver.get(self.url)
            time.sleep(0.3)
            self.logger.info(
                f"Searching on url: {self.url} for item #{count}: {self.item}..."
            )
            try:
                search_input_id = self.ids[self.url.split(".")[1]]["search_input_id"]
                self.logger.debug(f"inserting {self.item} on search bar")
                search_input = WebDriverWait(self.driver, self._timeout).until(
                    EC.presence_of_element_located((By.ID, search_input_id))
                )
            except Exception:
                self.logger.error("No Data Available")
            else:
                search_input = self.driver.find_element_by_id(search_input_id)
                search_input.send_keys(self.item)

            try:
                search_button_xpath = self.ids[self.url.split(".")[1]][
                    "search_button_xpath"
                ]
                self.logger.debug("Clicking on search button, using xpath")
                search_button = WebDriverWait(self.driver, self._timeout).until(
                    EC.presence_of_element_located((By.XPATH, search_button_xpath))
                )
            except Exception:
                self.logger.error("No Data Available")
            else:
                search_button = self.driver.find_element_by_xpath(search_button_xpath)
                search_button.click()
                time.sleep(0.5)

            try:
                self.logger.debug("Selecting first result and open link, using xpath")
                first_result_xpath = self.ids[self.url.split(".")[1]][
                    "first_result_xpath"
                ]
                first_res = WebDriverWait(self.driver, self._timeout).until(
                    EC.presence_of_element_located((By.XPATH, first_result_xpath))
                )
            except Exception:
                self.logger.error("No Data Available")
            else:
                first_res = self.driver.find_element_by_xpath(first_result_xpath)
                first_res.click()
                time.sleep(0.5)

            try:
                name = self.get_product_name()
                price = self.get_product_price()
                current_url = self.get_current_url()

                if name != "Not Available":
                    shopping_list.append(
                        Shopping_List(
                            shop_name=self.url.split(".")[1],
                            item_name=name.title(),
                            item_price=price,
                            item_url=current_url,
                        )
                    )
                    assert len(shopping_list) != 0 and isinstance(shopping_list, list)
            except Exception:
                self.logger.error("No Data Available")

        self.close_session()
        return shopping_list

    def get_current_url(self):
        current_url = self.driver.current_url
        url_pattern = self.ids[self.url.split(".")[1]]["url_shortner_pattern"]
        linker = self.ids[self.url.split(".")[1]]["url_shortner_linker"]
        if url_pattern in current_url:
            current_url = (
                self.url + linker + url_pattern + current_url.split(url_pattern)[-1]
            )
        return current_url

    def get_product_price(self):
        """Gets and cleans product item price on the makro page."""
        price = None
        try:
            price = self.driver.find_element_by_class_name(
                self.ids[self.url.split(".")[1]]["price_promotion"]
            ).text
            time.sleep(0.5)
            assert isinstance(price, str) and price != ""
        except Exception:
            self.logger.debug(f"{self.item} is not on promotion, getting normal price")
            time.sleep(0.5)
            price = self.driver.find_element_by_class_name(
                self.ids[self.url.split(".")[1]]["price_product"]
            ).text

        try:
            time.sleep(0.2)
            if "takealot" in self.url.split(".")[1]:
                return price.split("R")[-1]
            elif "woolworths" in self.url.split(".")[1]:
                return price.split("R")[-1].strip()
            elif "makro" in self.url.split(".")[1]:
                price = re.sub("\D", "", price.split("\n")[0]) if "R" in price else price
                return "%.2f" % (float(price) / 100)
            elif "pnp" in self.url.split(".")[1]:
                return "%.2f" % (float(price.split("R")[-1]) / 100)
            elif "game":
                price = re.sub("\D", "", price.split("\n")[0])
                return float(price) / 100
        except Exception:
            self.logger.exception(
                f"Failed to retrieve price for {self.item} on {self.url}"
            )
            return "Not available"

    def get_product_name(self):
        """Returns the product item name on the makro page."""
        product_name = None
        try:
            product_name = self.driver.title.split("|")[0].strip()
            assert isinstance(product_name, str) and product_name != ""
        except Exception:
            product_name = self.driver.find_element_by_class_name(
                self.ids[self.url.split(".")[1]]["product_name"]
            ).text.split("\n")[0]

        if (not product_name) or (product_name.lower() in self.driver.current_url):
            self.logger.error("Failed to get item name from class, and title")
            product_name = "Not Available"
        return product_name

    def close_session(self):
        """Close the browser session."""
        self.driver.close()


if __name__ == "__main__":

    items = ["pampers pants", "self raising flour", "jungle oats 1kg"]
    urls = [
        "https://www.makro.co.za/",
        "https://www.game.co.za/",
        "https://www.pnp.co.za/",
        "https://www.woolworths.co.za/",
        "https://www.takealot.com/",
    ]

    for url in urls:
        try:
            shopping_bot = ShoppingBot(items, url, ids, "FATAL")
            shopping_list = shopping_bot.search_items()
        except Exception:
            shopping_bot.close_session()
        else:
            print(shopping_list, end="\n\n")
