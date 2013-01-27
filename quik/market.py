# -*- coding: utf-8 -*-
import datetime
import logging
from quik import Quik
from trading import market
from trading.order import Order, BUY, SELL, EXECUTED, ACTIVE, KILLED

    
log = logging.getLogger('qmarket')

ORDER_OP = {u"Купля":BUY,u"Продажа":SELL}

class QuikMarket(market.Market):

    def __init__(self, path, dde):
        market.Market.__init__(self)

        self.conn = Quik( path, dde )
        self.bid = {}
        self.ask = {}
        self.conn.subscribe( "TICKERS", {
            "seccode":u"Код бумаги",
            "classcode":u"Код класса",
            "price":u"Цена послед."
        }, self.ontick )

        self.conn.subscribe( "ORDERS", {
            "order_key":u"Номер",
            "seccode":u"Код бумаги",
            "operation":u"Операция",
            "price":u"Цена",
            "quantity":u"Кол-во",
            "left":u"Остаток",
            "state":u"Состояние"
        }, self.onorder )

        self.conn.subscribe( "BOOK", {
            "price":u"Цена",
            "ask":u"Покупка",
            "bid":u"Продажа"
        }, self.onbook, self.onbookready )

    def onbookready(self,tool):
        ticker = self.ticker( tool )
        ticker.book( self.bid, self.ask )
        self.bid = {}
        self.ask = {}

    def onbook(self,data):
        if data["bid"]:
            self.bid[ data["price"] ] = data["bid"]
        if data["ask"]:
            self.ask[ data["price"] ] = data["ask"]
 
    def ontick(self,data):
        """ Quik tickers data handler """
        ticker = self.ticker( data["seccode"] )
        ticker.classcode = data["classcode"]
        ticker.time = datetime.datetime.now()
        ticker.price = data["price"]
        ticker.volume = 0
        self.tick(ticker)

    def onorder(self,data):
        state = data["state"]
        ticker = self.__getitem__( data["seccode"] )
        order = ticker.order( int( data["order_key"] ) )
        old_status = order.status
        order.operation = ORDER_OP[ data["operation"] ]
        order.price = float( data["price"] )
        order.quantity = int( data["quantity"] )
        order.quantity_left = int( data["left"] )
        if state == u"Исполнена": 
            order.status = EXECUTED
            order.onexecuted()
            order.delete()
        elif state == u"Активна": 
            order.status = ACTIVE
            order.onregistered()
        elif state == u"Снята": 
            order.status = KILLED
            order.onkilled()
            order.delete()
        log.debug('Order status changed, id=%s, key=%s, status: %s -> %s' % (id(order), order.order_key, old_status, order.status))
