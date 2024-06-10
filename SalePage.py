from bs4 import BeautifulSoup
from SaleEntry import SaleEntry
import datetime
import time as t

class SalePage:
    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.out_of_date = False

    def isEmpty(self):
        result = self.soup.select_one('.nodata')
        if result is None:
            return False
        return True


    def getSaleEntries(self, begin, end):
        sell_entries = []

        rows = self.soup.select('.list_tb_csgo > tr')
        for row in rows:
            status = row.select('p')[-1].decode_contents()
            if ('出售成功' not in status) and ('供应成功' not in status):
                continue

            name = row.select_one('.textOne').decode_contents()

            price = 0

            temp = row.select_one('.f_Strong').decode_contents()
            if temp:
                if '<small>' in temp:
                    temp = temp.split('<small>')[0]
                price += float(str(temp).replace('¥ ', ''))

            temp = row.select_one('small')
            if temp:
                temp = temp.decode_contents()
                price += (float(str(temp).replace('.', '')) / 100)

            time_raw = row.select_one('.c_Gray.t_Left').decode_contents()

            date = time_raw.split(' ')[0]
            tokens = date.split('-')
            date = datetime.date(int(tokens[0]), int(tokens[1]), int(tokens[2]))

            time = time_raw.split(' ')[1]
            tokens = time.split(':')
            time = datetime.time(int(tokens[0]), int(tokens[1]), int(tokens[2]))

            if begin <= date < end:
                entry = SaleEntry(name, price, date, time)
                sell_entries.append(entry)

            if date < begin:
                self.out_of_date = True

        return sell_entries
