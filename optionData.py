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


stockPrice = getStockPrice("AAPL")


aapl = Options('AAPL', 'yahoo')
data = aapl.get_all_data()
data = data.reset_index()


print type (list(data))
print list(data.columns.values)

#Print statements:
#print list(data)
#print data.sort_values(ascending=True)
#print data.head()
#print list(data)
#print len(list(data))
#print data.head()


getStockPrice("APPL")
data=data.sort_values(['Expiry'], ascending=[False])

#data=data.iloc[0:4]
#data=data.drop(['IsNonstandard','Underlying','Underlying_Price'], axis=1)
#data=data.drop(data.columns[0], axis=1)

#Print statements:
#print data.columns[1]
#printdata.sort_values(['Last'], ascending=[True])
#print data


writer = pd.ExcelWriter('C:/Users/sped\PycharmProjects/cboeData/output.xlsx')
data.to_excel(writer,'Sheet1')
writer.save()