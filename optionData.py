import pandas as pd
import pandas.io
from pandas_datareader import data, wb
from datetime import date, timedelta
from pandas_datareader.data import Options
import datetime

class optionsData(object):
    def __init__(self):
        self.removeDataList=['Symbol','Chg','PctChg','IV','Root',
                             'IsNonstandard','Underlying','Underlying_Price',
                             'Quote_Time','Last_Trade_Date','JSON']
        self.stockPrice = self.getStockPrice("AAPL")
        df = self.getOptionsData("AAPL")
        df = self.removeData(df)
        df = self.calcStrikePrice(df)
        df = self.sepCallPuts(df)
        self.writeDataFrame(df)

    #Function to get stock price from google finance
    def getStockPrice(self,stock):
        start = date.today() - timedelta(7)
        end= datetime.datetime.today().strftime('%Y-%m-%d')
        aapl = data.DataReader(stock, "google", start, end)
        stockPrice = aapl.iloc[[-1]]['Close'].values[0]
        return stockPrice

    #Get option data from yahoo finance
    def getOptionsData(self,optionIndex):
        optionIndex = Options(optionIndex, 'yahoo')
        data = optionIndex.get_all_data()
        data = data.reset_index()
        data= data.sort_values(['Expiry'], ascending=[True])
        data = data.reset_index()
        data=data.drop(['index'], axis=1)
        return data

    def removeData(self, df):
        for i in self.removeDataList:
            df=df.drop([i], axis=1)
        return df

    #Calculate whether strike price is within 0.15%+- of stock price
    def calcStrikePrice(self, df):
        for index, row in df.iterrows():
            if not self.stockPrice-0.15*self.stockPrice < row[
                'Strike']<1.15*self.stockPrice:
                df = df.drop([index], axis=0)
        return df

    #Divide Call and Puts
    def sepCallPuts(self, df):
        dfCall=df
        dfPut=df

        print type(dfPut)
        print type(dfCall)
        for index, row in df.iterrows():
            if df['Type'][index] == 'call':
                dfPut = dfPut.drop([index], axis=0)
            else:
                dfCall = dfCall.drop([index], axis=0)

        df = pd.concat([dfCall, dfPut], axis=1, ignore_index=True)
        #print dfCall
        return df

    #Write Data to excel spreadsheet
    def writeDataFrame(self,df):
        writer = pd.ExcelWriter(
            'C:/Users/sped\PycharmProjects/cboeData/output.xlsx')
        df.to_excel(writer, 'Sheet1')
        writer.save()
        print 'data written'


a=optionsData()