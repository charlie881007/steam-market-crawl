class SaleEntry:
    def __init__(self, name, price, date, time):
        self.name = name
        self.price = price
        self.date = date
        self.time = time

    def __str__(self):
        return f'{self.name} {self.price} {self.date} {self.time}'

    def to_iterable(self):
        return [self.name, self.price, self.date, self.time]