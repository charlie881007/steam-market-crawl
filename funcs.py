import openpyxl
from datetime import date
import numpy as np
import os

exchange_rate = 4.36
discount_rate = 0.8696


def get_appid(game):
    return {'csgo': 730, 'dota2': 570, 'tf2': 440, 'rust': 252490}[game]


def month_word_to_num(month):
    return {'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12}[month]


def get_search_name(name):
    name.replace('/', '-')
    return name


def write_txt(iterable, save_name):
    first = True
    with open(save_name, 'w', encoding='utf-8') as file:
        for item in iterable:
            if first:
                file.write(f'{item}')
                first = False
            else:
                file.write(f'\n{item}')


def write_excel(game, iterable, file_name):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['物品名稱', 'buff價格', 'steam收購價格', 'steam最低價', '實際折數', '潛在折數', ' ', '網址'])

    try:
        os.mkdir(game)
    except FileExistsError:
        pass

    for item in iterable:
        # if there is demand
        if iterable[item]['steam_demand']:
            buff_price = iterable[item]['buff']
            steam_demand_price = iterable[item]['steam_demand']
            steam_lowest_price = iterable[item]['steam_lowest'] if iterable[item]['steam_lowest'] else '從缺'
            cost = buff_price * exchange_rate
            revenue = steam_demand_price * discount_rate
            potential_revenue = (steam_lowest_price - 0.02) * discount_rate if iterable[item]['steam_lowest'] else '從缺'
            rate = cost / revenue
            potential_rate = cost / potential_revenue if iterable[item]['steam_lowest'] else '從缺'
            steam_url = iterable[item]['steam_url']

            ws.append([item, buff_price, steam_demand_price, steam_lowest_price, rate, potential_rate, ' ', steam_url])

    wb.save(f'{game}/{file_name}.xlsx')
    wb.close()


def convert_date_to_obj(d):
    d = d.split()
    month = month_word_to_num(d[0])
    day = int(d[1])
    year = int(d[2])

    sold_date = date(year, month, day)
    return sold_date


def exclude_outlier(prices):
    q1 = np.quantile(prices, 0.25)
    q3 = np.quantile(prices, 0.75)
    iqr = q3 - q1
    floor = q1 - 1.5*iqr
    ceiling = q3 + 1.5*iqr

    for price in prices:
        if price < floor or price > ceiling:
            prices.remove(price)
    return prices


def convert_headers(temp):
    headers = {}
    for line in temp.split('\n'):
        tokens = line.split(': ')
        key = tokens[0]
        value = tokens[1]
        headers[key] = value
    return headers