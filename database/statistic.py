from database import db_service
from const import name_city_for_statistic, name_city_for_statistic_rev

async def get_count_of_users():
    collection, connection = await db_service.loading_collection("user")
    connection.close()
    return f"Количество пользователей данного бота: {collection.count_documents({})}"


async def get_count_cliks_to_city():
    collection, connection = await db_service.loading_collection("statistic")
    cliks_to_citys = collection.find_one({})

    answer = "Количество пользователей в различных городах:"
    for item in cliks_to_citys.keys():
        if item in ["clicks_to_link_vac", "_id"]:
            continue
        answer += f"\n{name_city_for_statistic_rev[item]} -> {cliks_to_citys[item]}"

    connection.close()
    return answer

async def update_clicks_to_link_vac():
    collection, connection = await db_service.loading_collection("statistic")
    collection.update_one({}, {"$inc" : {"clicks_to_link_vac" : 1}})
    connection.close()

async def update_peak_city(new_city: str, user_id: int):
    user = await db_service.get_user(user_id)
    old_city = user["city"]

    if old_city == new_city:
        return

    collection, connection = await db_service.loading_collection("statistic")
    collection.update_one({}, {"$inc" : {name_city_for_statistic[old_city] : -1}})
    collection.update_one({}, {"$inc" : {name_city_for_statistic[new_city] : 1}})
    connection.close()
