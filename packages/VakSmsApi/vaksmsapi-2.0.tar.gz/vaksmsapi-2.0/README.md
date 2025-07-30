# VAKSMS API for Python 3

<div align="center">

[![lolkof - SYNKVAKSMS](https://img.shields.io/static/v1?label=lolkof&message=SYNKVAKSMS&color=blue&logo=github)](https://github.com/lolkofka/syncvaksms "Go to GitHub repo")

[VAKSMS Official documentation](https://vak-sms.com/api/vak/)

ПОЖАЛУЙСТА ИСПОЛЬЗУЙТЕ https://pypi.org/project/syncvaksms/
СТАРАЯ ВЕРСИЯ ЭТОЙ БИБЛИОТЕКИ ПОДДЕРЖИВАЕТЬСЯ НЕ ПОЛНОСТЬЮ И НЕ РЕКОМЕНДУЕТСЯ

Так же есть асинхронная версия библиотеки https://pypi.org/project/aiovaksms/

</div>

## About

Это библиотека по https://vak-sms.com/api/vak/ API **от энтузиастов**. Все методы проверены и
**соответствуют** оффициальной документации:
https://vak-sms.com/api/vak/
Возвращает pydantic объекты. Пожалуйста по предложениям и ошибкам 
пишите сюда [issues](https://github.com/lolkofka/syncvaksms)

API обновленно на *06 Июля 2025*.

* PyPl - https://pypi.org/project/syncvaksms/
* Github - https://github.com/lolkofka/syncvaksms
* Requirements: Python >= 3.10

## Установка библиотеки

* Установи с помощью pip: `pip install VakSmsApi` # Эту библиотеку
* Установи с помощью pip: `pip install syncvaksms` # Рекомендую

* Загрузить исходники - `git clone https://github.com/lolkofka/syncvaksms`

## Начало работы

### Первые шаги (как лучше всего использовать)

```python
from VakSmsApi import VakSmsApi


def main():
    client = VakSmsApi('TOKEN') # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net') # работает в росси

    # Покупка номера
    number = client.get_number('ya')
    print(number.tel)  # 79995554433

    # ожидание смс кода (библиотека сама ждёт пока прийдёт смс код)
    sms_code = number.wait_sms_code(timeout=300, per_attempt=5) # Не обязательно указывать timeout и per_attempt
    print(sms_code) #1234

    # указание статуса
    number.set_status('end')
    # bad - забанить номер
    # end - отменить номер
    # send - ожидать новую смс


main()
```

### Получить баланс токена

```python


from VakSmsApi import VakSmsApi


def main():
    client = VakSmsApi('TOKEN') # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net') # работает в россим
    balances = client.get_balance()
    print(balances)  # balance = 100.0


main()
```

### Узнать количество доступных к покупке номеров

```python


from VakSmsApi import VakSmsApi

def main():
    client = VakSmsApi('TOKEN') # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net') # работает в россим
    
    data = client.get_count_number('cp')
    print(data)  # service='cp' count=4663 price=18.0


main()
```

### Получить список стран

```python


from VakSmsApi import VakSmsApi


def main():
    client = VakSmsApi('TOKEN') # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net') # работает в россим
    data = client.get_country_list()
    print(data)  # [CountryOperator(countryName='Tajikistan', countryCode='tj', operatorList=['babilon mobile', 'beeline', 'megafon', 'tcell']), CountryOperator(countryName='Zimbabwe', countryCode='zw', operatorList=['econet', 'netone', 'telecel'])... ]


main()
```

### Купить номер

```python


from VakSmsApi import VakSmsApi


def main():
    client = VakSmsApi('TOKEN') # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net') # работает в россим
    data = client.get_number('ya')
    
    # Эксклюзивная функция этой и syncvaksms библиотеки для получения времени жизни номера
    # все известные сервисы, время жизни которых отличается от стандартных 20 минут
    # включены в базу данных библиотеки по состоянию на 06.07.2025
    # также работают с параметром "rent=True"
    print(data.lifetime) # 1200 Оставшееся время жизни номера
    print(data.lives_up_to) # 1727823949 unix время смерти номера
    
    print(data)  # tel=79296068469 service='ya' idNum='1725546315697382' lifetime=1200 lives_up_to=1727823949


main()
```

### Получение смс кода (устаревшее, лучше используйте wait_sms_code)

```python


from VakSmsApi import VakSmsApi


def main():
    client = VakSmsApi('TOKEN')  # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net')  # работает в россим
    data = client.get_sms_code('1725546315697382') # 1725546315697382 is number id (idNum)
    print(data)  # smsCode='1234'


main()
```

### Запрос новой смс

```python


from VakSmsApi import VakSmsApi


def main():
    client = VakSmsApi('TOKEN') # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net') # работает в россим
    data = client.set_status('1725546315697382', 'send') # 1725546315697382 is number id (idNum)
    print(data)  # ready


main()
```

### Получить полное имя сервиса информацию и иконки
### Этого метода нет в оффициальной документации vaksms

```python


from VakSmsApi import VakSmsApi


def main():
    client = VakSmsApi('TOKEN') # используется vaksms.com домен (не работает в россии)
    client = VakSmsApi('TOKEN', base_url='https://moresms.net') # работает в россим
    data = client.get_count_number_list()
    print(data)  # {'mr': Service(name='VK - MailRu', icon='https://vak-sms.com/static/service/mr.png', info='Тут можно принять смс от сервисов VKGroup.Не забывайте проверять номера на занятость через восстановление. Подробнее в базе знаний - https://bit.ly/3M6tXup', cost=22.0, rent=False, quantity=41153, private=False), ... }
    print(data['mr'].name) # VK - MailRu
    

main()
```

## Contact

* E-Mail - lolkofprog@gmail.com
* Telegram - [@lolkof](https://t.me/lolkof)

## License

Released under [GPL](/LICENSE) by [@lolkofka](https://github.com/AioSmsProviders).