import time
import traceback
import dltv_cyberscore
while True:
    dltv_cyberscore.get_live_matches()
    print('Сплю 2 минуту')
    time.sleep(120)