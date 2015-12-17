#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymssql

class DataMan:
    def __init__(self, opt):
        self.opt = opt

    def open(self):
        server = self.opt['server']
        user = self.opt['user']
        password = self.opt['password']
        db = self.opt['db']

        self.conn = pymssql.connect(server, user, password, db)

    def close(self):
        self.conn.close()

    def clear_all(self):
        cursor = self.conn.cursor()
        tables = [
            'Users', 'Products', 'Promotions', 'Orders'
        ]

        for t in tables:
            cursor.execute(
                'DELETE FROM [%s].[dbo].[%s]' % (self.opt['db'], t)
            )

        self.conn.commit()

    def fill_users(self, users):
        cursor = self.conn.cursor()
        for u in users:
            sql = 'INSERT INTO [%s].[dbo].[Users] VALUES (' % self.opt['db']
            sql += "%d, '%s', '%s', '%s', '%s', 0, 0)" % (
                u['UserId'],
                u['UserName'],
                u['RealName'],
                u['CellPhone'],
                u['Address']
            )

            cursor.execute(sql)

        self.conn.commit();

    def fill_products(self, products):
        cursor = self.conn.cursor()
        for p in products:
            sql = 'INSERT INTO [%s].[dbo].[Products] VALUES (' % self.opt['db']
            sql += "%d, '%s', %d, %d)" % (
                p['ProductId'],
                p['ProductName'],
                p['SaleCounts'],
                p['Stock']
            )

            cursor.execute(sql)

        self.conn.commit();

    def fill_promotions(self, promotions):
        cursor = self.conn.cursor()
        for p in promotions:
            sql = 'INSERT INTO [%s].[dbo].[Promotions] VALUES (' % self.opt['db']
            sql += "%d, %d, '%s', '%s', %d, %f)" % (
                p['PromotionId'],
                p['ProductId'],
                p['StartTime'],
                p['EndTime'],
                p['Quantity'],
                p['Price']
            )

            cursor.execute(sql)

        self.conn.commit();
