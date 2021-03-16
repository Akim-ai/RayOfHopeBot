import requests  # импортируем наш знакомый модуль
import lxml.html
import cash
from lxml import etree
import json


def add_currency(currency):
    try:
        return lxml.html.document_fromstring(requests.get('https://pokur.su/usd/' + currency + '/1/').text)\
            .xpath('/html/body/div[1]/div/div[2]/div[6]/table/thead/tr/th[3]/text()')[0]
    except IndexError:
        return


def get_price(first_currency, second_currency, amount):
    return lxml.html.document_fromstring(requests.get('https://pokur.su/' + first_currency + '/' + second_currency
                                                      + '/' + str(amount) + '/').text)\
            .xpath('/html/body/div[1]/div/div[2]/article/header/div/div[1]/div/div/p/span[2]/text()')


def get_values(currency):
    list_of_currency = []
    for i in cash.get_currency():
        if currency != i[0]:
            list_of_currency.append([lxml.html.document_fromstring(requests.get('https://pokur.su/' + currency + '/'
                                                                            + i[0] + '/1/').text)
                                .xpath('/html/body/div[1]/div/div[2]/article/header/div/div[1]/div/div/p/span[2]'
                                       '/text()')[0], i[1]])
    return list_of_currency
