async def formating(islist: list) -> list:
    lst_of_vac = []
    for row in islist:
        vac = f'''Название: {row["title"]}\nЗарплата: {row["salary"]}\nНавыки: {row["skills"]}'''
        lst_of_vac.append(vac)

    return lst_of_vac