import datetime
import calendar

def get_year():
	now = datetime.datetime.now()
	return now.year
	
def cetak_nomor_hari():
	print ("[", end='')
	for i in range (1, 365):
		print (i, end='')
		print(", ", end='')
	print (365, end='')
	x = get_year()
	if (calendar.isleap(x)):
		print (", 366", end='')
	print ("]")
	return
	
def number_to_date(x):
	year = get_year()
	date = datetime.datetime(year, 1, 1) + datetime.timedelta(x - 1)
	return date
	
def date_to_day(date):
	day_name = date.strftime("%A")
	return day_name

print (get_year())
cetak_nomor_hari()
x = number_to_date(5)
print (x)
print (date_to_day(x))