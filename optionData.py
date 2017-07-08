import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta
from pandas_datareader.data import Options
import datetime
import numpy as np
import xlsxwriter

class optionsData(object):
    #Run all functions on instance creation
    def __init__(self):
        self.stock ="AAPL"

        self.removeDataList=['Symbol','Chg','PctChg','IV','Root',
                             'IsNonstandard','Underlying','Underlying_Price',
                             'Quote_Time','Last_Trade_Date','JSON','Bid',
                             'Ask','Vol','Open_Int']

        self.stockPrice = self.getStockPrice(self.stock)
        df = self.getOptionsData(self.stock)
        df = self.removeData(df)

        #editData removes all but the first 4 rows
        #df =  self.editData(df)

        df = self.calcStrikePrice(df)
        self.count=0

        #fullDf is the fullDataframe that will be constructed which will hold
        #  all the data
        self.fullDf = pd.DataFrame()
        self.combinations = self.createCombinations()
        self.dfList=[]
        self.dfList=self.createWeekDfList(df)

        maxColumns=self.findMaxColumns()
        reordered = self.reorderColumns(maxColumns)

        self.concatAll = self.concatAll[reordered]

        # Write out data
        self.writeDataFrame(self.concatAll)

    #reoderColumns
    def reorderColumns(self, maxColumns):
        for i in self.dfList:
            if len(i.columns) == maxColumns:
                correctColumnList = list(i.columns)

        self.concatAll = pd.concat(self.dfList,ignore_index=True)

        important = correctColumnList
        reordered = important + [c for c in self.concatAll.columns if
                                 c not in important]
        return reordered

    #find the week with the maximum number of columns
    def findMaxColumns(self):
        #Find max number of columns in Dataframes
        maxColumns = max([len(self.dfList[i].columns) for i in range(len(
            self.dfList))])
        return maxColumns

    def calcRiskRewardRatio(self, row1, row2, row3,row4, lastTotal):
        ratio = ((row1-row2-lastTotal)+(row3-row4-lastTotal))/2*-1
        return ratio

    def calcLastTotal(self, row1, row2, row3,row4):
        lastTotal = row2 + row3 - row1 - row4
        return lastTotal

    def normRatio(self, lastTotal, riskRewardRatio):
        normRatio = ((1/lastTotal)*-riskRewardRatio)*-1
        return normRatio

    #This functin creates a list of the weeks of dataframes which will then
    # be concatenated which makes up the final data.
    def createWeekDfList(self, df):
        df=df.groupby(by=['Expiry'])

        #Loop through groups in datatframe
        for index, value in df:
            #index is the date

            # week DF is the dataframe for all entries within that week
            weekDf = df.get_group(index)

            #weekDf = weekDf.set_index([newList])
            weekDf = self.calcCombinations(weekDf)

            if weekDf.empty:
                continue

            self.dfList.append(weekDf)

        return self.dfList

    def calcCombinations(self, df):
        index=0
        weekDfList=[]
        #concatWeekDf is the concatenated dataframe for 1 of the possible
        # combinations of spread

        #weekDf = pd.DataFrame(columns=df.columns)
        weekDf = pd.DataFrame()


        concatWeekDf = pd.DataFrame(columns=df.columns)

        for i in self.combinations:
            self.count = self.count + 1
            if df.loc[(df['Strike'] == i[0]) & (df['Type'] == "call")].empty:
                continue
            if df.loc[(df['Strike'] == i[1]) & (df['Type'] == "call")].empty:
                continue
            if df.loc[(df['Strike'] == i[2]) & (df['Type'] == "put")].empty:
                continue
            if df.loc[(df['Strike'] == i[3]) & (df['Type'] == "put")].empty:
                continue


            row1=df.loc[(df['Strike'] == i[0]) & (df['Type'] ==
                                                  "call")]
            row2=df.loc[(df['Strike'] == i[1]) & (df['Type'] ==
                                                  "call")]
            row3=df.loc[(df['Strike'] == i[2]) & (df['Type'] ==
                                                  "put")]
            row4=df.loc[(df['Strike'] == i[3]) & (df['Type'] ==
                                                  "put")]


            row1Last =  row1['Last'].values[0]
            row2Last =  row2['Last'].values[0]
            row3Last =  row3['Last'].values[0]
            row4Last =  row4['Last'].values[0]

            concatWeekDf = pd.concat([row1,row2,row3,row4], ignore_index=True)

            #re-order columns pop Expiry to the front of column list
            cols = list(concatWeekDf)


            total = self.calcLastTotal(row1Last,row2Last,row3Last,row4Last)
            ratio = self.calcRiskRewardRatio(row1Last,row2Last,row3Last,
                                             row4Last, total)
            normRatio = self.normRatio(total,ratio)



            cols.insert(0, cols.pop(cols.index('Expiry')))
            concatWeekDf = concatWeekDf.ix[:, cols]
            concatWeekDf.columns=['Expiry{0}'.format(index), 'Strike{'
                                                             '0}'.format(
                index), 'Type{0}'.format(index), 'Last{0}'.format(index)]
            index = index + 1


            concatWeekDf['total{0}'.format(index)]= total
            concatWeekDf['ratio{0}'.format(index)]=ratio
            concatWeekDf['normratio{0}'.format(index)] = normRatio



            #Continue loop if combination is empty
            if concatWeekDf.empty:
                continue

            weekDf = pd.concat([weekDf, concatWeekDf], axis=1)
        return weekDf

    #create all combinations for bodySpread
    def createCombinations(self):
        body=np.arange(1, 5, 0.5)
        wing =np.arange(2, 3, 0.5)
        stockPrice= int(self.getStockPrice(self.stock))
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


    #Remove all but the first 4 rows of data
    def editData(self, df):
        print df
        df =df[:20]
        return df

    #Write Data to excel spreadsheet
    def writeDataFrame(self,df):
        writer = pd.ExcelWriter(
            'C:/Users/sped\PycharmProjects/cboeData/output.xlsx',
            engine='xlsxwriter',
            datetime_format='mmm d yy')
        df.to_excel(writer, 'Sheet1')
        writer.save()
        print 'data written'

a=optionsData()