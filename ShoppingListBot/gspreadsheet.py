import gspread
import ShoppingListBot as shopping_bot
from ShoppingListBot import LoggingClass
from oauth2client.service_account import ServiceAccountCredentials

import logging

import coloredlogs


class PriceUpdater(LoggingClass):
    def __init__(self, spreadsheet_name, secrets_json, log_level="INFO"):
        self.secrets_json = secrets_json
        self.row_start = 2
        self.stores_row = 2

        self.logger.setLevel(log_level.upper())
        coloredlogs.install(level=log_level.upper())

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(self.secrets_json, scope)
        client = gspread.authorize(creds)
        self.sheet = client.open(spreadsheet_name).sheet1
        self.logger.info("Successfully opened spreadsheet: %s", spreadsheet_name)

    def get_all_stores(self):
        return {
            coord.value: (coord.row, coord.col)
            for coord in [
                self.sheet.find(store_name)
                for store_name in self.sheet.row_values(self.stores_row)
                if store_name
            ]
        }

    def get_all_product_name_coord(self, product_name="Product Name"):
        return [
            (coord.row + self.row_start, coord.col)
            for coord in self.sheet.findall(product_name)
        ]

    def get_all_price_coord(self, price="Price"):
        return [
            (coord.row + self.row_start, coord.col) for coord in self.sheet.findall(price)
        ]

    def get_all_url_coord(self, url="URL"):
        return [
            (coord.row + self.row_start, coord.col) for coord in self.sheet.findall(url)
        ]

    def get_all_items(self, items="Item"):
        items_coord = self.sheet.find(items)
        col, row = items_coord.col, items_coord.row
        return [item for item in self.sheet.col_values(col)[row:] if item]

    def get_shopping_cart(self):
        items = self.get_all_items()
        urls = shopping_bot.URLS
        shopping_carts = []
        self.logger.info(f"[Attempting] to retrieve product information.")
        for url in urls:
            crawling_bot = shopping_bot.ShoppingBot(items, url)
            crawling_bot.search_items()
            shopping_carts.append(crawling_bot.shopping_cart)
        self.logger.info(
            f"[Done] Retrieving product information from {crawling_bot.__class__}"
        )
        return shopping_carts

    def process_item_list(self):
        list_of_shopping_carts = self.get_shopping_cart()
        available_stores_coord = self.get_all_stores()
        product_names_coord = self.get_all_product_name_coord()
        prices_coord = self.get_all_price_coord()
        urls_coord = self.get_all_url_coord()

        for shopping_carts in list_of_shopping_carts:
            for shop_name, shopping_cart in shopping_carts.items():
                for shop_coord in available_stores_coord[shop_name]:
                    for prod_coord in product_names_coord:
                        if shop_coord == prod_coord[1]:
                            self.logger.info(f"Updating Google Sheets for {shop_name}.")
                            for count, cart in enumerate(shopping_cart):
                                self.logger.info(
                                    f"Updated {cart.item_name} and {cart.item_price}."
                                )
                                self.sheet.update_cell(
                                    prod_coord[0] + count, prod_coord[1], cart.item_name
                                )
                                self.sheet.update_cell(
                                    prod_coord[0] + count,
                                    prod_coord[1] + 1,
                                    cart.item_price,
                                )
                                self.sheet.update_cell(
                                    prod_coord[0] + count,
                                    prod_coord[1] + 2,
                                    cart.item_url,
                                )
                            available_stores_coord.pop(shop_name, None)

    def update_spreadsheet_price(self):
        # TODO
        # get urls from spreadsheet
        # for url in urls
        #   > get new prices from shopping bot
        #   > update spreadsheet with new prices
        pass


if __name__ == "__main__":
    price_updater = PriceUpdater("Shopping List", "client_secret.json")
    price_updater.process_item_list()
