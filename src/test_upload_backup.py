import time
from datetime import datetime, timedelta
run = True

sendSharepointLastRetry = datetime.now()
nextRetry = sendSharepointLastRetry +  timedelta(seconds=float(5))
while run:
  
  now = datetime.now()

  print(f'NOW {now}')
  print(f"TRY {nextRetry}")
  print("**********************************")
  time.sleep(1)