import time
import traceback
import dltv_cyberscore
while True:
    # try:
    #     dltv_cyberscore.get_live_matches()
    # except Exception as e:
    #     error_message = str(e)
    #     # Получаем последний объект трассировки и извлекаем номер строки
    #     tb = traceback.TracebackException.from_exception(e)
    #     frame = tb.stack[-1]
    #     filename = frame.filename
    #     line_no = frame.lineno
    #
    #     error_info = f"Ошибка: {error_message} в файле {filename}, строка {line_no}"
    #
    #     with open('errors.txt', 'r+') as f:
    #         f.write(error_info)
    dltv_cyberscore.get_live_matches()
    print('Сплю 1 минуту')
    time.sleep(60)
