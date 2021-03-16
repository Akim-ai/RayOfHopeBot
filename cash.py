import json
from config import red
import parsing


def get_currency():
    return json.loads(red.get('currency'))


def get_first(id):
    return json.loads(red.get(id))


def get_two_currency(id):
    try:
        print(json.loads(red.get(id)), json.loads(red.get(id+id)))
        return json.loads(red.get(id)), json.loads(red.get(id + id))
    except TypeError:
        pass


def get_second_value(id):
    return json.loads(red.get(id+id))


def get_values_to_print():
    return json.loads(red.get('valuesToPrint'))


def add_currency(currency):
    all_currency = list(json.loads(red.get('currency')))
    for i in all_currency:
        if currency in i:
            return print('iii')
    full_name = parsing.add_currency(currency)
    if full_name:
        to_upload = all_currency
        to_upload.append([currency, full_name])
        print(to_upload)
        red.set('currency', json.dumps(to_upload))
        return 'Succesed'
    else:
        return print('Dont have value like')


def conversion_help(currency, id, step):
    if step:
        red.set(id, json.dumps(currency.replace('&', '/')))
    else:
        red.set(id+id, json.dumps(currency.replace('%', '/')))

