import pandas.io.data as web
import datetime
start = datetime.datetime(2008, 1, 1)
end = datetime.datetime(2013, 1, 1)
df=web.DataReader("XKO", 'google', start, end)
df.info()
df.memory_usage()