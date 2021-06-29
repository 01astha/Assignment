import logging
from flask import Flask, request

app = Flask(__name__)

@app.route('/orders')
def total_orders():
    items = request.json
    order_items = items.get('order_items')
    distance = items.get('distance')
    offer = items.get('offer', None)
    return get_total(order_items, distance, offer)


"""
This is a distance(km) to cost(INR) mapping. default is for any distance more than 50 
"""
fares = {
    '10': 50,
    '20': 100,
    '50': 500,
    'default': 1000
}

"""
This method calculate the delivery fee (in paisa) based on the input distance
"""
def get_delivery_fee(distance):
    distance_km = distance / 1000
    if distance_km <= 10:
        delivery_fee = fares['10']
    elif distance_km <= 20:
        delivery_fee = fares['20']
    elif distance_km <= 50:
        delivery_fee = fares['50']
    else:
        delivery_fee = fares['default']
    delivery_fee = delivery_fee * 100
    logging.info(f'Delivery fee: {delivery_fee}')
    return delivery_fee


"""
This method calculates the discount to be applied based on the giver Offer_type
"""
def get_discount(offer, delivery_fee):
    offer_val = 0
    if not offer:
        return offer_val
    if offer['offer_type'] == 'FLAT':
        offer_val = offer['offer_val']
    elif offer['offer_type'] == 'DELIVERY':
        offer_val = delivery_fee
    logging.info(f'Total offer: {offer_val}')
    return offer_val


"""
This method validate the item based on Price ,name_length and quantity and returns the required responses with error 
message. Returns None if item is valid else return the Error response.
"""
def validate_item(order_items):
    max_name_length = 20
    max_allowed_quantity = 50
    max_allowed_price = 50000
    status_code = None
    message = None
    if len(order_items['name']) > max_name_length:
        status_code = 413
        message = 'name field too large'
    elif order_items['quantity'] > max_allowed_quantity:
        status_code = 413
        message = 'too many quantity. Max allowed:'+ str(max_allowed_quantity)
    elif order_items['price'] > max_allowed_price:
        status_code = 413
        message = 'too large price. Max allowed:' + str(max_allowed_price)
    response = {'status': status_code, 'message': message}
    return None if status_code is None and message is None else response


"""
This is an utility method to validate the total items in the list and return the response.Returns None if item's list 
is not empty else returns Error message response.
"""
def validate_items_length(items):
    if len(items) == 0:
        return {'status': 411, 'message': 'No items found'}
    return None


def get_total(order_items, distance, offer):
    item_sum = 0
    valid_items = validate_items_length(order_items)
    if valid_items is not None:
        return valid_items
    for item in order_items:
        item_validity = validate_item(item)
        if item_validity is not None:
            return item_validity
        item_sum += item['quantity'] * item['price']
    logging.info(f'Total item sum: {item_sum}')
    delivery_fee = get_delivery_fee(distance)
    discount = get_discount(offer,delivery_fee)
    total = item_sum + delivery_fee
    grand_total = total - min(total, discount)
    return {'order_total': grand_total}


if __name__ == '__main__':
    logging.info('Running the app ...')
    logging.getLogger().setLevel(logging.INFO)
    app.run(host="0.0.0.0", port=8080)
