import requests
from .funcs import *
import urllib
from datetime import date
import math
import os
import sqlite3
import re
import time

pause_sec = 120
interval = 0.01


class Market:

    def __init__(self, cookie, cookie_buff):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.182 Safari/537.36'}
        self.headers_buff = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.182 Safari/537.36'}

        self.headers['Cookie'] = cookie
        self.headers_buff['Cookie'] = cookie_buff

        self.conn = sqlite3.connect('steam.db')
        self.c = self.conn.cursor()

    def get_all_item_names(self):
        # 請求網址
        url = 'https://steamcommunity.com/market/search/render/'
        params = {'start': 0,
                  'count': 100,
                  'search_descriptions': 0,
                  'sort_column': 'popular',
                  'sort_dir': 'desc',
                  'appid': 730,
                  'category_730_ItemSet[]': 'any',
                  'category_730_ProPlayer[]': 'any',
                  'category_730_StickerCapsule[]': 'any',
                  'category_730_TournamentTeam[]': 'any',
                  'category_730_Weapon[]': 'any',
                  # [tag_CSGO_Type_WeaponCase, tag_CSGO_Tool_Sticker]
                  'category_730_Type[]': ['tag_CSGO_Type_WeaponCase'],
                  'norender': 1,
                  'query': ''
                  }

        # 測試能不能連線steam伺服器
        try:
            res = requests.get(url, headers=self.headers, params=params, timeout=10)
            if res.status_code != 200:
                print('無法與steam伺服器連線')
                return None

            # 檢查json請求是否成功
            res = res.json()
            if res['success'] is not True:
                print('無法取得json')
                return None

            # 商品總數
            total_item = res['total_count']

            # 寫入物品名稱的檔案
            file = open('items.txt', 'w', encoding='utf-8')

            item_list = []
            for i in range(0, total_item, 100):
                params['start'] = i
                res = requests.get(url, headers=self.headers, params=params, timeout=10)

                # 檢查response
                if res.status_code == 200:
                    res = res.json()
                    # 一切成功
                    if res['success'] is True:
                        print(f'進度：{i + 1}/{total_item}')
                        items = res['results']
                        for item in items:
                            item_name = item['name']
                            item_list.append(item_name)
                            if i == 0 and items[0]['name'] == item_name:
                                file.write(item_name)
                            else:
                                file.write('\n' + item_name)

                    # json 請求失敗
                    else:
                        print('json請求失敗')
                        break

                # status code 不是 200
                else:
                    print('status_code不是200')
                    break

            # 物品寫入完成，關閉檔案
            file.close()
            return item_list
        except Exception as e:
            print(e)


    def get_low_price_items(self, percent=15, period=99999):
        # 確保items.txt存在
        try:
            with open('items.txt', 'r', encoding='utf-8') as file:
                pass
        except FileNotFoundError:
            self.get_all_item_names()

        # 開啟 items.txt
        file_all_items = open('items.txt', 'r', encoding='utf-8')
        items = file_all_items.read().split('\n')
        item_count = len(items)

        # 請求目標與參數
        url = 'https://steamcommunity.com/market/pricehistory/'
        params = {'currency': 30,
                  'appid': 730
                  }

        today = date.today()
        file_target_items = open('low_price_items.txt', 'w', encoding='utf-8')

        first_item = True

        n = 1
        for item in items:
            print(f'{n}/{item_count}')
            n += 1
            params['market_hash_name'] = item
            res = requests.get(url, headers=self.headers, params=params, timeout=10)
            if res.status_code == 200:
                res = res.json()
                if res['success'] is True:
                    prices = res['prices']
                    total_sales = 0
                    total_revenue = 0
                    current_day = 0
                    sale_prices = []
                    for price_data in prices:
                        date_data = price_data[0]
                        date_data = date_data.split()
                        year = int(date_data[2])
                        month = month_word_to_num(date_data[0])
                        day = int(date_data[1])
                        history_date = date(year, month, day)

                        # 期間內的銷售
                        if (today - history_date).days <= period:
                            # 換日
                            if day != current_day and current_day != 0:
                                avg_price = total_revenue / total_sales if total_sales != 0 else 0
                                sale_prices.append(avg_price)
                                total_sales = 0
                                total_revenue = 0

                            else:
                                current_day = day

                            sales = int(price_data[2])
                            price = price_data[1]
                            total_sales += int(sales)
                            total_revenue += sales * price

                    # 如果期限內有紀錄 且 算熱門
                    if sale_prices and total_sales >= 5:
                        latest_price = sale_prices[-1]
                        sale_prices.sort()
                        size = len(sale_prices)
                        for i in range(size):
                            if sale_prices[i] >= latest_price:
                                pr = i / size
                                break

                        if pr <= percent / 100:
                            if first_item:
                                file_target_items.write(f'{item}  {latest_price:.2f}  {pr}')
                                first_item = False
                            else:
                                file_target_items.write(f'\n{item}  {latest_price:.2f}  {pr}')

                else:
                    time.sleep(pause_sec)
                    print('無法取得json')

            else:
                print('無法與伺服器連線')

        file_all_items.close()


    def get_buff_price(self, game, min_price, max_price):
        # 取得buff商品價格
        url_buff = 'https://buff.163.com/api/market/goods'

        params_buff = {
            'game': game,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': 'price.desc',
            '_': '1613411118154',
        }

        price_table = {}

        for page in range(1, 999):
            print(f'BUFF請求到第{page}頁')
            params_buff['page_num'] = page

            try:
                res = requests.get(url_buff, params=params_buff, headers=self.headers_buff, timeout=10)

                if res.status_code == 200:
                    # 網頁成功載入
                    res = res.json()
                    if res['code'] == 'OK':
                        # json請求成功
                        data = res['data']['items']
                        total_goods_on_page = len(data)

                        # 更新buff價格到price_table
                        repeat = 0
                        for item in data:
                            price_buff = float(item['sell_min_price'])
                            print(price_buff)
                            item_name = item['name']

                            # 計算該頁有幾個商品重複
                            if item_name not in price_table:
                                price_table[item_name] = {}
                                price_table[item_name]['buff'] = price_buff
                                price_table[item_name]['steam_demand'] = 0
                                price_table[item_name]['steam_lowest'] = 0
                                price_table[item_name]['steam_url'] = ''
                            else:
                                repeat += 1

                        # 如果該頁商品重複過多，代表已到頁面上限
                        if repeat >= (total_goods_on_page * 0.8):
                            break
                    else:
                        # json請求失敗
                        print('buff的json沒有請求到')

            except:
                print('網路掛了')
                time.sleep(pause_sec)
        return price_table

    def get_demand_and_lowest_price(self, id):
        url_for_demand_price = 'https://steamcommunity.com/market/itemordershistogram'
        params_for_demand_price = {'country': 'TW', 'language': 'english', 'currency': 30, 'two_factor': 0,
                                   'item_nameid': id}
        sell_price = 0
        demand_price = 0
        status = 0

        try:
            res = requests.get(url_for_demand_price, headers=self.headers, params=params_for_demand_price, timeout=10)
            url = res.url

            if res.status_code == 200:
                data = res.json()
                if data['success'] == 1:
                    buy_order = data['highest_buy_order']
                    sell_table = data['sell_order_table']

                    # 試圖找到販賣價格
                    match = re.search(r'Quantity<\/th><\/tr><tr><td align=\"right\" class=\"\">NT\$ (?P<price>\d+.\d+)', sell_table)
                    if match:
                        sell_price = match['price']
                        while ',' in sell_price:
                            sell_price = sell_price.replace(',', '')
                        sell_price = float(sell_price)

                    # 試圖找到求購價格
                    if buy_order:
                        demand_price = int(buy_order) / 100
                    else:
                        print('太冷門啦，沒有人求購')

                else:
                    print(f'網址錯誤 網址: {url}')

            elif res.status_code == 429:
                print('訪問太多次了')
                status = -1
            elif res.status_code == 400:
                print(f'伺服器不知道怎麼回應 網址: {res.url}')
            elif res.status_code == 500:
                print('伺服器遭遇未知錯誤')
                status = 0
            elif res.status_code == 502:
                status = 0
            else:
                print(f'伺服器掛了 status: {res.status_code} 網址: {url}')
                status = -1
        except Exception as e:
            print(f'發生錯誤: {e}')
            print('網路掛了')
            time.sleep(pause_sec)

        return status, demand_price, sell_price

    def add_item_id(self, game, item):
        # '/'轉換成'-' 才是正確的url
        item_name_for_search = get_search_name(item)

        app_id = get_appid(game)
        url_for_getting_id = f'https://steamcommunity.com/market/listings/{app_id}/{item_name_for_search} '

        pattern = r'Market_LoadOrderSpread\( (?P<item_id>\d+) \)'
        pattern = re.compile(pattern)

        try:
            res = requests.get(url_for_getting_id, headers=self.headers, timeout=10)
            if res.status_code == 200:

                match = pattern.search(res.text)
                if match:
                    id = match['item_id']

                    self.c.execute(f'INSERT INTO {game}_item_id VALUES (?, ?)', (item, id,))
                    self.conn.commit()

                    print('新增成功! ! !')

                    return id

                else:
                    print(f'沒有人販賣這個物品 網址: {res.url}')
                    return 0

            elif res.status_code == 429:
                print('訪問太多次了')
                return -1
            elif res.status_code == 500:
                print('伺服器遭遇未知錯誤')
                return 0
            elif res.status_code == 502:
                return 0
            else:
                print(f'伺服器掛了 status: {res.status_code} 網址: {res.url}')
                return -1
        except Exception as e:
            print(e)
            time.sleep(pause_sec)
            return 0

    def get_item_id(self, game, name):
        self.c.execute(f'SELECT id from {game}_item_id where name = ?', (name,))
        id = self.c.fetchone()
        return id

    def instant_sell(self, game, min_price, max_price):
        price_table = self.get_buff_price(game, min_price, max_price)


        item_counter = len(price_table)
        print(f'總件數{item_counter}')

        n = 1
        # 查詢steam收購價格
        for item in price_table:
            item_name_in_url = get_search_name(item)
            price_table[item]['steam_url'] = f'https://steamcommunity.com/market/listings/{get_appid(game)}/{item_name_in_url}'

            print(f'{n:4}/{item_counter}   ${price_table[item]["buff"]:.2f}', end='   ')
            n += 1

            id = self.get_item_id(game, item)

            # 資料庫裡已經有物品ID
            if id:
                print('YES')
                id = id[0]

                # 對求購價格請求
                status, demand_price, lowest_price = self.get_demand_and_lowest_price(id)

                # steam不給請求求購
                if status == -1:
                    break

                # 請求完成
                else:
                    price_table[item]['steam_demand'] = demand_price
                    price_table[item]['steam_lowest'] = lowest_price

            # 資料庫沒有物品ID
            else:
                print('NO')
                id = self.add_item_id(game, item)

                if id == 0:
                    # still cant get id (due to no one sell this on market)
                    pass
                elif id == -1:
                    # steam拒絕請求id
                    break
                else:
                    # 成功對steam請求ID
                    # 對求購價格請求
                    status, demand_price, lowest_price = self.get_demand_and_lowest_price(id)

                    # steam不給請求求購
                    if status == -1:
                        break

                    # 請求完成
                    else:
                        price_table[item]['steam_demand'] = demand_price
                        price_table[item]['steam_lowest'] = lowest_price

        write_excel(game, price_table, f'{game}_快速轉賣_{min_price}_to_{max_price}')
        self.conn.close()

    def get_history(self, game, item, days):
        url = 'https://steamcommunity.com/market/pricehistory/'

        params = {'country': 'TW', 'currency': 30, 'appid': get_appid(game)}
        item = get_search_name(item)
        params['market_hash_name'] = item

        try:
            res = requests.get(url, headers=self.headers, params=params, timeout=10)
            if res.status_code == 200:
                # 伺服器正常且允許存取
                data = res.json()

                today = date.today()
                prices = []

                if data['success']:
                    sale_data_all = data['prices']
                    print('steam網頁讀取成功')

                    for sale_data in sale_data_all:
                        sold_day = convert_date_to_obj(sale_data[0])
                        if (today - sold_day).days <= days:
                            price = sale_data[1]
                            volume = int(sale_data[2])
                            price = [price] * volume

                            prices.extend(price)

                    return 0, prices


                else:
                    print(f'json請求失敗 網址: {res.url}')
                    return 0, []

            elif res.status_code == 429:
                print('存取太多次了')
                return -1, []

            elif res.status_code == 500:
                print(f'{res.status_code} 網址: {res.url}')
                return 0, []

            else:
                print(f'伺服器報了  {res.status_code} {res.url}')
                return -1, []

        except Exception as e:
            # 所有跟連線有關的錯誤
            print(e)
            time.sleep(pause_sec)
            return 0, []

    def get_lowest_price(self, game, item):
        url = 'https://steamcommunity.com/market/itemordershistogram'

        params = {'country': 'TW', 'language':'english', 'currency': 30, 'two_factor': 0}
        id = self.get_item_id(game, item)

        if id is None:
            id = self.add_item_id(game, item)

        # 伺服器封鎖我
        if id == -1:
            return -1

        # 找不到物品ID(可能沒有人販賣)
        elif id == 0:
            return 0

        else:
            params['item_nameid'] = id
            try:
                res = requests.get(url, headers=self.headers, params=params, timeout=10)
                if res.status_code == 200:
                    # 伺服器正常且允許存取
                    data = res.json()

                    if data['success'] == 1:

                        price = data['lowest_sell_order']

                        if not price:
                            return 0

                        return int(price)

                        # table = data['sell_order_table']
                        #
                        #
                        # if table:
                        #     match = re.search(r'Quantity<\/th><\/tr><tr><td align=\"right\" class=\"\">NT\$ (?P<price>\d+.\d+|\d+)', table)
                        #     print(res.url)
                        #
                        #     # 找到販賣價格
                        #     if match:
                        #         price = match['price']
                        #
                        #         while ',' in price:
                        #             price = price.replace(',', '')
                        #
                        #         return float(price) if price else 0
                        #
                        #     # 請求的業面中找不到販賣價格
                        #     else:
                        #         print('re找不到販賣價格')
                        #         return 0
                        #
                        # else:
                        #     print('找不到販賣價格table')
                        #     return 0

                    else:
                        print(f'json請求失敗 網址: {res.url}')
                        return 0

                elif res.status_code == 429:
                    print('存取太多次了')
                    return -1

                elif res.status_code == 500:
                    print(f'{res.status_code} 網址: {res.url}')
                    return 0

                else:
                    print(f'伺服器報了  {res.status_code} {res.url}')
                    return -1

            except FileExistsError:
                time.sleep(pause_sec)
                return 0




    def normanl_sell(self, game, min_price, max_price):
        price_table = self.get_buff_price(game, min_price, max_price)

        total_item = len(price_table)
        counter = 1
        for item in price_table:
            item_name_in_url = get_search_name(item)
            price_table[item]['steam_url'] = f'https://steamcommunity.com/market/listings/{get_appid(game)}/{item_name_in_url}'

            print(f'{counter}/{total_item}', end=' ')
            counter += 1
            price = self.get_lowest_price(game, item)
            if price == -1:
                break
            else:
                # 可以繼續寫入
                # 先檢查有沒有抓到價格
                if price:
                    # 更新
                    price_table[item]['steam'] = price
                    print('成功')
                else:
                    print('沒抓到價格')


        write_excel(game, price_table, f'普通轉賣_{game}_{min_price}_to_{max_price}')

    def get_item_name(self, game, id):
        name = self.c.execute(f'SELECT name FROM {game}_item_id WHERE id = ?', (id, )).fetchone()
        return name
