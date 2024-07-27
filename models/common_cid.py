import datetime

db = DAL('mysql://root:@localhost/xyz')
mreporting_http_pass = 'abC321'
date_fixed = datetime.datetime.now() + datetime.timedelta(hours=6)
