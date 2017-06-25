import pandas as pd
import pandas.io
from pandas_datareader import data, wb
from datetime import date, timedelta
from pandas_datareader.data import Options
import datetime

class optionsData(object):
    #Run all functions on instance creation
    def __init__(self):
        self.removeDataList=['Symbol','Chg','PctChg','IV','Root',
                             'IsNonstandard','Underlying','Underlying_Price',
                             'Quote_Time','Last_Trade_Date','JSON','Bid',
                             'Ask','Vol','Open_Int']
        self.stockPrice = self.getStockPrice("AAPL")
        df = self.getOptionsData("AAPL")
        df = self.removeData(df)
        df = self.calcStrikePrice(df)

        print (type(df))
        print int( self.getStockPrice("AAPL"))

        #group by type
        df=df.groupby(by=['Expiry'])


        df = df.get_group('2017-06-30 00:00:00')

        combinations=self.createCombinations()
        #print combinations
        myList=[]
        myDf = pd.DataFrame(columns=df.columns)
        fullDf = pd.DataFrame(columns=df.columns)
        #print myDf
        print combinations
        #print df.values
        for i in combinations:
            if df.loc[(df['Strike'] == i[0]) & (df['Type'] == "call")].empty:
                continue
            if df.loc[(df['Strike'] == i[1]) & (df['Type'] == "call")].empty:
                continue
            if df.loc[(df['Strike'] == i[2]) & (df['Type'] == "put")].empty:
                continue
            if df.loc[(df['Strike'] == i[3]) & (df['Type'] == "put")].empty:
                continue

            row1=df.loc[(df['Strike'] == i[0]) & (df['Type'] =="call")]
            row2=df.loc[(df['Strike'] == i[1]) & (df['Type'] == "call")]
            row3=df.loc[(df['Strike'] == i[2]) & (df['Type'] == "put")]
            row4=df.loc[(df['Strike'] == i[3]) & (df['Type'] == "put")]

            #print row1
            #print row2
            #print row3
            #print row4

            myDf = pd.concat([row1,row2,row3,row4], ignore_index=True)
            if fullDf.empty:
                fullDf = myDf
                continue
            fullDf = pd.concat([fullDf, myDf], axis=1)


        print myDf.values
        print fullDf.values
        self.writeDataFrame(fullDf)

    #create all combinations for bodySpread
    def createCombinations(self):
        body = range(1,50)
        wing = range(1,4)
        stockPrice= int(self.getStockPrice("AAPL"))
        spreadList = []

        # calculating calls
        for i in body:
            for a in wing:
                spreadList.append(
                    (a + i + stockPrice, i + stockPrice, stockPrice - i,
                     stockPrice - a - i))

        return spreadList

    #Function to get stock price from google finance
    def getStockPrice(self,stock):
        start = date.today() - timedelta(7)
        end= datetime.datetime.today().strftime('%Y-%m-%d')
        stockData = data.DataReader(stock, "google", start, end)
        stockPrice = stockData.iloc[[-1]]['Close'].values[0]
        return stockPrice

    #Get option data from yahoo finance
    def getOptionsData(self,optionIndex):
        optionIndex = Options(optionIndex, 'yahoo')
        data = optionIndex.get_all_data()
        data = data.reset_index()
        data= data.sort_values(['Expiry'], ascending=[True])
        data = data.reset_index()
        data= data.drop(['index'], axis=1)
        return data

    #Remove unnecessary columns
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

        for index, row in df.iterrows():
            if df['Type'][index] == 'call':
                dfPut = dfPut.drop([index], axis=0)
            else:
                dfCall = dfCall.drop([index], axis=0)

        dfPut = dfPut.reset_index()
        dfCall = dfCall.reset_index()
        dfPut=dfPut.drop(['index'], axis=1)
        dfCall=dfCall.drop(['index'], axis=1)
        df = pd.concat([dfCall, dfPut], axis=1)
        return df

    #Remove all but the first 4 rows of data
    def editData(self, df):
        df =df[:4]
        return df

    #Write Data to excel spreadsheet
    def writeDataFrame(self,df):
        writer = pd.ExcelWriter(
            'C:/Users/sped\PycharmProjects/cboeData/output.xlsx')
        df.to_excel(writer, 'Sheet1')
        writer.save()
        print 'data written'


a=optionsData()