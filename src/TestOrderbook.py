from plugins import InitialEngine
from datetime import datetime

def testInsortBuyIsSorted():
    buy1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"00:00:00.000",'Record Type':"ENTER",'Price':"35.080",'Volume':"1000",'Undisclosed Volume':"0",'Value':"35080",'Qualifiers':"",'Trans ID':"0",'Bid ID':"6245081189407525023",'Ask ID':"",'Bid/Ask':"B",'Entry Time':"",'Old Price':"",'Old Volume':"",'Buyer Broker ID':"140",'Seller Broker ID':""}
    buys = {"buy1":buy1,"buy2":buy1.copy(),"buy3":buy1.copy(),"buy4":buy1.copy(),"buy5":buy1.copy(),"buy6":buy1.copy(),"buy7":buy1.copy(),"buy8":buy1.copy(),"buy9":buy1.copy(),"buy10":buy1.copy()}
    buys["buy2"]["Price"] = 35.080
    buys["buy3"]["Price"] = 36.298
    buys["buy4"]["Price"] = 27.987
    buys["buy5"]["Price"] = 34.902
    buys["buy6"]["Price"] = 37.333
    buys["buy7"]["Price"] = 29.072
    buys["buy8"]["Price"] = 35.026
    buys["buy9"]["Price"] = 39.333
    buys["buy10"]["Price"] = 37.822
    orderBook = InitialEngine.OrderBook()
    orderBook._insortBuy(buys["buy1"])
    orderBook._insortBuy(buys["buy2"])
    orderBook._insortBuy(buys["buy3"])
    orderBook._insortBuy(buys["buy4"])
    orderBook._insortBuy(buys["buy5"])
    orderBook._insortBuy(buys["buy6"])
    orderBook._insortBuy(buys["buy7"])
    orderBook._insortBuy(buys["buy8"])
    orderBook._insortBuy(buys["buy9"])
    orderBook._insortBuy(buys["buy10"])
    assert all(float(orderBook.buys[i]['Price']) >= float(orderBook.buys[i+1]['Price']) for i in xrange(len(orderBook.buys)-1))
    print "Passed testInsortBuyIsSorted"

def testInsortSellIsSorted():
    sell1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"00:00:00.000",'Record Type':"ENTER",'Price':"35.080",'Volume':"1000",'Undisclosed Volume':"0",'Value':"35080",'Qualifiers':"",'Trans ID':"0",'Bid ID':"6245081189407525023",'Ask ID':"",'Bid/Ask':"A",'Entry Time':"",'Old Price':"",'Old Volume':"",'seller Broker ID':"140",'Seller Broker ID':""}
    sells = {"sell1":sell1,"sell2":sell1.copy(),"sell3":sell1.copy(),"sell4":sell1.copy(),"sell5":sell1.copy(),"sell6":sell1.copy(),"sell7":sell1.copy(),"sell8":sell1.copy(),"sell9":sell1.copy(),"sell10":sell1.copy()}
    sells["sell2"]["Price"] = 35.080
    sells["sell3"]["Price"] = 36.298
    sells["sell4"]["Price"] = 27.987
    sells["sell5"]["Price"] = 34.902
    sells["sell6"]["Price"] = 37.333
    sells["sell7"]["Price"] = 29.072
    sells["sell8"]["Price"] = 35.026
    sells["sell9"]["Price"] = 39.333
    sells["sell10"]["Price"] = 37.822
    orderBook = InitialEngine.OrderBook()
    orderBook._insortSell(sells["sell1"])
    orderBook._insortSell(sells["sell2"])
    orderBook._insortSell(sells["sell3"])
    orderBook._insortSell(sells["sell4"])
    orderBook._insortSell(sells["sell5"])
    orderBook._insortSell(sells["sell6"])
    orderBook._insortSell(sells["sell7"])
    orderBook._insortSell(sells["sell8"])
    orderBook._insortSell(sells["sell9"])
    orderBook._insortSell(sells["sell10"])
    assert all(float(orderBook.sells[i]['Price']) <= float(orderBook.sells[i+1]['Price']) for i in xrange(len(orderBook.sells)-1))
    print "Passed testInsortSellIsSorted"

def testSimpleMatchSameQuantity():
    buy1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"11:00:00.000",'Record Type':"ENTER",'Price':"35.100",'Volume':"1000",'Undisclosed Volume':"0",'Value':"35080",'Qualifiers':"",'Trans ID':"0",'Bid ID':"6245081189407525023",'Ask ID':"",'Bid/Ask':"B",'Entry Time':"",'Old Price':"",'Old Volume':"",'Buyer Broker ID':"140",'Seller Broker ID':""}
    sell1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"12:00:00.000",'Record Type':"ENTER",'Price':"35.080",'Volume':"1000",'Undisclosed Volume':"0",'Value':"70200",'Qualifiers':"",'Trans ID':"0",'Bid ID':"",'Ask ID':"6245081189408853420",'Bid/Ask':"A",'Entry Time':"",'Old Price':"",'Old Volume':"",'Buyer Broker ID':"",'Seller Broker ID':"140"}
    orderBook = InitialEngine.OrderBook()
    #add first buy and check it matched 0 orders
    assert (len (orderBook.addToBuy(buy1,datetime.strptime(buy1['Time'], "%H:%M:%S.%f"))) == 0)
    #add second buy and check it matched 1 orders
    assert (len (orderBook.addToSell(sell1,datetime.strptime(sell1['Time'], "%H:%M:%S.%f"))) == 1)
    print "Passed testSimpleMatchSameQuantity"

def testSimpleMatchDifferentQuantity():
    buy1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"11:00:00.000",'Record Type':"ENTER",'Price':"35.100",'Volume':"1000",'Undisclosed Volume':"0",'Value':"35080",'Qualifiers':"",'Trans ID':"0",'Bid ID':"6245081189407525023",'Ask ID':"",'Bid/Ask':"B",'Entry Time':"",'Old Price':"",'Old Volume':"",'Buyer Broker ID':"140",'Seller Broker ID':""}
    sell1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"12:00:00.000",'Record Type':"ENTER",'Price':"35.080",'Volume':"2000",'Undisclosed Volume':"0",'Value':"70200",'Qualifiers':"",'Trans ID':"0",'Bid ID':"",'Ask ID':"6245081189408853420",'Bid/Ask':"A",'Entry Time':"",'Old Price':"",'Old Volume':"",'Buyer Broker ID':"",'Seller Broker ID':"140"}
    orderBook = InitialEngine.OrderBook()
    #add first buy and check it matched 0 orders
    assert (len (orderBook.addToBuy(buy1,datetime.strptime(buy1['Time'], "%H:%M:%S.%f"))) == 0)
    #add second buy and check it matched 1 orders
    matches = orderBook.addToSell(sell1,datetime.strptime(sell1['Time'], "%H:%M:%S.%f"))
    assert (len (matches) == 1)
    #check volume and price is correct
    assert (float(matches[0]['Volume']) == 1000)
    assert (float(matches[0]['Price']) == 35.080)
    #check volume of the sell decreased
    assert (int(orderBook.sells[0]['Volume']) == 1000)
    print "Passed testSimpleMatchDifferentQuantity"

def testIncorrectMatching():
    buy1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"11:00:00.000",'Record Type':"ENTER",'Price':"35.080",'Volume':"1000",'Undisclosed Volume':"0",'Value':"35080",'Qualifiers':"",'Trans ID':"0",'Bid ID':"6245081189407525023",'Ask ID':"",'Bid/Ask':"B",'Entry Time':"",'Old Price':"",'Old Volume':"",'Buyer Broker ID':"140",'Seller Broker ID':""}
    sell1 = {'Instrument':"BHP",'Date':"2013-03-15",'Time':"12:00:00.000",'Record Type':"ENTER",'Price':"35.100",'Volume':"2000",'Undisclosed Volume':"0",'Value':"70200",'Qualifiers':"",'Trans ID':"0",'Bid ID':"",'Ask ID':"6245081189408853420",'Bid/Ask':"A",'Entry Time':"",'Old Price':"",'Old Volume':"",'Buyer Broker ID':"",'Seller Broker ID':"140"}    
    orderBook = InitialEngine.OrderBook()
    #add first buy and check it matched 0 orders
    assert (len (orderBook.addToBuy(buy1,datetime.strptime(buy1['Time'], "%H:%M:%S.%f"))) == 0)
    #add second buy and check it matched 0 orders
    matches = orderBook.addToSell(sell1,datetime.strptime(sell1['Time'], "%H:%M:%S.%f"))
    assert (len (matches) == 0)
    #check volume of the sell decreased
    assert (int(orderBook.sells[0]['Volume']) == 2000)
    assert (len (orderBook.sells) == 1)
    assert (len (orderBook.buys) == 1)
    print "Passed testIncorrectMatching"
testInsortBuyIsSorted()
testInsortSellIsSorted()
testSimpleMatchSameQuantity()
testSimpleMatchDifferentQuantity()
testIncorrectMatching()