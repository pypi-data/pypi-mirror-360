from enum import Enum

class DummyNames(Enum):
    DUMMY_PRODUCT = "dummy_product"
    DUMMY_CATEGORY_LEVEL = "dummy_category_level"
    DUMMY_CATEGORY = "dummy_category"
    DUMMY_STORE = "dummy_store"

class FlagLevels(Enum):
    MISSING_VALUE = "missing_value"
    NOT_FOR_SALE = "not_for_sale"
    OUT_OF_STOCK = "out_of_stock"
 