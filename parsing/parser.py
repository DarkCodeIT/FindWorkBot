import aiohttp
import asyncio
import time
from random import randint
from typing import AnyStr

from bs4 import BeautifulSoup
from fake_headers import Headers

from const import eng_city_id
from database import db_service
from logs.logger import get_logger

logger = get_logger(name=__name__)

class DynamicCollection:
    def __init__(self):
        self.active_collection: str = ""
        self.old_collection: str = ""

    async def update_active_collection(self):

        logger.info("Try to get active collection from db")

        collection, connection = await db_service.loading_collection(coll_name="setting")
        data = collection.find_one()["active_collection"]

        if data == "vacansy":
            self.active_collection = "vacansy_two"
            self.old_collection = "vacansy"
            collection.update_one({}, {"$set" : {"active_collection" : "vacansy_two"}})

        else:
            self.old_collection = "vacansy_two"
            self.active_collection = "vacansy"
            collection.update_one({}, {"$set" : {"active_collection" : "vacansy"}})

        logger.info(f"Active collection is {self.active_collection}, close connection")
        connection.close()

class BS4Tools:

    @staticmethod
    async def get_count_pages(html_page: str) -> int:
        soup = BeautifulSoup(html_page, "lxml")
        count_page = soup.find(
            name="div",
            class_="content"
        ).find(
            name="div",
            class_="row"
        ).find(
            name="div",
            class_="col-lg-8 col-xxl-9 position-relative content-search-vacancy"
        ).find(
            name="ul",
            class_="pagination"
        ).find_all(
            name="li",
            class_="page"
        )[-1].text

        return int(count_page)

    @staticmethod
    async def get_links_to_vac(html_page: str) -> list:
        soup = BeautifulSoup(html_page, "lxml")
        links = soup.find(
            name="div",
            class_="content"
        ).find(
            name="div",
            class_="row"
        ).find(
            name="div",
            class_="col-lg-8 col-xxl-9 position-relative content-search-vacancy"
        ).find_all(
            name="div",
            class_="item-list"
        )

        return links

    @staticmethod
    async def get_href(item) -> str:
        href = item.find(
            name="div",
            class_="head"
        ).find(
            name="div",
            class_="title"
        ).find(
            name="a",
            class_="stretched"
        ).get("href")

        return href

    @staticmethod
    async def _get_vacansy_region_skills(single_line) -> tuple[str | AnyStr, str | AnyStr]:
        skills = ""
        region = ""

        for line in single_line:

            if line.find("div", class_="label").text == "Профессиональные навыки":
                row_line = line.find("div", class_="value").text.split(";")

                for i in range(len(row_line)):
                    if i == len(row_line) - 1:
                        skills += row_line[i].replace("\n", "").strip()
                        break

                    skills += row_line[i].replace("\n", "").strip() + "\n"

            if line.find("div", class_="label").text == "Регион":
                region += line.find("div", class_="value").text.replace("\n", "").strip()

        return region, skills

    @staticmethod
    async def get_vacansy_details(html_page: str, id_city: int, url: str) -> dict[str, str | AnyStr | int]:
        soup = BeautifulSoup(html_page, "lxml")

        main = soup.find(
            name="div",
            class_="content"
        ).find(
            name="div",
            class_="row"
        ).find(
            name="div",
            class_="bordered-box item mb-3"
        )

        title = main.find(
            name="h4",
            class_="title"
        ).text.strip()

        date_of_pub = main.find(
            name="ul",
            class_="info small mb-2"
        ).text.strip()

        salary = main.find(
            name="div",
            class_="price"
        ).text.strip()

        single_line = main.find(
            name="div",
            class_="text"
        ).find_all(
            name="div",
            class_="single-line"
        )

        region, skills = await BS4Tools._get_vacansy_region_skills(single_line)

        return {
            "city_id" : id_city,
            "title" : title,
            "salary" : salary,
            "publis" : date_of_pub,
            "skills" : skills,
            "region" : region,
            "link" : url
        }

#Создание классов (создаем вне функции, чтобы иметь доступ к этим классам в других функциях без глобального объявления)
dynamic_collection = DynamicCollection()
semaphore = asyncio.Semaphore(60)

async def create_tasks_by_filter_city(session: aiohttp.ClientSession) -> list:
    tasks_city = []

    for city in eng_city_id.keys():
        id_city = eng_city_id[city]
        link = f"https://www.enbek.kz/ru/search/vacancy?except[subsidized]=subsidized&region_id={id_city}"
        tasks_city.append(create_tasks_to_page(id_city=id_city, url=link, session=session))

    return tasks_city


async def create_tasks_to_page(id_city: int, url: str, session: aiohttp.ClientSession) -> list:
    tasks_with_pages = []

    try:
        async with semaphore:
            async with session.get(url=url, headers=Headers(headers=True).generate()) as response:
                count = await BS4Tools.get_count_pages(html_page=await response.text())

                for page in range(1, count):
                    link = f"https://www.enbek.kz/ru/search/vacancy?except[subsidized]=subsidized&region_id={id_city}&page={page}"
                    tasks_with_pages.append(create_tasks_to_vacansy(id_city=id_city, url=link, session=session))

                return tasks_with_pages
    except Exception as ex:
        logger.error(f"Can not get pagination on page {url}")
        logger.error(f"{ex}")


async def create_tasks_to_vacansy(id_city: int, url: str, session: aiohttp.ClientSession) -> list:
    tasks_to_vac = []

    try:
        async with semaphore:
            async with session.get(url=url, headers=Headers(headers=True).generate()) as response:
                #Получаем список блоков в которых есть ссылки на страницу вакансии
                vac = await BS4Tools.get_links_to_vac(await response.text())

                #Вытаскиваем ссылку на вакансию и создаем таски
                for item in vac:
                    link = f"https://www.enbek.kz{await BS4Tools.get_href(item)}"
                    tasks_to_vac.append(get_vacansy(id_city=id_city, url=link, session=session))

                return tasks_to_vac

    except Exception as ex:
        logger.error(f"Can not get urls to vacansy on page {url}")
        logger.error(f"{ex}")

async def get_vacansy(id_city: int, url: str, session: aiohttp.ClientSession):

    try:
        async with semaphore:
            async with session.get(url=url, headers=Headers(headers=True).generate()) as response:
                data = await BS4Tools.get_vacansy_details(html_page=await response.text(), id_city=id_city, url=url)
    except Exception as ex:
        logger.error(f"Can not get details abount vacansy url is {url}")
        logger.error(f"{ex}")

    try:
        await db_service.insert(data=data, coll=dynamic_collection.active_collection)
    except Exception as ex:
        logger.error(f"Can not upload data to db: data is {data}\nActive collection is {dynamic_collection.active_collection}")
        logger.error(f"{ex}")


async def point_run():
    #Получаем коллекцию в которую будем сохранять данные
    await dynamic_collection.update_active_collection()
    print("lihsfdjkosfpklm")
    #Создаем таймаут на http запросы если в течение
    #этого временя запрос не выполнится то он отменится
    timeout = aiohttp.ClientTimeout(total=20)

    #Создание сессии для всех запросов на сервер
    session = aiohttp.ClientSession(timeout=timeout)

    #Получение тасков на нахождения вакансий в городах
    tasks_by_city = await create_tasks_by_filter_city(session)

    logger.info("Tasks filtering by city is recived")
    logger.info("Starting tasks for every city")

    for task_c in tasks_by_city:
        start_time = time.time()
        #Запуск поиска количества страниц по данному городу(task_c) и получение корутин(create_tasks_to_vacansy)
        tasks_with_pages_with_ten = await task_c
        logger.info("Task to page with vac is recived")

        #Запуск полученных ранее корутин из которых мы получим список последних заданий(get_vacansy)
        logger.info("Starting tasks 'page with vac'")
        last_tasks = await asyncio.gather(*tasks_with_pages_with_ten)
        logger.info("Last tasks is recived")

        #Делаем паузы чтобы, уменьшить риск бана IP
        time_sleep = randint(60, 120)
        logger.info(f"Freezing the code on time{time_sleep}\n")
        await asyncio.sleep(time_sleep)

        #Теперь запускаем последние корутины и сохраняем данные в БД
        logger.info("Running code pending last tasks")
        last = set()

        #Распаковываем список со списками в которых лежит по 10 корутин
        for item in last_tasks:
            if item is not None:
                for item_task in item:
                    last.add(item_task)

        logger.info("Starting Last tasks")
        await asyncio.gather(*last)
        end_time = time.time()
        logger.info(f"Speed work is {end_time-start_time}")

        # Делаем паузы, чтобы уменьшить риск блокировки IP
        time_sleep = randint(120, 200)
        logger.info(f"Freezing the code on time{time_sleep}\n")
        await asyncio.sleep(time_sleep)


    #Очищаем старую коллекцию
    coll, connection = await db_service.loading_collection(dynamic_collection.old_collection)
    coll.delete_many({})
    connection.close()
    logger.info("DB is cleared")
