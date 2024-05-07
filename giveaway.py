import time

import requests
import json
url = 'https://egb.com/giveaways'
headers = {
    "Host": "egb.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "X-CSRF-Token": "UUu1IL8sY0iZFFc2_FYI4ICk-WT34IRRGjz19DND8CbKEJZ9zTvbeAdcw72OYEecZiDlBaZimaYP-VuJwtmkAQ",
    "DNT": "1",
    "Sec-GPC": "1",}
id = 45176
while True:
    id += 1
    data = {
        'giveaway_id': id
    }
    response = requests.post(url=url, json=data, headers=headers)
    if response.status_code == 200:
        answer = json.loads(response.text)
        print(answer)