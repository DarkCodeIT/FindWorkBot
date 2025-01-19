from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.utils.callback_factory import CallbackCity, CallbackVac
from bot.keyboards.inline_mk import city_level_0, city_level_1, navigation_vac
from bot.keyboards.reply_mk import menu_r
from database.db_service import update_city
from database.statistic import update_peak_city
from logs.logger import get_logger

router_callback = Router(name="Callback_router")
logger = get_logger(__name__)

#Обрабатываем запрос на выбор/изменение города
@router_callback.callback_query(F.data.in_({"change", "chose"}))
async def change_chose_city(query: CallbackQuery):
    await query.message.edit_text(text="В каком городе вы находитесь?", reply_markup=await city_level_0())


#Обрабатываем навигацию каталога всех городов, а так же выбор какого либо города
@router_callback.callback_query(CallbackCity.filter())
async def input_city_nav(query: CallbackQuery, callback_data: CallbackCity):
    if callback_data.action == "Далее":
        await query.message.edit_text(text="Тут есть ваш город?", reply_markup=await city_level_1())

    elif callback_data.action == "Назад":
        await query.message.edit_text(text="Тут есть ваш город?", reply_markup=await city_level_0())

    else:
        user_id = query.from_user.id
        await query.answer()

        try:
            #Загружаем в БД новые данные
            await update_peak_city(new_city=callback_data.action, user_id=user_id)
            await update_city(user_tg_id=user_id, city=callback_data.action)

            await query.message.delete()
            await query.message.answer(text="Теперь можно начинать поиск)", reply_markup=await menu_r())
        except Exception as ex:
            logger.error(f"{ex}")


@router_callback.callback_query(CallbackVac.filter())
async def vacansy(query: CallbackQuery, callback_data: CallbackVac, state: FSMContext):
    #Загружаем данные из Состояния и проверяем есть ли они там
    row_vac = await state.get_data()
    if not row_vac:
        await query.answer(text="Извините я не помню никаких вакансий>_< Попробуйте поиск снова!")
        return

    #Создаем пагинацию
    list_vac = row_vac["DATA_VAC"]
    page_num = int(callback_data.page)

    #Отправляем следующую вакансию
    if callback_data.action == "next":
        page = page_num + 1 if page_num < len(list_vac) else page_num

        #Если вакансия последняя в списке
        if page == len(list_vac):
            await query.answer(text="Это последняя вакансия :(")
            return

        await query.message.edit_text(list_vac[page], reply_markup=await navigation_vac(page=page))
        return

    #Отправляем предыдущую вакансию
    if callback_data.action == "back":
        page = page_num - 1 if page_num > 0 else 0

        #Если вакансия самая первая в списке
        if page == 0:
            await query.answer(text="Вакансии под номером -1, быть не может :/")
            return

        await query.message.edit_text(list_vac[page], reply_markup=await navigation_vac(page=page))
        return

    #Обрабатываем выход из пагинации
    if callback_data.action == "menu":
        await query.message.delete()
        await query.message.answer(text="Для поиска введите 'Search'")
        await state.clear()