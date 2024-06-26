""" A Bunch of ultity functions to interface with DB"""

from interfaces.FoodItem import Dish
import sqlite3 as db
from db_variables import CHOWS_MAIN_DB

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DuplicateFoodException(Exception):
    def __init__(self):            
        # Call the base class constructor with the parameters it needs
        super().__init__()

class DbDish:
  
    @staticmethod
    def retrieve_dishes_by_id_like(sub_id):
        connection = db.connect(CHOWS_MAIN_DB)
        connection.row_factory = dict_factory
        dishes = []
        with connection:
            c = connection.cursor()
            sql_query_string = "SELECT * FROM DISH WHERE ID LIKE ?||'%'"
            c.execute(sql_query_string, (sub_id,))
            rows = c.fetchall()
            for row in rows:
                dish = Dish(row['ID'], float(row['PRICE']), 1, row['DESCRIPTION'], row['DESCRIPTION_CHINESE'])
                dish.categories = dish.deserialise_categories(row['CATEGORIES'])
                dishes.append(dish)
        return dishes

    @staticmethod
    def retrieve_dishes_by_id(id):
        """ This retrieve dish must match the id exactly"""
        connection = db.connect(CHOWS_MAIN_DB)
        connection.row_factory = dict_factory
        with connection:
            c = connection.cursor()
            sql_query_string = "SELECT * FROM DISH WHERE ID = ?;"
            c.execute(sql_query_string, (id,))
            row = c.fetchone()
            # Pretty sure there is a way to use the row_factory to contruct a Dish object :thinking:
            dish = Dish(row['ID'], float(row['PRICE']), 1, row['DESCRIPTION'], row['DESCRIPTION_CHINESE'])
            dish.categories = dish.deserialise_categories(row['CATEGORIES'])
        return dish

    @staticmethod
    def retrieve_dishes_by_description(text):
        connection = db.connect(CHOWS_MAIN_DB)
        connection.row_factory = dict_factory
        dishes = []
        with connection:
            c = connection.cursor()
            sql_query_string = "SELECT * FROM DISH WHERE DESCRIPTION LIKE '%'||?||'%'"
            c.execute(sql_query_string, (text,))
            rows = c.fetchall()
            for row in rows:
                dish = Dish(row['ID'], float(row['PRICE']), 1, row['DESCRIPTION'], row['DESCRIPTION_CHINESE'])
                dish.categories = dish.deserialise_categories(row['CATEGORIES'])
                dishes.append(dish)
        return dishes


    @staticmethod
    def create_dish(dish: Dish):
        """ Creates a row if id has not been created."""
        connection = db.connect(CHOWS_MAIN_DB)
        connection.row_factory = dict_factory

        with connection:
            c = connection.cursor()
            try:
                insert_new_dishes = (dish.id, dish.description, dish.description_chinese, dish.unit_price, dish.serialise_categories())
                c.execute("""   INSERT INTO DISH(ID, DESCRIPTION, DESCRIPTION_CHINESE, PRICE, CATEGORIES) 
                                VALUES (?, ?, ?, ?, ?) """, 
                            insert_new_dishes)

            except db.IntegrityError as e:
                raise DuplicateFoodException()
            connection.commit()

    @staticmethod
    def update_dish(dish: Dish):
        """ Creates a row if id has not been created."""
        connection = db.connect(CHOWS_MAIN_DB)
        connection.row_factory = dict_factory

        with connection:
            c = connection.cursor()
            try:
                update_dish_data = (dish.description, dish.description_chinese, dish.unit_price, dish.serialise_categories(), dish.id)
                c.execute("""   UPDATE DISH SET DESCRIPTION = ?, DESCRIPTION_CHINESE = ? , PRICE = ?, CATEGORIES = ? where ID = ?
                                """, 
                            update_dish_data)
            except db.IntegrityError as e:
                raise e
            connection.commit()
            