"""Mean reversion signal generator plugin"""

import plugins
import copy
from plugins.SignalGeneratorUtils import calculateAverageReturn

class MeanReversionSignalGenerator(plugins.ISignalGeneratorPlugin):
    """Makes buy and sell signals based off the mean reversion strategy"""

    def setup(self, config):
        """Reads mean reversion strategy parameters from the config file"""
        self.buyPacketSize = config.getint('Parameters','buyPacketSize')
        self.sellPacketSize = config.getint('Parameters','sellPacketSize')
        
        self.maxBuyPacketSurplus = config.getint('Parameters','maxBuyPacketSurplus')
        self.buyDistanceFromMeanThreshold = config.getfloat('Parameters','buyDistanceFromMeanThreshold')
        self.sellDistanceFromMeanThreshold = config.getfloat('Parameters','sellDistanceFromMeanThreshold')
        self.minimumTimeBeforeAction = config.get('Parameters','minimumTimeBeforeAction')
        
        self.BHPsharesInStock = 0
        self.outstandingSellVolume = 0
        self.outstandingBuyVolume = 0
        
        self.myorders = []
        self.tradesviewed = []
        self.runningaverage = 0
        
        self.currentTime = '00:00:00.000'
        
        self.historicalOutlook = config.getint('Parameters','historicalOutlook')
        if self.historicalOutlook < 2:
            self.historicalOutlook = 2
                
        self.tradesbeforeorder = []
        self.previousfivetrades = []
    
    def manualSetup(self,parameters):
        """Reads momentum strategy parameters from a parameter list"""
        self.minimumTimeBeforeAction = parameters["minimumTimeBeforeAction"]
        self.buyDistanceFromMeanThreshold = parameters["buyDistanceFromMeanThreshold"]
        self.sellDistanceFromMeanThreshold = parameters["sellDistanceFromMeanThreshold"]        
        self.buyPacketSize = parameters["buyPacketSize"]
        self.sellPacketSize = parameters["sellPacketSize"]
        self.maxBuyPacketSurplus = parameters["maxBuyPacketSurplus"]
        
        self.ordersviewed = []
        self.tradesviewed = []
        self.runningaverage = 0
        
        self.BHPsharesInStock = 0 # convert this into a dictionary for multiple instruments
        self.myorders = []
        self.outstandingSellVolume = 0
        self.outstandingBuyVolume = 0
        self.currentTime = '00:00:00.000'
        self.historicalOutlook = parameters["historicalOutlook"]
        
        self.tradesbeforeorder = []
        self.previousfivetrades = []

    def __call__(self, trading_record=None, endofday=False):
        orders = []
        
        if trading_record == None and endofday == False:
            # return all initial orders i.e. random before market open
            return orders
        elif trading_record == None and endofday == True:
            if self.BHPsharesInStock > 0:
                # Dump the shares because day is finished
                return self.createDumpShareSell()
            return None
        elif trading_record['Record Type'] == 'TRADE':
            self.previousfivetrades.append(trading_record)
            if len(self.previousfivetrades) > self.historicalOutlook:
                self.previousfivetrades.pop(0)
            
            self.currentTime = trading_record['Time']
            if trading_record['Buyer Broker ID'] == 'Algorithmic':
                self.outstandingBuyVolume -= int(trading_record['Volume'])
                self.BHPsharesInStock += int(trading_record['Volume'])
            if trading_record['Seller Broker ID'] == 'Algorithmic':
                self.outstandingSellVolume -= int(trading_record['Volume'])
            
            self.tradesviewed.append(trading_record)
            if len(self.tradesviewed) > self.historicalOutlook:
                self.tradesviewed.pop(0)
            if len(self.tradesviewed) > 1:
                self.runningaverage = calculateAverageReturn(self.tradesviewed)
            
            if len(self.tradesviewed) > 1 and self.currentTime >= self.minimumTimeBeforeAction:
                if self.runningaverage >= self.sellDistanceFromMeanThreshold:
                    if self.BHPsharesInStock > 0:
                        sell = trading_record.copy()
                        sell['Record Type'] = 'ENTER'
                        sell['Bid/Ask'] = 'A'
                        sell['Price'] = 'MP' #trading_record['Price'] # we can decrease this if we want
                        
                        if self.BHPsharesInStock >= self.sellPacketSize:
                            sell['Volume'] = str(self.sellPacketSize)
                            self.BHPsharesInStock -= self.sellPacketSize
                        else:
                            sell['Volume'] = str(self.BHPsharesInStock)
                            self.BHPsharesInStock = 0
                        
                        self.outstandingSellVolume += int(sell['Volume'])
                        sell['Ask ID'] = 'Algorithmic' + str(len(self.myorders)) # Keeps this unique
                        sell['Bid ID'] = ''
                        sell['Buyer Broker ID'] = ''
                        sell['Seller Broker ID'] = 'Algorithmic'
                        orders.append(sell)
                        self.myorders.append(sell)
                                                
                        self.tradesbeforeorder.append(copy.deepcopy(self.previousfivetrades))
                elif self.runningaverage <= -self.buyDistanceFromMeanThreshold:
                    if self.shouldBuyMoreStocks(trading_record['Instrument']) == True:
                        buy = trading_record.copy()
                        buy['Record Type'] = 'ENTER'
                        buy['Bid/Ask'] = 'B'
                        buy['Price'] = 'MP' #trading_record['Price'] # we can increase this if we want
                        buy['Volume'] = self.volumeToBuy(trading_record['Instrument'])          
                        self.outstandingBuyVolume += int(buy['Volume'])
                        buy['Bid ID'] = 'Algorithmic' + str(len(self.myorders))
                        buy['Ask ID'] = ''
                        buy['Buyer Broker ID'] = 'Algorithmic'
                        buy['Seller Broker ID'] = ''
                        orders.append(buy)
                        self.myorders.append(buy)  
                                                
                        self.tradesbeforeorder.append(copy.deepcopy(self.previousfivetrades))
        return orders
     
    def createDumpShareSell(self):
        sell = {
            'Instrument': 'BHP',
            'Date': '20130101',
            'Time': self.currentTime,
            'Record Type': 'ENTER',
            'Price': 'MP',
            'Volume': self.BHPsharesInStock,
            'Undisclosed Volume': '',
            'Value': '',
            'Qualifiers': '',
            'Trans ID': 0,
            'Bid ID': '',
            'Ask ID': 'Algorithmic' + str(len(self.myorders)),
            'Bid/Ask': 'A',
            'Entry Time': '',
            'Old Price': '',
            'Old Volume': '',
            'Buyer Broker ID': '',
            'Seller Broker ID': 'Algorithmic'
        }
        
        return sell
    def shouldBuyMoreStocks(self, instrument):
        if self.BHPsharesInStock + self.outstandingBuyVolume + self.outstandingSellVolume >= self.maxBuyPacketSurplus*self.buyPacketSize:
            return False
        return True
        
    def volumeToBuy(self,instrument):
        if self.maxBuyPacketSurplus*self.buyPacketSize - self.BHPsharesInStock + self.outstandingBuyVolume + self.outstandingSellVolume < self.buyPacketSize:
            return self.maxBuyPacketSurplus*self.buyPacketSize - self.BHPsharesInStock + self.outstandingBuyVolume + self.outstandingSellVolume
        else:
            return self.buyPacketSize
    def getTradesBeforeOrder(self):
        return self.tradesbeforeorder
