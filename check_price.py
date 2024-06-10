import requests
import re
from my_package.Market import Market
from my_package.funcs import *
import time
import math
import html
from bs4 import BeautifulSoup


balance_rate = 0.75
balance_rate_expire = 0.8

white_list = ['Genuine Promo Burning Iron',
              'Genuine Eternal Barding of the Chaos Chosen',
              'Spectrum 2 Case',
             ]

# headers模板
headers_general = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}

# 請求市集清單的cookie
cookie_steam = 'ActListPageSize=100; Steam_Language=english; browserid=2438133063309690348; timezoneOffset=28800,' \
               '0; _ga=GA1.2.1906543814.1638847527; ' \
               'steamMachineAuth76561199215895350=9C3C1F53C54BA432409211699A3BAF8AE0433EB2; steamCurrencyId=30; ' \
               'steamRememberLogin=76561199215895350||78fbf14d7d819f27b583365b55cc5467; ' \
               '_gid=GA1.2.318615881.1647771301; steamCountry=TW|a0f1a9a6c762944d9450f2d82661565b; ' \
               'sessionid=daf88cd09f57671fcde22a63; webTradeEligibility={"allowed":1,"allowed_at_time":0,' \
               '"steamguard_required_days":15,"new_device_cooldown_days":7,"time_checked":1647922166}; ' \
               'tsTradeOffersLastRead=1647451528; ' \
               'steamLoginSecure=76561199215895350||3BF1485F60D7E9F866C8BC11EFE1892E8DB58598; _gat=1 '

# 請求下架的headers
temp = """Accept: text/javascript, text/html, application/xml, text/xml, */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
Connection: keep-alive
Content-Length: 34
Content-type: application/x-www-form-urlencoded; charset=UTF-8
Cookie: ActListPageSize=10; Steam_Language=english; browserid=2438133063309690348; timezoneOffset=28800,0; _ga=GA1.2.1906543814.1638847527; steamMachineAuth76561199215895350=9C3C1F53C54BA432409211699A3BAF8AE0433EB2; steamCurrencyId=30; steamRememberLogin=76561199215895350%7C%7C78fbf14d7d819f27b583365b55cc5467; _gid=GA1.2.318615881.1647771301; steamCountry=TW%7Ca0f1a9a6c762944d9450f2d82661565b; sessionid=daf88cd09f57671fcde22a63; webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A7%2C%22time_checked%22%3A1647922166%7D; tsTradeOffersLastRead=1647451528; steamLoginSecure=76561199215895350%7C%7C3BF1485F60D7E9F866C8BC11EFE1892E8DB58598; _gat=1
Host: steamcommunity.com
Origin: https://steamcommunity.com
Referer: https://steamcommunity.com/market/
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36
X-Prototype-Version: 1.7
X-Requested-With: XMLHttpRequest"""
headers_for_remove = dict((key, value) for key, value in (pair.split(': ') for pair in temp.split('\n')))
session_id = re.search('sessionid=([^;]+)', temp).group(1)
data = {'sessionid': session_id}

# 請求buff的headers
temp = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
Connection: keep-alive
Cookie: Device-Id=pjnWvM1ryqtXoR96S42T; _ga=GA1.2.1294642150.1638847524; P_INFO=886-978550552|1642575034|1|netease_buff|00&99|null&null&null#taiwan&710000#10#0|&0||886-978550552; _gid=GA1.2.826822315.1648175896; Locale-Supported=zh-Hans; session=1-ZmdBGhFe9qUqKTibGfjRuYB4OqyUpwvmeYr72FUYgTwx2042474895; _gat_gtag_UA_109989484_1=1; csrf_token=ImE5ZGE0NmViMDAwOTQ3Mzc4OGMzM2QyNzM1NGY2NzkwY2I1OWNkMTEi.FR7U-A.L3SjxfDnYhICTpqWyZoiCMBfdas; game=dota2
Host: buff.163.com
Referer: https://buff.163.com/market/csgo
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"""

temp = temp.replace('zh-Hans', 'en')
headers_for_buff = dict((key, value) for key, value in (pair.split(': ') for pair in temp.split('\n')))
cookie_buff = re.search('Cookie: .*', temp).group()

# 把cookie放進headers模板
headers_general['Cookie'] = cookie_steam

# 請求市集清單的網址
url_for_listing = 'https://steamcommunity.com/market/'

payload = {'query': '', 'start': 10, 'count': 100}

game = 'dota2'
market = Market(cookie_steam, cookie_buff)


def check_shelf():
    # 用來儲存哪些東西在架上
    on_sale_items = []

    # 用來儲存物品跟最低價
    price_table = {}

    try:
        # 把高過最低價的東西都拉下來

        # 把cookie放進headers模板
        headers_general['Cookie'] = cookie_steam

        # 取得物品清單
        res = requests.get(url_for_listing, headers=headers_general, timeout=60)
        item_blocks = re.findall(
            '<div class="market_listing_row market_recent_listing_row listing_[\s\S]*?<div style="clear: both"></div>\r\s*</div>',
            res.text)
        print(f'總件數: {len(item_blocks)}')

        # 對每個物品清查
        for item_block in item_blocks:
            # 先抓物品的名稱
            name = re.search(r'<a class="market_listing_item_name_link" href=".+">(?P<name>.*)</a>', item_block)['name']

            # 再抓物品的上架編號
            listing_id = \
                re.search(r'<div class="market_listing_row market_recent_listing_row listing_(?P<listing_id>\d+)',
                          item_block)['listing_id']

            # 再抓物品的上架價格
            my_price = float(
                re.search(r'<span title="This is the price the buyer pays\.">\r\s*NT\$ (?P<my_price>(\d+\.\d+)|(\d+))',
                          item_block)['my_price'])

            # 取得目前的最低價
            lowest_price = market.get_lowest_price(game, name)
            price_table[name] = lowest_price

            # 如果我的價錢比最低價還低，就把物品拉下來
            if my_price > lowest_price:
                # 請求下架的網址
                url_for_remove = 'https://steamcommunity.com/market/removelisting/'
                url_for_remove += listing_id
                requests.post(url_for_remove, headers=headers_for_remove, data=data)

            # 我的東西是最低價
            else:
                on_sale_items.append(name)


    except Exception as e:
        # 把所有錯誤都吃掉
        if e == requests.Timeout:
            print('steam炸了')
            time.sleep(300)
            pass
        else:
            print(f'錯誤種類: {e}')

    return on_sale_items, price_table


def clear_shelf():
    # 用來儲存哪些東西在架上
    on_sale_items = []

    # 用來儲存物品跟最低價
    price_table = {}

    try:
        # 把高過最低價的東西都拉下來

        # 取得物品清單
        res = requests.get(url_for_listing, headers=headers_general, timeout=60)
        item_blocks = re.findall(
            '<div class="market_listing_row market_recent_listing_row listing_[\s\S]*?<div style="clear: both"></div>\r\s*</div>',
            res.text)
        print(f'總件數: {len(item_blocks)}')

        # 對每個物品清查
        for item_block in item_blocks:

            # 再抓物品的上架編號
            listing_id = \
                re.search(r'<div class="market_listing_row market_recent_listing_row listing_(?P<listing_id>\d+)',
                          item_block)['listing_id']

            # 再抓物品的名稱
            name = re.search(r'<a class="market_listing_item_name_link" href=".+">(?P<name>.*)</a>', item_block)['name']

            # 如果物品在白名單內，不要下架
            if name in white_list or ' | ' in name:
                continue

            # 請求下架
            url_for_remove = 'https://steamcommunity.com/market/removelisting/'
            url_for_remove += listing_id
            requests.post(url_for_remove, headers=headers_for_remove, data=data)

    except Exception as e:
        # 把所有錯誤都吃掉
        if e == requests.Timeout:
            print('steam炸了')
            time.sleep(300)
            pass
        else:
            print(f'錯誤種類: {e}')

    return on_sale_items, price_table


def get_cost(game, item):
    url_for_cost = f'https://buff.163.com/market/buy_order/history'
    params = {'game': game, 'search': item, 'page_num': 1}
    try:
        while True:
            res = requests.get(url_for_cost, headers=headers_for_buff, params=params)

            orders = re.findall('<tr id="bill_order_[\s\S]*?(?=(?:<tr id="bill_order_|</table>))', res.text)

            if orders:
                for order in orders:
                    order_name = re.search('<span class="textOne">(.*?)</span>', order)
                    if order_name:
                        order_name = html.unescape(order_name.group(1))
                        if order_name == item.replace('  ', ' '):
                            big = re.search('<strong class="f_Strong">¥ (?P<big>\d+)', order)
                            small = re.search('<small>\.(?P<small>\d+)', order)

                            if big and small:
                                total = float(big['big'] + '.' + small['small'])
                                return total
                            elif big:
                                big = int(big['big'])
                                total = big
                                return total
                            else:
                                pass
                params['page_num'] += 1
            else:
                break
    except Exception as e:
        print('buff連線錯誤')
        print(e)
        return 0

    return 0


def put_on_sell(onshelf, price_table):
    res = requests.get(
        f'http://steamcommunity.com/inventory/76561199215895350/{get_appid(game)}/2?l=english&count=5000',
        headers=headers_for_remove)
    res_json = res.json()

    url_for_sale = 'https://steamcommunity.com/market/sellitem/'
    temp = """Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
Connection: keep-alive
Content-Length: 98
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Cookie: ActListPageSize=10; Steam_Language=english; browserid=2438133063309690348; timezoneOffset=28800,0; _ga=GA1.2.1906543814.1638847527; steamMachineAuth76561199215895350=9C3C1F53C54BA432409211699A3BAF8AE0433EB2; steamCurrencyId=30; steamRememberLogin=76561199215895350%7C%7C78fbf14d7d819f27b583365b55cc5467; _gid=GA1.2.318615881.1647771301; steamCountry=TW%7Ca0f1a9a6c762944d9450f2d82661565b; sessionid=daf88cd09f57671fcde22a63; webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A7%2C%22time_checked%22%3A1647922166%7D; tsTradeOffersLastRead=1647451528; steamLoginSecure=76561199215895350%7C%7C3BF1485F60D7E9F866C8BC11EFE1892E8DB58598; strInventoryLastContext=570_2; _gat=1
Host: steamcommunity.com
Origin: https://steamcommunity.com
Referer: https://steamcommunity.com/profiles/76561199215895350/inventory/
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"""
    session_id = re.search('sessionid=([^;]+)', temp).group(1)

    headers_for_sale = dict((key, value) for key, value in (header.split(': ') for header in temp.split('\n')))
    data_for_sale = {'sessionid': session_id, 'appid': get_appid(game), 'contextid': 2}

    if res_json.get('assets', 0):

        assets = res_json['assets']
        descriptions = res_json['descriptions']

        cost_table = {}

        for asset in assets:

            asset_id = asset['assetid']
            class_id = asset['classid']
            instance_id = asset['instanceid']

            name = ''
            is_expire = False
            for description in descriptions:
                if description['instanceid'] == instance_id and description['classid'] == class_id:
                    name = description['market_name']
                    if description['tradable']:
                        is_expire = True

            if not name:
                continue

            cost_table[name] = {'cost': 0, 'expire': is_expire}

            cost_as_tw = cost_table[name].get('cost', 0)
            if not cost_as_tw:
                cost_as_tw = get_cost(game, name) * exchange_rate
                cost_table[name]['cost'] = cost_as_tw

            if cost_as_tw:

                current_lowest = price_table.get(name)

                if not current_lowest:
                    current_lowest = market.get_lowest_price(game, name)

                if not current_lowest:
                    print('抓不到steam最低價')
                    continue

                # 放超過7天
                floor_balance_rate = balance_rate
                if is_expire:
                    floor_balance_rate = balance_rate_expire

                pricing1 = math.floor((current_lowest - 1) / 1.15) if name not in onshelf else math.floor(
                    current_lowest / 1.15)
                pricing2 = math.floor(cost_as_tw / floor_balance_rate * 100)

                price = pricing1 if pricing1 >= pricing2 else pricing2


                method = f'壓價錢({cost_as_tw * 100 / price * 100 :.2f}折)' if pricing1 >= pricing2 else f'底價({int(floor_balance_rate * 100)}折)'

                print(f'{name:45s}  方法: {method:45s}  超過7天: {is_expire}   鴨價格:{pricing1}    底價:{pricing2}   成本:{cost_as_tw/exchange_rate}')

            else:
                print(f'{name} 抓不到成本')
                continue

            data_for_sale['assetid'] = asset_id
            data_for_sale['amount'] = 1
            data_for_sale['price'] = price

            if price == pricing2:
                continue

            on_sell_res = requests.post(url_for_sale, headers=headers_for_sale, data=data_for_sale)
            print(on_sell_res.text)



        # 驗證價格
        print('確認價格')

        res = requests.get(url_for_listing, headers=headers_general, timeout=60)

        soup = BeautifulSoup(res.text, 'html.parser')
        confirming_items = soup.select('div[class*="market_listing_row market_recent_listing_row listing_"]')


        for item in confirming_items:
            name = item.select_one('a[class="market_listing_item_name_link"]').text
            cost_as_tw = cost_table.get(name, {}).get('cost', 0)

            if not cost_as_tw:
                print(f'{name:60s}找不到購買成本')

            else:
                revenue = float(re.search(r'\(NT\$ (.+)\)',
                                    item.select_one('span[title="This is how much you will receive."]').text.strip()).group(1).replace(',', ''))

                rate = cost_as_tw / revenue

                is_expire = True if cost_table[name]['expire'] else False
                is_valid = False
                if is_expire:
                    if rate <= (balance_rate_expire + 0.01):
                        is_valid = True
                else:
                    if rate <= (balance_rate + 0.01):
                        is_valid = True

                print(f'{name:60s}比率:{rate*100:.2f}        過期: {is_expire}        合格: {is_valid}')

    else:
        print('物品庫空的')

on_market = []
price_table = {}

#
# clear_shelf()
clear_shelf()
put_on_sell(on_market, price_table)


