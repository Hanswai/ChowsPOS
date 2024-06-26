from DbDishInterface import DbDish
from interfaces.FoodItem import Dish
import sqlite3 as db
from db_variables import CHOWS_MAIN_DB
from enum import Enum
from datetime import datetime

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DeliveryMethod(Enum):
    NONE = 1
    COLLECTION = 2
    PRESENT = 3
    DELIVERY = 4

class FoodNotFoundException(Exception):
    def __init__(self, food_id) -> None:
        self.food_id = food_id
        message = f"{food_id} not found in DB."
        super().__init__(message)



class FoodOrder:
    def __init__(self):
        self.retreived_dishes = [] # This is acting like a cache - I can use the python built in cache rather than managing it myself.
        self.ordered_dishes = []
        self.delivery_method = DeliveryMethod.NONE
        self.customer = None
        self.order_id = None

    def reset(self):
        self.retreived_dishes.clear()
        self.ordered_dishes.clear()
        self.delivery_method = DeliveryMethod.NONE

    def add_to_food_order(self, dish: Dish):
        if dish is None:
            print("Why are you giving me a None?")
            return
        result = next((x for x in self.ordered_dishes if x.item_number == dish.item_number), None)
        if result:
            result.quantity += 1
        else:
            self.ordered_dishes.append(dish)

    def set_delivery_method(self, delivery_method_string):
        if delivery_method_string == "COLLECTION":
            self.delivery_method = DeliveryMethod.COLLECTION
        elif delivery_method_string == "DELIVERY":
            self.delivery_method = DeliveryMethod.DELIVERY
        elif delivery_method_string == "PRESENT":
            self.delivery_method = DeliveryMethod.PRESENT
        else:
            self.delivery_method = DeliveryMethod.NONE
    
    def set_customer(self, customer):
        self.customer = customer

    def get_all_dishes(self):
        return self.ordered_dishes
    
    def get_total_price(self):
        sum = 0
        for i in self.ordered_dishes:
            sum += i.get_total_price()
        return sum
    
    def get_food_item(self, food_id):
        if food_id:
            # check to see if I have retrieved it already
            if len(self.retreived_dishes) > 0:
                result = next((x for x in self.retreived_dishes if x.item_number == food_id), None)
                if result:
                    return result
            # Otherwise retrieve from db.
            dish_from_db =  DbDish.retrieve_dishes_by_id_like(food_id)
            if len(dish_from_db) == 0:
                raise FoodNotFoundException(food_id)
            else:
                return dish_from_db[0]

    #
    # DB related functions
    #

    def save_order_to_db(self):
        if len(self.ordered_dishes) == 0:
            return 
        connection = db.connect(CHOWS_MAIN_DB)
        connection.row_factory = dict_factory
        with connection:
            c = connection.cursor()
            insert_main_order_db = (datetime.now().date(), 
                        self.delivery_method.name, 
                        self.customer.id if self.customer is not None else "",
                        str(self.get_total_price()))
            c.execute("""   INSERT INTO ORDER_DETAILS (DATE_RECEIVED, ORDER_TYPE, CUSTOMER_ID, TOTAL_PRICE) 
                            VALUES (?, ?, ?, ?) """, 
                        insert_main_order_db)

            self.order_id = c.lastrowid
            insert_items_order_db = []
            for food_item in self.ordered_dishes:
                insert_items_order_db.append((  food_item.id,
                                                self.order_id,
                                                food_item.quantity,
                                                food_item.note))
            
            c.executemany("""   INSERT INTO ORDER_ITEMS (FOOD_ITEM_ID, ORDER_ID, QUANTITY, NOTE) 
                                VALUES (?, ?, ?, ?) """, 
                        insert_items_order_db)
            connection.commit()

    # def retrieve_food_item(self, food_id):
    #     connection = db.connect(CHOWS_MAIN_DB)
    #     connection.row_factory = dict_factory
    #     food_item = None
    #     with connection:
    #         c = connection.cursor()
    #         c.execute("SELECT * FROM DISH WHERE ID = ?", (food_id,))
    #         result = c.fetchone()
    #         if result:
    #             food_item = FoodItem(result['ID'], float(result['PRICE']), 1, result['DESCRIPTION'], result['DESCRIPTION_CHINESE'])
    #             self.retreived_food_items.append(food_item)
    #             return food_item
    #     raise FoodNotFoundException(food_id)
