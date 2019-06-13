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

        self.item_col = 2
        self.product_info_row = 3
        self.stores_info = {}
        self.price_col = 2
        self.frequency_col = 3
        self.url_col = 4
        self.product_name_row = 5
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

    # def update_spreadsheet_price(self):
    #     urls = self.sheet.col_values(self.url_col)

    #     for i in range(1, len(urls)):
    #         print(f"Processing URL {i} or {len(urls)-1}")
    #         amazon_bot = AmazonBot(urls[i])
    #         product_name = amazon_bot.get_product_name()
    #         product_price = amazon_bot.get_product_price()

    #         print(f"Updating item {self.sheet.cell(i+1, self.item_col).value} from Amazon listing {product_name} with price {product_price}")
    #         self.sheet.update_cell(i+1, self.price_col, product_price)
    #         amazon_bot.close_session()

    def get_all_stores(self):
        return {
            coord.value :(coord.row, coord.col)
            for coord in [
                self.sheet.find(store_name)
                for store_name in self.sheet.row_values(self.stores_row)
                if store_name
            ]
        }


    def get_all_product_name_coord(self, product_name="Product Name"):
        return [(coord.row + self.row_start, coord.col) for coord in self.sheet.findall(product_name)]

    def get_all_price_coord(self, price="Price"):
        return [(coord.row + self.row_start, coord.col) for coord in self.sheet.findall(price)]

    def get_all_url_coord(self, url="URL"):
        return [(coord.row + self.row_start, coord.col) for coord in self.sheet.findall(url)]

    def get_all_items(self, items="Item"):
        items_coord = self.sheet.find(items)
        col, row = items_coord.col, items_coord.row
        return [item for item in self.sheet.col_values(col)[row:] if item]

    def get_shopping_cart(self):
        items = self.get_all_items()
        urls = shopping_bot.URLS
        for url in urls:
            crawling_bot = shopping_bot.ShoppingBot(items, url)
            crawling_bot.search_items()
        return crawling_bot.shopping_cart

    def process_item_list(self):
        # Skip over the column heading in the spreadsheet.
        shopping_carts = self.get_shopping_cart()
        available_stores_coord = self.get_all_stores()
        product_names_coord = self.get_all_product_name_coord()
        prices_coord = self.get_all_price_coord()
        urls_coord = self.get_all_url_coord()

        for shop_name, shopping_cart in shopping_carts.items():
            for shop_coord in available_stores_coord[shop_name]:
                for prod_coord in product_names_coord:
                    if shop_coord == prod_coord[1]:
                        for count, cart in enumerate(shopping_cart):
                            # self.sheet.update_cell(
                            print(
                                prod_coord[0] + count,
                                prod_coord[1],
                                cart.item_name
                            )
                            print(
                            # self.sheet.update_cell(
                                prod_coord[0] + count,
                                prod_coord[1]+1,
                                cart.item_price
                            )
                            print(
                            # self.sheet.update_cell(
                                prod_coord[0] + count,
                                prod_coord[1]+2,
                                cart.item_url
                            )
                        # available_stores_coord.pop(shop_name, None)

        import IPython

        globals().update(locals())
        IPython.embed(header="Python Debugger")
        self.logger.info("Updating spreadsheet.")


if __name__ == "__main__":

    price_updater = PriceUpdater("Shopping List", "client_secret.json")
    price_updater.process_item_list()
