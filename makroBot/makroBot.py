import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class MakroBot(object):
    """Parses relevant information from a text file consisting of
    makro links."""

    def __init__(self, items, timeout=60):
        """Setup bot for makro URL."""
        self.makro_url = "https://www.makro.co.za/"
        self.items = items
        self.timeout = timeout

        # self.profile = webdriver.FirefoxProfile()
        self.options = Options()
        self.options.headless = True

        self.driver = webdriver.Firefox(
            # firefox_profile=self.profile,
            firefox_options=self.options,
            timeout=self.timeout,
        )

        # Navigate to the makro URL.
        try:
            print("Navigating to %s" % self.makro_url)
            self.driver.get(self.makro_url)
        except TimeoutException:
            print("Timeout loading page")
            self.close_session()
        if self.options.headless:
            print("Headless Firefox Initialized")

        # # Obtain the source
        # self.html = self.driver.page_source
        # self.soup = BeautifulSoup(self.html, 'html.parser')
        # self.html = self.soup.prettify('utf-8')

    def search_items(self):
        """Searches through the list of items obtained from spreadsheet and
        obtains name, price, and URL information for each item."""
        urls = []
        prices = []
        names = []
        for item in self.items:
            print(f"Searching for {item}...")
            self.driver.get(self.makro_url)
            # insert items on search bar
            search_id = "js-site-search-input"
            try:
                search_input = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.ID, search_id))
                )
            finally:
                search_input = self.driver.find_element_by_id(search_id)
                search_input.send_keys(item)

            # Click on search button
            xpath = "/html/body/main/div[2]/div/div[2]/div/div/div[4]/div/div/div/div/div[2]/div/form/span[2]/a/i"
            try:
                search_button = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            finally:
                search_button = self.driver.find_element_by_xpath(xpath)
                search_button.click()

            # Select first result and open link
            first_result_xpath = "/html/body/main/div[9]/div[3]/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]"
            try:
                first_res = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, first_result_xpath))
                )
            finally:
                first_res = self.driver.find_element_by_xpath(first_result_xpath)
                first_res.click()

            current_url = self.driver.current_url
            if "/p/" in current_url:
                current_url = self.makro_url + "p/" + current_url.split("/p/")[-1]

            name = self.get_product_name(current_url)
            print(name)
            price = self.get_product_price(current_url)
            print(price)
            print(current_url)
            print()

            names.append(name)
            prices.append(price)
            urls.append(current_url)

        self.close_session()
        return prices, urls, names

    def get_product_price(self, url):
        """Gets and cleans product price from makro page."""
        self.driver.get(url)
        price = None
        try:
            price = self.driver.find_element_by_class_name(
                "product-ProductNamePrice"
            ).text
        except:
            pass

        try:
            assert price
        except AssertionError:
            price = self.driver.find_element_by_class_name(
                "product-PromotionSection"
            ).text

        try:
            price = float(re.sub("\D", "", price.split("\n")[0])) / 100
        except:
            price = "Not available"

        return "R %s" % price

    def get_product_name(self, url):
        """Returns the product name of the makro URL."""
        self.driver.get(url)
        product_name = None
        try:
            product_name = self.driver.find_element_by_class_name("name").text
        except:
            pass

        try:
            assert product_name
        except AssertionError:
            product_name = self.driver.title.split("|")[0].strip()

        if not product_name:
            product_name = 'Not Available'
        return product_name

    def close_session(self):
        """Close the browser session."""
        self.driver.close()


if __name__ == "__main__":
    items = ["pampers", "golden cloud flour", "jungle oats"]
    try:
        makro = MakroBot(items)
        makro.search_items()
    except Exception:
        makro.close_session()
