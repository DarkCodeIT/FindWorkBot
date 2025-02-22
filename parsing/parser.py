import aiohttp
import asyncio
import time

from random import randint
from typing import AnyStr

from bs4 import BeautifulSoup
from fake_headers import Headers

from const import eng_city_id, data_parsing
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

        else:
            self.old_collection = "vacansy_two"
            self.active_collection = "vacansy"

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
semaphore = asyncio.Semaphore(5)


async def create_tasks_by_filter_city(session: aiohttp.ClientSession, coll) -> list:
    tasks_city = []

    for city in eng_city_id.keys():
        id_city = eng_city_id[city]
        link = f"https://www.enbek.kz/ru/search/vacancy?except[subsidized]=subsidized&region_id={id_city}"
        tasks_city.append(create_tasks_to_page(id_city=id_city, url=link, session=session, coll=coll))

    return tasks_city


async def create_tasks_to_page(id_city: int, url: str, session: aiohttp.ClientSession, coll) -> list:
    tasks_with_pages = []

    try:
        async with semaphore:
            async with session.get(url=url, headers=Headers(headers=True).generate()) as response:
                count = await BS4Tools.get_count_pages(html_page=await response.text())

                for page in range(1, count):
                    link = f"https://www.enbek.kz/ru/search/vacancy?except[subsidized]=subsidized&region_id={id_city}&page={page}"
                    tasks_with_pages.append(create_tasks_to_vacansy(id_city=id_city, url=link, session=session, coll=coll))

                return tasks_with_pages
    except Exception as ex:
        logger.error(f"Can not get pagination on page {url}")
        logger.error(f"{ex}")


async def create_tasks_to_vacansy(id_city: int, url: str, session: aiohttp.ClientSession, repeat: int=3, coll=None) -> list:
    tasks_to_vac = []

    try:
        async with semaphore:
            async with session.get(url=url, headers=Headers(headers=True).generate(), timeout=aiohttp.ClientTimeout(5)) as response:
                #Получаем список блоков в которых есть ссылки на страницу вакансии
                vac = await BS4Tools.get_links_to_vac(await response.text())

                #Вытаскиваем ссылку на вакансию и создаем таски
                for item in vac:
                    link = f"https://www.enbek.kz{await BS4Tools.get_href(item)}"
                    tasks_to_vac.append(get_vacansy(id_city=id_city, url=link, session=session, coll=coll))

                return tasks_to_vac

    except Exception as ex:
        logger.error(f"Can not get urls to vacansy on page {url}")
        logger.error(f"{ex}")
        if repeat > 0:
            logger.info("TRY AGAIN GO SLEEP\n\n")
            await asyncio.sleep(randint(2, 5))
            await create_tasks_to_vacansy(id_city, url, session, repeat-1, coll=coll)


async def get_vacansy(id_city: int, url: str, session: aiohttp.ClientSession, repeat: int=3, coll=None):

    try:
        async with semaphore:
            async with session.get(url=url, headers=Headers(headers=True).generate(), timeout=aiohttp.ClientTimeout(5)) as response:
                vac = await BS4Tools.get_vacansy_details(html_page=await response.text(), id_city=id_city, url=url)
    except Exception as ex:
        logger.error(f"Can not get details abount vacansy url is {url}")
        logger.error(f"{ex}")

    try:
        if vac is not None:
            coll.insert_one(vac)
        # data_parsing.append(data)
            logger.info("DATA SAVED")
    except Exception as ex:
        logger.error(f"Can not upload data to db: data is NONE\nActive collection is {dynamic_collection.active_collection}")
        logger.error(f"{ex}")
        if repeat > 0:
            logger.info("TRY AGAIN GO SLEEP\n\n")
            await asyncio.sleep(2, 5)
            await get_vacansy(id_city, url, session, repeat-1, coll=coll)


async def point_run():
    #Получаем коллекцию в которую будем сохранять данные
    await dynamic_collection.update_active_collection()

    #Создание сессии для всех запросов на сервер
    session = aiohttp.ClientSession()
    collection_, connection_ = await db_service.loading_collection(dynamic_collection.active_collection)

    #Получение тасков на нахождения вакансий в городах
    tasks_by_city = await create_tasks_by_filter_city(session, collection_)
    logger.info("TASK BY CITY IS HAVE RUN TASKS WITH 10 URLS\n")

    for task_c in tasks_by_city:
        #Запуск поиска количества страниц по данному городу(task_c) и получение корутин(create_tasks_to_vacansy)
        tasks_with_pages_with_ten = await task_c
        logger.info("Task to page with vac is recived\n")

        #Запуск полученных ранее корутин из которых мы получим список последних заданий(get_vacansy)
        logger.info("Starting tasks 'page with vac'\n")
        last_tasks = await asyncio.gather(*tasks_with_pages_with_ten)
        logger.info("Last tasks is recived\n")

        #Делаем паузы чтобы, уменьшить риск бана IP
        time_sleep = randint(60, 120)
        logger.info(f"Freezing the code on time{time_sleep}\n")
        await asyncio.sleep(time_sleep)

        #Теперь запускаем последние корутины и сохраняем данные в БД
        logger.info("Running code pending last tasks\n")
        last = set()

        #Распаковываем список со списками в которых лежит по 10 корутин
        for item in last_tasks:
            if item is not None:
                for item_task in item:
                    last.add(item_task)

        logger.info("Starting Last tasks\n")
        await asyncio.gather(*last)

        # Делаем паузы, чтобы уменьшить риск блокировки IP
        time_sleep = randint(120, 200)
        logger.info(f"Freezing the code on time{time_sleep}\n")
        await asyncio.sleep(time_sleep)


    connection_.close()
    #Обновляем активную коллекцию
    collection, connection = await db_service.loading_collection("setting")
    collection.update_one({}, {"$set" : {"active_collection" : dynamic_collection.active_collection}})
    connection.close()

    #Очищаем старую коллекцию
    coll, connection = await db_service.loading_collection(dynamic_collection.old_collection)
    coll.delete_many({})
    connection.close()
    logger.info("DB is cleared")
