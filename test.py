import requests
import re
from my_package.Market import *
import sqlite3

cookie = 'ActListPageSize=100; timezoneOffset=28800,0; _ga=GA1.2.1569208104.1566558694; ' \
         'browserid=2261329906651497723; steamMachineAuth76561199101538833=5F0F063A0C5A3D5A74D8A330A4628F9A248B0A75; ' \
         'steamMachineAuth76561198882725636=D5D41D3E937F595E8658460812D89ED5405D17E1; Steam_Language=english; ' \
         'steamMachineAuth76561198127360767=40684852BBD62632B4B6694E7C4EF545931EE719; recentlyVisitedAppHubs=730,' \
         '1150730,570; _gid=GA1.2.2145978931.1626827557; sessionid=9f514fc51363593a7f55be14; ' \
         'steamCountry=TW|034ca398ffc6916747c1ec1c874c4445; ' \
         'steamMachineAuth76561199142450063=ECCEE0392A2B1759CBF74F38612428C85D342619; strInventoryLastContext=753_6; ' \
         'steamLoginSecure=76561198127360767||223E9609E3EADC9C92AE031EAAC0A0898085978A; ' \
         'steamRememberLogin=76561198127360767||973f2693c60d5f196f4768423b65871c; webTradeEligibility={"allowed":1,' \
         '"allowed_at_time":0,"steamguard_required_days":15,"new_device_cooldown_days":7,"time_checked":1626859679}; ' \
         'tsTradeOffersLastRead=1626859926 '

cookie_buff = 'Device-Id=yzaXnFdnQNeqjCExrtg9; _ga=GA1.2.1712764201.1626950100; _gid=GA1.2.1334305556.1627998524; ' \
              'Locale-Supported=zh-Hans; session=1-OCjtugcc-DDgXNgOGxUszFYDZ3RwCJoHjVkSSiTxvY3R2046383888; ' \
              'game=dota2; _gat_gtag_UA_109989484_1=1; ' \
              'csrf_token=IjBlOTk4ZmI4OTVmNmFjODRjZjQ4MTY0ZGYzMjRmMWZmMWJhMzdiOWIi.E-tu9Q.D8oqxtJW2bUbDCNt5zXtmco4frA '

game = 'dota2'
cookie_buff = cookie_buff.replace('zh-Hans', 'en')
market = Market(cookie, cookie_buff)
market.instant_sell(game, 6.51, 9.99)

# 盒子圖
# items = market.get_all_item_names()
# if items:
#     for item in items:
#         if 'Case' in item:
#             item = get_search_name(item)
#             market.get_figure(item)
# else:
#     print('沒抓到任何物品')
# with open('items_csgo.txt', 'r', encoding='utf-8') as file:
#     data = file.read()
#     items = data.split("\n")
#     size = len(items)
#     n = 1
#     for item in items:
#         print(f'{item} {n}/{size}', end='  ')
#         id = market.get_item_id('csgo', item)
#         if id:
#             print('已經在資料庫中了')
#         else:
#             print('加入資料庫...')
#             market.add_item_id('csgo', item)
#
#         n += 1
