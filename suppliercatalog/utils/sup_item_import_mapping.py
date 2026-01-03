FIELD_MAPPING = {
    "name1": "item_name",
    "name2": "custom_item_name_2",
    "tradeclass": "custom_tradeclass",
    "supplierquality": "custom_supplier_quality",
    "weight_shop_unit": "weight_per_unit",
    "orderunit_quantity": "min_order_qty",
    "orderunit": "purchase_uom",
    "base_price_faktor": "custom_base_price_faktor",
    "remaining_shelf_life": "shelf_life_in_days",
    "ernhinweis_vegan": "custom_ernhinweis_vegan",
    "ernhinweis_vegetarisch": "custom_ernhinweis_vegetarisch",
    "ernhinweis_glutenfrei": "custom_ernhinweis_glutenfrei",
    "ernhinweis_laktosefrei": "custom_ernhinweis_laktosefrei",
    "controlagency": "custom_controlagency",
    "description": "description",
    "brand": "custom_brand_suppliercatalog",
    "list_of_ingredients": "custom_list_of_ingredients",
    "item_bio_id": "custom_item_bio_id",
    "weight_item": "custom_weight_item",
    "weight_order_unit": "custom_weight_order_unit",
    "width": "custom_width_shop_unit",
    "height": "custom_height_shop_unit",
    "depth": "custom_depth_shop_unit",
    "content_weight": "custom_weight_content",
    "content_uom": "custom_content_uom",
    "shop_unit_uom": "stock_uom",
    "base_price_unit": "custom_base_price_unit",
    "pfand_typ": "custom_pfand_typ",
    "pfand_ammount": "custom_pfand_ammount",
    "pfand_typ_vpe1": "custom_pfand_typ_vpe1",
    "pfand_ammount_vpe1": "custom_pfand_ammount_vpe1",
    "shop_unit": "custom_shop_unit",
    "country_of_origin": "custom_country_of_production"
}


# ----------------------------------
# Helper Funktion to import only existing Values
# ----------------------------------

def is_empty(value):
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False
