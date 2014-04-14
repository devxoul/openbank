# -*- coding: utf-8 -*-
 
from datetime import datetime
import urllib2
from .. import Bank
from .. import Transaction


class KB(Bank):

    #: 계좌번호 ('-' 제외)
    account = None

    #: 계좌 비밀번호 (숫자 4자리)
    password = None

    #: 주민등록번호 끝 7자리
    resident = None

    #: 인터넷 뱅킹 ID (대문자)
    username = None

    def __init__(self, account, password, resident, username):
        self.account = account
        self.password = password
        self.resident = resident
        self.username = username

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value.replace('-', '')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if len(value) != 4 or not value.isdigit():
            raise ValueError(u"password: 비밀번호는 숫자 4자리여야 합니다.")
        self._password = value

    @property
    def resident(self):
        return self._resident

    @resident.setter
    def resident(self, value):
        if len(value) != 7 or not value.isdigit():
            raise ValueError(u"resident: 주민등록번호 끝 7자리를 입력해주세요.")
        self._resident = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value.upper()

    def parse_int(self, formatted_int):
        try:
            return int(formatted_int.replace(',', ''))
        except:
            return 0

    def strip(self, string):
        return string.strip().replace('&nbsp;', '')

    def quick_inquiry_raw(self, start_date=None, end_date=None):
        """국민은행 계좌 빠른조회 raw 데이터
        """

        if start_date is None:
            start_date = datetime.today()

        if end_date is None:
            end_date = datetime.today()

        url = 'https://obank.kbstar.com/quics?asfilecode=524517'
        params = {
            '다음거래년월일키': '',
            '다음거래일련번호키': '',
            '계좌번호': self.account,
            '비밀번호': self.password,
            '조회시작일': start_date.strftime('%Y%m%d'),
            '조회종료일': end_date.strftime('%Y%m%d'),
            '주민사업자번호': '000000' + self.resident,
            '고객식별번호': self.username,
            '응답방법': '2',
            '조회구분': '2',
            'USER_TYPE': '02',
            '_FILE_NAME': 'KB_거래내역빠른조회.html',
            '_LANG_TYPE': 'KOR'
        }

        for k, v in params.iteritems():
            url += '&' + k + '=' + v

        r = urllib2.urlopen(url)
        data = r.read()
        return data

    def quick_inquiry(self, start_date=None, end_date=None):
        """국민은행 계좌 빠른조회. 빠른조회 서비스에 등록이 되어있어야 사용 가능.
        빠른조회 서비스: https://obank.kbstar.com/quics?page=C018920
        """

        transactions = []
        
        html = self.quick_inquiry_raw(start_date, end_date)
        rows = html.split("<tr align='center'>")[1:]
        for row in rows:
            columns = row.split("'>")[1:]
            columns = [self.strip(column.split('<')[0]) for column in columns]

            transaction = Transaction()
            transaction.date = datetime.strptime(columns[0], '%Y.%m.%d').date()
            transaction.description = columns[1]
            transaction.withdrawal = self.parse_int(columns[4])
            transaction.deposit = self.parse_int(columns[5])
            transaction.balance = self.parse_int(columns[6])
            if transaction.withdrawal:
                transaction.receiver = columns[2]
            elif transaction.deposit:
                transaction.sender = columns[2]
            transactions.append(transaction)
        return transactions

    def balance(self):
        html = self.quick_inquiry_raw()
        formatted = html.split("<td class='td' colspan='3'>")[2].split("<")[0]
        balance = self.parse_int(formatted)
        return balance
