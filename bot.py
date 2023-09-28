import interactions
from interactions import *
import requests
import asyncio
import datetime
from time import sleep
from config import Config, load_config

config: Config = load_config()
TOKEN: str = config.tg_bot.token

bot = interactions.Client(token=TOKEN)

temp = '\n'

weatherButton = Button(style=ButtonStyle.BLURPLE, label='Погода', custom_id='weather')
newsButton = Button(style=ButtonStyle.GREEN, label='Новости', custom_id='news')




@component_callback('weather')
async def wetherCallback(ctx: ComponentContext):
    my_api = 'e360399219f78ea6d3c2db305a00d570'
    lat = '51.2049'
    lon = '58.5668'
    lang = 'ru'
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={my_api}&lang={lang}&units=metric',
    )
    call_json = r.json()
    await ctx.send(
        f'>>> **Общая характеристика погоды:** {call_json["weather"][0]["description"]}{temp}**Температура:** {call_json["main"]["temp"]}С{temp}**По ощущениям:** {call_json["main"]["feels_like"]}C{temp}**Влажность:** {call_json["main"]["humidity"]}%{temp}**Скорость ветра:** {call_json["wind"]["speed"]}м/с{temp}**Атмосферное давление:** {call_json["main"]["pressure"]}гПа'
    )

@component_callback('news')
async def newsCallback(ctx: SlashContext):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
       "country": "ru",
       "apiKey": "759fd39d8eb44f829f210692d4e84d6e"
    }
    r = requests.get(url, params=params)
    call_json = r.json()
    news_data = call_json['articles']
    news_message = ''
    
    for i, article in enumerate(news_data):
        if not i <= 5:
            break
        title = article['author']
        description = article['title']
        link = article['url']
        news_message += f'**{i + 1}. {title}**\n{description}\n[Подробнее]({url})\n'
    await ctx.send(f'>>> {news_message}')
    

@listen()
async def on_startup():
    print(f'{bot.user} активирован')
    for guild in bot.guilds:
        print(
            f'{bot.user} подключен к чату:\n'
            f'{guild.name} (id: {guild.id})'
        )

@slash_command(description='Вызвать меню')
async def menu(ctx: SlashContext):
    await ctx.send('**Меню**', components=[weatherButton, newsButton])

notes = {}

@slash_command(description='Создать заметку')
@slash_option(
    name='title',
    description='Название заметки',
    opt_type=OptionType.STRING,
    min_length=1,
    max_length=50
)
@slash_option(
    name='content',
    description='Тект заметки',
    opt_type=OptionType.STRING
)
async def create_note(ctx: SlashContext, title, content):
    global notes
    if title in notes:
        await ctx.send('Заметка с таким именем уже существует!', delete_after=15)
    else:
        notes[title] = content
        await ctx.send(f'Заметка с названием "{title}" создана')

@slash_command(description='Просмотреть заметку')
@slash_option(
    name='title',
    description='Название заметки',
    opt_type=OptionType.STRING,
    min_length=1,
    max_length=50
)
async def look_note(ctx: SlashContext, title):
    if title in notes:
        await ctx.send(f'**{title}**:\n{notes[title]}')
    else:
        await ctx.send('Заметка с таким именем не существует!', delete_after=15)

@slash_command(description='Удалить заметку')
@slash_option(
    name='title',
    description='Название заметки',
    opt_type=OptionType.STRING,
    min_length=1,
    max_length=50
)
async def delete_note(ctx: SlashContext, title):
    if title in notes:
        del notes[title]
        await ctx.send(f'Заметка с названием "{title}" удалена')
    else:
        await ctx.send('Заметка с таким именем не существует!', delete_after=15)

@slash_command(description='Установить напоминание')
@slash_option(
    name='time',
    description='Время в секундах',
    opt_type=OptionType.INTEGER
)
@slash_option(
    name='reminder',
    description='Текст напоминания',
    opt_type=OptionType.STRING
)
async def remind(ctx: SlashContext, time, reminder):
    try:
        time = int(time)
    except ValueError:
        return await ctx.send('Время должно быть числом!', delete_after=15)
    if time <= 0:
        return await ctx.send('Время должно быть положительным числом!', delete_after=15)
    await ctx.send(f'Хорошо, я напомню вам через {time} секунд о следующем: {reminder}')
    await asyncio.sleep(time)
    await ctx.send(f'{ctx.author.mention}, вот ваше напоминание: {reminder}')

@slash_command(description='Посмотреть время')
async def get_time(ctx: SlashContext):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    await ctx.send(f'Текущее время: {current_time}')

@slash_command(description='Посмотреть дату')
async def get_date(ctx: SlashContext):
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')
    await ctx.send(f'Текущая дата: {current_date}')

minutes = [
    "минута",
    "минуты",
    "минут"
]

secund = [
    "секунд",
    "секунды",
    "секунда"
]

hour = [
    "час",
    "часа",
    "часов"
]


bot.start()