import os

from dotenv import load_dotenv
from pymongo import MongoClient


async def loading_collection(coll_name: str) -> tuple:
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")

    # Подключение к Mongo
    client = MongoClient(mongo_uri)

    # Получение ссылки на БД
    db = client["job"]
    collection = db[coll_name]

    return collection, client

async def insert(data: dict, coll: str):
    collection, connection = await loading_collection(coll)
    collection.insert_one(data)
    connection.close()

async def add_feedback(user_name: str, user_id: int, text: str):
    data = {"user_name": user_name,
                "user_id": user_id,
                "text": text
                }

    await insert(data, "feedbacks")

async def update_city(user_tg_id: int, city: str):
    collection, connection  = await loading_collection(coll_name="user")
    collection.update_one({"user_tg_id" : user_tg_id}, {"$set" : {"city" : city}})
    connection.close()

async def get_user(user_id: int):
    collection, connection = await loading_collection(coll_name="user")
    result = collection.find_one({"user_tg_id" : user_id})
    connection.close()
    return result

async def get_active_collection() -> str:
    collection, connection = await loading_collection(coll_name="setting")
    active_collection = collection.find_one({})
    connection.close()
    return active_collection["active_collection"]

async def get_vacansy(city_id: int, prof: str):
    active_collection = await get_active_collection()
    collection, connection= await loading_collection(coll_name=active_collection)

    result = collection.aggregate([
			{
				"$search" : {
					"index" : "Work",
					"compound" : {
						"must" : [
							{
								"text" :{
										"query" : prof,
										"path" : "title",
										"fuzzy" : {}
								}
							}
						]
					}
				}
			},
			{
				"$match" : {
					"city_id" : city_id
				}
			},
			{
				"$limit" : 100000000000
			}
		])

    connection.close()
    return result