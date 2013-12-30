# -*- coding:cp936 -*-
from pylab import *
from matplotlib.dates import DateFormatter, WeekdayLocator, HourLocator, DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo, candlestick, plot_day_summary, candlestick2
from matplotlib.font_manager import FontProperties

if  __name__ == '__main__':
	font = FontProperties(fname=r"t:\Windows\Fonts\simsun.ttc",size=18)
	# 定义起始、终止日期和股票代码
	date1 = ( 2013, 1, 1 )
	date2 = ( 2013, 8, 1 )
	date3 = ( 2013, 5, 1 )
	
	stock_num = '600036.ss'
	# 定义日期格式
	mondays = WeekdayLocator(MONDAY) #major ticks on the mondays
	alldays = DayLocator()	#minor ticks on the days
	weekFormatter = DateFormatter('%b %d')	# Jan 12
	dayFormatter = DateFormatter('%d')	# 12
	# 获取股票数据
	quotes = quotes_historical_yahoo(stock_num, date1, date2)
	quotes2 = quotes_historical_yahoo(stock_num, date1, date3)
	if len(quotes) == 0:
		raise SystemExit
	# 绘制蜡烛线或美国线
	fig = figure(facecolor='gray')
	fig.subplots_adjust(bottom=0.2)
	ax = fig.add_subplot(111)
	ax2 = fig.add_subplot(111)
	
	#fig, ax = plt.subplots()
	#fig.subplots_adjust(bottom=0.2)
	
	ax.xaxis.set_major_locator(mondays)
	ax.xaxis.set_minor_locator(alldays)
	ax.xaxis.set_major_formatter(weekFormatter)
	#注释掉下面的其中一行，可以得到蜡烛线或美国线
	candlestick(ax, quotes, width=0.6)
	candlestick(ax2, quotes2, width=0.6)
	#plot_day_summary(ax, quotes, ticksize=3)
	ax.xaxis_date()
	ax.autoscale_view()
	ax2.xaxis_date()
	ax2.autoscale_view()

	setp( gca().get_xticklabels(), rotation=90, horizontalalignment='right')
	title(stock_num + u'2012,12,25-2013,6,1',fontproperties=font)
	grid()
	show()