import config.sharepoint_settings as sharepoint_settings
import datetime
from database.database import DataBase

database = DataBase()
daysKeeped = sharepoint_settings.SHAREPOINT_KEEP_MESSAGES_DAYS
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d") 
print("Date requested : ", now)

items = database.getMessages(date=now, status='not_sent')
 
print("Located items : ", items)
 
    