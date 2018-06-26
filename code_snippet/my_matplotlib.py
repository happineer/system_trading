import matplotlib.pyplot as plt
from pymongo import MongoClient


def subplot(date, price, vol):
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(date, price)
    plt.subplot(2, 1, 2)
    plt.plot(date, vol)
    plt.show()


def labeling(date, price, vol):
    plt.figure()
    plt.plot(date, price)
    plt.title("LG electronics")
    plt.xlabel("date")
    plt.ylabel("price")
    plt.show()


def main():
    mongo = MongoClient()
    tt_db = mongo.TopTrader
    c_day = tt_db.time_series_day
    lg = c_day.find({'code': '066570'})
    lg_stock = [d for d in lg]
    date = [d['date'] for d in lg_stock]
    price = [d['현재가'] for d in lg_stock]
    vol = [d['거래량'] for d in lg_stock]

    subplot(date, price, vol)
    labeling(date, price, vol)


if __name__ == "__main__":
    main()
