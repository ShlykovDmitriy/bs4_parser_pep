

# **Проект парсинга** 

## Описание
___
Парсинг может получать информацию об обновлении python, версии python, скачивать фаил в zip формате и выводить таблице с актуальными статусами PEP. Информацию можно вывести в терминал, таблицей в терминале или файлом.
___
## Технологии
___
-  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
-  [![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-3776AB)](https://www.crummy.com/software/BeautifulSoup/)



___
## Установка и запуск
___
1. Склонируйте репозиторий на свой компьютер:
```bash 
git clone git@github.com:ShlykovDmitriy/bs4_parser_pep.git
```

2. Создайте виртуальное окружение в корне проекта и активируйте его :

```bash 
python -m venv venv
source venv/bin/activate
```

3. Установите зависимости :


```bash
pip install -r requirements.txt
``` 


4. Запуск программы:

для Linux 
```bash
python src/main.py <парсер> <аргумент по необходимости>
```
Парсеры:
- whats-new  - выдаст статьи и авторов обновлений питона
- latest-versions  - выдаст версии питона
- download - скачает фаил питона
- pep - выдаст таблицу со списком актуальных статусов PEP и их количество

Аргументы:
-h, --help            show this help message and exit
-c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}


___
### Автор
___
[Шлыков Дмитрий](https://github.com/ShlykovDmitriy)