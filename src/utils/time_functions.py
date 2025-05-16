from datetime import datetime, timedelta



class TimeUtils():


    def getDiferenceSeconds(self, startTime):
        
        finishTime = datetime.utcnow()
        delta = finishTime - startTime
        diff= delta.total_seconds()
        return diff
    
    def getCurrentDateTime(self):
        return datetime.utcnow()
    
    def get24HoursFromNow(self):
        return datetime.now() + timedelta(hours=-24)
    
    def stringToDateTime(sef, dateString):

        return datetime.fromisoformat(dateString)