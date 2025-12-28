import frappe

# Calculates the Kilo Rate with Item Rate and Item Base Price Faktor in the Doctyp Item Price
def custom_validate(doc, method):
    if doc.item_code:
        item = frappe.get_doc("Item", doc.item_code)
        if item.custom_base_price_faktor and doc.price_list_rate:
            doc.custom_kilo_rate = doc.price_list_rate * item.custom_base_price_faktor



def update_item_prices_on_factor_change(doc, method):
    """
    Automatically update the field `custom_kilo_rate` in all linked Item Prices
    when the custom_base_price_faktor of the Item has changed.

    Trigger: validate on Item
    """

    # Skip if the factor has not changed
    if not doc.has_value_changed("custom_base_price_faktor"):
        return

    # Get all Item Price records for this item
    item_prices = frappe.get_all(
        "Item Price",
        filters={"item_code": doc.name},
        fields=["name", "price_list_rate"]
    )

    for item_price in item_prices:
        # Only update if price_list_rate is set
        if not item_price.price_list_rate:
            continue

        # Calculate new value
        custom_kilo_rate = item_price.price_list_rate * doc.custom_base_price_faktor

        # Update the custom_kilo_rate field in Item Price
        frappe.db.set_value("Item Price", item_price.name, "custom_kilo_rate", custom_kilo_rate)
