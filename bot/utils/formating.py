async def formating(islist: list) -> list:
    lst_of_vac = []
    lst_of_link = []

    for row in islist:
        vac = f'''Название: {row["title"]}\nЗарплата: {row["salary"]}\nНавыки: {row["skills"]}'''
        lst_of_vac.append(vac)
        lst_of_link.append(row["link"])

    return [lst_of_vac, lst_of_link]