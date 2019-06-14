import unittest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys


class MakroBot(unittest.TestCase):

    def setUp(self):
        self._options = Options()
        self._options.headless = True
        self.driver = webdriver.Firefox(options=self._options, timeout=30)

    def test_search(self):
        driver = self.driver
        driver.get("https://www.makro.co.za/")
        self.assertIn("Makro", driver.title)
        elem = driver.find_element_by_id("js-site-search-input")
        elem.send_keys("beer")
        elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()