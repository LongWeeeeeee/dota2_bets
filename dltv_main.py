import time
import traceback
from dltv_cyberscore import get_team_positions, dota2protracker
while True:
    try:
        result = get_team_positions()
        if result is not None:
            radiant_heroes_and_pos, dire_heroes_and_pos, radiant_team_name, dire_team_name, url, score = result
            print(f'{radiant_team_name} VS {dire_team_name}')
            dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                            dire_heroes_and_positions=dire_heroes_and_pos, radiant_team_name=radiant_team_name,
                            dire_team_name=dire_team_name, score=score, antiplagiat_url=url, only_good_bets=True)
    except Exception as e:
        error_message = str(e)
        # Получаем последний объект трассировки и извлекаем номер строки
        tb = traceback.TracebackException.from_exception(e)
        frame = tb.stack[-1]
        filename = frame.filename
        line_no = frame.lineno

        error_info = f"Ошибка: {error_message} в файле {filename}, строка {line_no}"

        with open('errors.txt', 'r+') as f:
            f.write(error_info)
    print('Сплю 2 минуты')
    time.sleep(120)