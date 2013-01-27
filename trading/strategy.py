from trading.broker import *
import logging

log = logging.getLogger("strategy")

class Sequental:
    def __init__(self,ticker, trades=[]):
        self.ticker = ticker
        self.trades = trades

    def trade( self, ticker ):

        result = self.trades.pop(0) if self.trades else TRADE_KEEP
        log.debug('Strategy %s says: %s' % (self.__class__.__name__, TRADE_NAMES[result]))
        return result

class Insanity:
    def __init__(self,ticker):
        self.ticker = ticker
        self.last_trade = TRADE_EXIT

    def trade( self, ticker ):
        import random

        result = random.choice([TRADE_LONG, TRADE_SHORT, TRADE_EXIT, TRADE_KEEP])
        log.debug('Strategy %s says: %s' % (self.__class__.__name__, TRADE_NAMES[result]))
        self.last_trade = result
        return result


class Strategy:

    def __init__(self,ticker,matype=0,period=13,stability=5):
        self.ticker = ticker
        self.matype = matype
        self.period = period
        self.stability = stability
        self.ma1 = ticker.indicator("MA1", "MA", optInTimePeriod=period, optInMAType=matype)
        self.signal = ticker["signal"]
        self.signal.set(0)

    def trade( self, ticker ):
        size = len(ticker)
        if size < self.period: 
            log.debug("Collecting data: %d/%d" ,size, self.period )
            return TRADE_KEEP

        if ticker.price < self.ma1.value():
            self.signal.set( +1 )
        elif ticker.price > self.ma1.value():
            self.signal.set( -1 )
        else:
            self.signal.set( 0 )

        ssum = sum(self.signal.data()[-self.stability:]) 
        log.debug("MA ssum = %+d; +-%d needed." % (ssum, self.stability))

        if ssum == +self.stability: 
            return TRADE_LONG
        if ssum == -self.stability: 
            return TRADE_SHORT
        if ssum == 0.0:
            return TRADE_EXIT

        return TRADE_KEEP

