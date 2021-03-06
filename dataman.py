#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from datetime import timedelta
import pymssql
from tools import RandomUtil

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

    def remove_orders(self):
        cursor = self.conn.cursor()

        sql = 'DELETE FROM [%s].[dbo].[Orders]' % (self.opt['db'])

        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def remove_promotions(self):
        cursor = self.conn.cursor()

        sql = 'DELETE FROM [%s].[dbo].[Promotions]' % (self.opt['db'])

        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def reset_product(self, product_id):
        cursor = self.conn.cursor()

        sql = """
        UPDATE [%s].[dbo].[Products]
        SET SaleCounts = 0, Stock = 100
        WHERE ProductId = %d
        """ % (self.opt['db'], product_id)

        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def reset_users(self):
        cursor = self.conn.cursor()

        sql = """
        UPDATE [%s].[dbo].[Users]
        SET OrderNumber = 0, OrderAmount = 0
        """ % (self.opt['db'])

        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def create_promotion(self, promotion_id, product_id, qty, price, start_time, end_time):
        cursor = self.conn.cursor()

        sql = """
        INSERT INTO [%s].[dbo].[Promotions]
        (PromotionId, ProductId, StartTime, EndTime, Quantity, Price)
        VALUES
        (%d, %d, '%s', '%s', %d, %.2f)
        """ % (self.opt['db'],
               promotion_id,
               product_id,
               start_time.strftime('%Y-%m-%d %H:%M:%S'),
               end_time.strftime('%Y-%m-%d %H:%M:%S'),
               qty, price
              )

        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def reset_promotion(self, promotion_id, product_id, qty, price, start_time, end_time):
        cursor = self.conn.cursor()

        sql = """
        UPDATE [%s].[dbo].[Promotions]
        SET ProductId = %d, StartTime = '%s', EndTime = '%s',
        Quantity = %d, Price = %.2f
        WHERE PromotionId = %d
        """ % (self.opt['db'],
               product_id,
               start_time.strftime('%Y-%m-%d %H:%M:%S'),
               end_time.strftime('%Y-%m-%d %H:%M:%S'),
               qty, price,
               promotion_id
              )

        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

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

    def fill_users(self, num):
        cursor = self.conn.cursor()
        rnd = RandomUtil()

        c = 0
        for i in range(num):
            u = {
                'UserId': i + 1,
                'UserName': 'u%d' % (i + 1),
                'RealName': rnd.rand_name(),
                'CellPhone': rnd.rand_mobile(),
                'Address': rnd.rand_address()
            }

            sql = 'INSERT INTO [%s].[dbo].[Users] VALUES (' % self.opt['db']
            sql += "%d, '%s', '%s', '%s', '%s', 0, 0)" % (
                u['UserId'],
                u['UserName'],
                u['RealName'],
                u['CellPhone'],
                u['Address']
            )

            cursor.execute(sql)
            c += 1

            if c == 1000:
                self.conn.commit()
                c = 0

        if c > 0:
            self.conn.commit()

    def fill_products(self, num):
        cursor = self.conn.cursor()
        shenqi = [
            u'东皇钟', u'轩辕剑', u'盘古斧', u'炼妖壶', u'昊天塔',
            u'伏羲琴', u'神农鼎', u'崆峒印', u'昆仑镜', u'女娲石'
        ]

        c = 0
        for i in range(num):
            p = {
                'ProductId': i + 1,
                'ProductName': shenqi[i % len(shenqi)] + str(time.time()),
                'SaleCounts': 0,
                'Stock': 100
            }

            sql = 'INSERT INTO [%s].[dbo].[Products] VALUES (' % self.opt['db']
            sql += "%d, '%s', %d, %d)" % (
                p['ProductId'],
                p['ProductName'],
                p['SaleCounts'],
                p['Stock']
            )

            cursor.execute(sql)
            c += 1

            if c == 1000:
                self.conn.commit()
                c = 0

        if c > 0:
            self.conn.commit()

    def fill_promotions(self, product_id, start, end, qty, price):
        promotions = [
            {
                'PromotionId': 1,
                'ProductId': product_id,
                'StartTime': start,
                'EndTime': end,
                'Quantity': qty,
                'Price': price
            }
        ]

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
