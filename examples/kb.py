# -*- coding: utf-8 -*-

import sys
import os

# add python path (../)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openbank.banks import KB, KBError
from datetime import date
from dateutil.relativedelta import relativedelta
import operator


kb = KB('ACCOUNT', 'PASSOWRD', 'RESIDENT', 'USERNAME')
start_date = date.today() - relativedelta(months=1)  # for 1 month

try:
    transactions = kb.quick_inquiry(start_date=start_date)
except KBError as e:
    print e


def money_per_day():
    data = []  # [date, money]
    for transaction in transactions:
        if len(data) == 0 or data[-1][0] != transaction.date:
            data.append([transaction.date, transaction.withdrawal])
        else:
            data[-1][1] += transaction.withdrawal

    for d in data:
        print d[0], d[1]


def money_per_receiver():
    data = {}  # {receiver: money}
    for transaction in transactions:
        if transaction.receiver is not None:
            money = data.get(transaction.receiver, 0) + transaction.withdrawal
            data[transaction.receiver] = money

    sorted_data = sorted(data.iteritems(), key=operator.itemgetter(1))
    for d in sorted_data:
        print '%7d' % d[1], d[0]


if __name__ == '__main__':
    # money_per_day()
    # money_per_receiver()
    pass
