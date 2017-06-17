import pandas as pd
import pandas.io
from pandas_datareader import data, wb
from datetime import date, timedelta
from pandas_datareader.data import Options
import datetime


#Function to get stock price from google finance
def getStockPrice(stock):
    start = date.today() - timedelta(7)
    end= datetime.datetime.today().strftime('%Y-%m-%d')

    aapl = data.DataReader(stock, "google", start, end)

    stockPrice = aapl.iloc[[-1]]['Close'].values[0]
    return stockPrice


#Get option data from yahoo finance
def getOptionsData(optionIndex):
    optionIndex = Options(optionIndex, 'yahoo')
    data = optionIndex.get_all_data()
    data = data.reset_index()
    data= data.sort_values(['Expiry'], ascending=[False])
    return data


#Write Data to excel spreadsheet
def writeDataFrame(df):
    writer = pd.ExcelWriter(
        'C:/Users/sped\PycharmProjects/cboeData/output.xlsx')
    df.to_excel(writer, 'Sheet1')
    writer.save()
    print 'data written'


stockPrice = getStockPrice("AAPL")
df = getOptionsData("AAPL")
writeDataFrame(df)