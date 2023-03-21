import sqlite3
import time


def balance():
    conn = sqlite3.connect('db4.db')
    cur = conn.cursor()
    cur.execute("UPDATE cards_user SET coin = coin + 5") # изменение ячейки coin в cards_user  ---sqlite
    conn.commit()
while True:
    balance()
    time.sleep(3) #time sleep любое время в сек