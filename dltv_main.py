import time
import traceback
import dltv_cyberscore
while True:
    dltv_cyberscore.get_live_matches()
    print('Сплю 3 минут')
    time.sleep(180)