from datetime import datetime, timezone
import config.settings as settings
import pytz
import os

class DateUtils():

    def getDateISOFormat(self ):
        dt = datetime.now(timezone.utc)
        tz = dt.astimezone()
        return  tz.isoformat()
    
    def getTimeStamp(self):
        return datetime.now().strftime(settings.DATETIME_STRING_FORMAT)
    
    def getTime(self):
        return datetime.now()
    
    def getDiferenceInmilliseconds(self, globalTime, currentTime):
        return  (currentTime - globalTime).total_seconds() * 1000
    
    def getTimeZone(self):
        dt = datetime.now(timezone.utc)
        tz = dt.astimezone()
        isoDate = tz.isoformat()
        p1 =  isoDate[:23]
        p2 = isoDate[-6:]
        
        return p1 + p2 
    
    def localTimeToUTC(self,  dateString):
         return  datetime.fromisoformat(dateString).astimezone(timezone.utc).isoformat()[:-9]+'Z'
    
    def timezone(self, zone):
        time_zone = pytz.timezone(zone)
        date = datetime.now(time_zone).isoformat()
        p1 = date[:23]
        p2 = date[-6:]

        return  p1 + p2
    
    def readLocalTime(self):
        self.localtime = "./etc/localtime"
        tz = os.readlink(self.localtime)
        loc = tz.find('/zoneinfo/')
        localTime = tz[loc + 10:]
        return localTime
             