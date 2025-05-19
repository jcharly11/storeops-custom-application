import config.sharepoint_settings as sharepoint_settings
import datetime
from database.database_azure import DataBaseFiles

database = DataBaseFiles()
daysKeeped = sharepoint_settings.SHAREPOINT_KEEP_MESSAGES_DAYS
now = datetime.datetime.now()
fakeDate = now + datetime.timedelta(days = daysKeeped) ##Adding day to perfomr query
fakeDate = fakeDate.strftime("%Y-%m-%d")
now = now.strftime("%Y-%m-%d")

print(f"Inserting data test {now}")
database.saveFiles(request_uuid = "00000-000000", link= "https://link-test-sharepoint.com", files= "TEST DATA", path= "TEST DATA")
print(f"Searching data test less than {fakeDate}")

items = database.getFilesOlderThan(date_time_inserted=fakeDate)
 
print("Located items : ", items)
 
    