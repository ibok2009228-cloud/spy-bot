"""
🕵️ TELEGRAM БОТ "ШПИОН" - СТАТИСТИКА ОНЛАЙНА
"""

import asyncio
import random
import logging
import json
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

# ==================== НАСТРОЙКИ ====================

BOT_TOKEN = "8090010535:AAEsAeC1LtfKzSbvLcRaugca0mNC2I8_Paw"
ADMIN_ID = 5560558079  # ← ТВОЙ ID

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== СТАТИСТИКА ====================

class StatsManager:
    def __init__(self, filename="bot_stats.json"):
        self.filename = filename
        self.daily_stats = defaultdict(lambda: {
            "unique_users": set(),
            "games_started": 0,
            "games_finished": 0,
            "commands_used": defaultdict(int)
        })
        self.load_stats()
    
    def load_stats(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for date, stats in data.items():
                        stats["unique_users"] = set(stats.get("unique_users", []))
                        stats["commands_used"] = defaultdict(int, stats.get("commands_used", {}))
                        self.daily_stats[date] = stats
            except:
                pass
    
    def save_stats(self):
        data = {}
        for date, stats in self.daily_stats.items():
            data[date] = {
                "unique_users": list(stats["unique_users"]),
                "games_started": stats["games_started"],
                "games_finished": stats["games_finished"],
                "commands_used": dict(stats["commands_used"]),
                "total_unique": len(stats["unique_users"])
            }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def log_user(self, user_id: int):
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[today]["unique_users"].add(user_id)
        self.save_stats()
    
    def log_command(self, command: str):
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[today]["commands_used"][command] += 1
        self.save_stats()
    
    def log_game_start(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[today]["games_started"] += 1
        self.save_stats()
    
    def log_game_end(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[today]["games_finished"] += 1
        self.save_stats()
    
    def get_stats(self, days: int = 7):
        result = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.daily_stats:
                stats = self.daily_stats[date].copy()
                stats["date"] = date
                stats["unique_users_count"] = len(stats["unique_users"])
                del stats["unique_users"]
                result.append(stats)
        return result

stats_manager = StatsManager()

# ==================== КАТЕГОРИИ ====================

CATEGORIES = {
    "еда": "🍔 Еда",
    "животное": "🐾 Животные",
    "место": "📍 Места",
    "профессия": "💼 Профессии",
    "транспорт": "🚗 Транспорт",
    "бравл старс": "🎮 Бравл Старс",
    "клеш рояль": "⚔️ Клеш Рояль",
    "футбол": "⚽ Футбол",
    "спорт": "🏆 Спорт",
    "техника": "📱 Техника",
    "музыка": "🎵 Музыка",
    "кино": "🎬 Кино",
    "абсолютный рандом": "🎲 Абсолютный рандом",
}

# ==================== БАЗА ДАННЫХ СЛОВ (БЕЗ ИЗМЕНЕНИЙ) ====================

WORDS_DATABASE: Dict[str, Dict[str, List[tuple]]] = {
    "еда": {
        "easy": [("пицца", "еда"), ("бургер", "еда"), ("суши", "еда"), ("шоколад", "еда"), ("мороженое", "еда"), 
                 ("кола", "еда"), ("чипсы", "еда"), ("пельмени", "еда"), ("блины", "еда"), ("картошка фри", "еда"),
                 ("хот-дог", "еда"), ("сэндвич", "еда"), ("пончик", "еда"), ("пирог", "еда"), ("торт", "еда"),
                 ("печенье", "еда"), ("конфета", "еда"), ("жвачка", "еда"), ("чипсы лейс", "еда"), ("сникерс", "еда"),
                 ("марс", "еда"), ("твикс", "еда"), ("кит-кат", "еда"), ("орео", "еда"), ("пепси", "еда"),
                 ("фанта", "еда"), ("спрайт", "еда"), ("ред-булл", "еда"), ("сок", "еда"), ("молоко", "еда"),
                 ("кефир", "еда"), ("ряженка", "еда"), ("сметана", "еда"), ("творог", "еда"), ("сыр", "еда"),
                 ("колбаса", "еда"), ("сосиска", "еда"), ("ветчина", "еда"), ("балык", "еда"), ("икра", "еда"),
                 ("хлеб", "еда"), ("булка", "еда"), ("батон", "еда"), ("лаваш", "еда"), ("пита", "еда")],
        "medium": [("фалафель", "еда"), ("гаспачо", "еда"), ("рататуй", "еда"), ("паэлья", "еда"), ("борщ", "еда"), 
                   ("плов", "еда"), ("хачапури", "еда"), ("долма", "еда"), ("кутаб", "еда"), ("чахохбили", "еда"),
                   ("хинкали", "еда"), ("шаурма", "еда"), ("тако", "еда"), ("буррито", "еда"), ("начос", "еда"),
                   ("гамбургер", "еда"), ("чизбургер", "еда"), ("биг-мак", "еда"), ("воппер", "еда"), ("лонгер", "еда"),
                   ("наггетсы", "еда"), ("стрипсы", "еда"), ("крылышки", "еда"), ("фри картофель", "еда"), ("кольца кальмара", "еда"),
                   ("цезарь", "еда"), ("греческий салат", "еда"), ("оливье", "еда"), ("селедка под шубой", "еда"), ("мимоза", "еда"),
                   ("окрошка", "еда"), ("солянка", "еда"), ("щи", "еда"), ("рассольник", "еда"), ("уха", "еда"),
                   ("котлета", "еда"), ("бефстроганов", "еда"), ("пельмени сибирские", "еда"), ("вареники", "еда"), ("макароны", "еда"),
                   ("спагетти", "еда"), ("паста", "еда"), ("лазанья", "еда"), ("ризотто", "еда"), ("кус-кус", "еда")],
        "hard": [("фуагра", "еда"), ("эскарго", "еда"), ("круассан", "еда"), ("багет", "еда"), ("тирамису", "еда"), 
                 ("панакота", "еда"), ("бриошь", "еда"), ("крем брюле", "еда"), ("макарон", "еда"), ("фондю", "еда"),
                 ("рататуй прованский", "еда"), ("буйабес", "еда"), ("касуле", "еда"), ("гратен", "еда"), ("террин", "еда"),
                 ("парфе", "еда"), ("суфле", "еда"), ("мусс", "еда"), ("ганаш", "еда"), ("кулинарный шоколад", "еда"),
                 ("трюфель шоколадный", "еда"), ("пралине", "еда"), ("нуга", "еда"), ("марципан", "еда"), ("пастила", "еда"),
                 ("рахат-лукум", "еда"), ("халва", "еда"), ("щербет", "еда"), ("гранита", "еда"), ("сорбет", "еда"),
                 ("семифредо", "еда"), ("тирамису классическое", "еда"), ("панна-котта", "еда"), ("крем-карамель", "еда"), ("флан", "еда"),
                 ("чуррос", "еда"), ("бунуэло", "еда"), ("тортилья", "еда"), ("фахитас", "еда"), ("кесадилья", "еда"),
                 ("гуакамоле", "еда"), ("сальса", "еда"), ("песто", "еда"), ("ткемали", "еда"), ("аджика", "еда")]
    },
    "животное": {
        "easy": [("собака", "животное"), ("кошка", "животное"), ("слон", "животное"), ("тигр", "животное"), ("лев", "животное"), 
                 ("медведь", "животное"), ("заяц", "животное"), ("волк", "животное"), ("лиса", "животное"), ("обезьяна", "животное"),
                 ("корова", "животное"), ("свинья", "животное"), ("овца", "животное"), ("коза", "животное"), ("лошадь", "животное"),
                 ("курица", "животное"), ("утка", "животное"), ("гусь", "животное"), ("индейка", "животное"), ("петух", "животное"),
                 ("мышь", "животное"), ("крыса", "животное"), ("хомяк", "животное"), ("морская свинка", "животное"), ("кролик", "животное"),
                 ("белка", "животное"), ("ежик", "животное"), ("крот", "животное"), ("бобр", "животное"), ("дикобраз", "животное"),
                 ("еж", "животное"), ("змея", "животное"), ("ящерица", "животное"), ("крокодил", "животное"), ("черепаха", "животное"),
                 ("лягушка", "животное"), ("жаба", "животное"), ("тритон", "животное"), ("саламандра", "животное"), ("улитка", "животное"),
                 ("слизняк", "животное"), ("червь", "животное"), ("гусеница", "животное"), ("бабочка", "животное"), ("мотылек", "животное")],
        "medium": [("енот", "животное"), ("барсук", "животное"), ("выдра", "животное"), ("сурикат", "животное"), ("панда", "животное"), 
                   ("коала", "животное"), ("кенгуру", "животное"), ("носорог", "животное"), ("бегемот", "животное"), ("жираф", "животное"),
                   ("зебра", "животное"), ("антилопа", "животное"), ("газель", "животное"), ("импала", "животное"), ("гну", "животное"),
                   ("бизон", "животное"), ("буйвол", "животное"), ("як", "животное"), ("лама", "животное"), ("альпака", "животное"),
                   ("викунья", "животное"), ("гепард", "животное"), ("леопард", "животное"), ("ягуар", "животное"), ("пума", "животное"),
                   ("рысь", "животное"), ("карликовая пантера", "животное"), ("сервал", "животное"), ("каракал", "животное"), ("манул", "животное"),
                   ("фенек", "животное"), ("шакал", "животное"), ("гиена", "животное"), ("гепард", "животное"), ("леопард", "животное"),
                   ("орангутан", "животное"), ("горилла", "животное"), ("шимпанзе", "животное"), ("бонобо", "животное"), ("гиббон", "животное"),
                   ("лемур", "животное"), ("индри", "животное"), ("ай-ай", "животное"), ("тарсиер", "животное"), ("мартышка", "животное")],
        "hard": [("тапир", "животное"), ("капибара", "животное"), ("панголин", "животное"), ("окапи", "животное"), ("аксолотль", "животное"), 
                 ("нарвал", "животное"), ("какаду", "животное"), ("тюлень", "животное"), ("дельфин", "животное"), ("орка", "животное"),
                 ("касатка", "животное"), ("морж", "животное"), ("тюлень-монах", "животное"), ("северный морской котик", "животное"), ("южный морской слон", "животное"),
                 ("дюгонь", "животное"), ("ламантин", "животное"), ("кит синий", "животное"), ("кит горбатый", "животное"), ("кит кашалот", "животное"),
                 ("белуха", "животное"), ("нарвал", "животное"), ("ваquita", "животное"), ("дельфин речной", "животное"), ("дельфин морской", "животное"),
                 ("белобрюхий дельфин", "животное"), ("косатка", "животное"), ("гринда", "животное"), ("малая косатка", "животное"), ("белуха", "животное"),
                 ("пингвин императорский", "животное"), ("пингвин аделие", "животное"), ("пингвин антарктический", "животное"), ("пингвин галапагосский", "животное"), ("альбатрос", "животное"),
                 ("буревестник", "животное"), ("пеликан", "животное"), ("баклан", "животное"), ("чайка", "животное"), ("пингвин", "животное"),
                 ("страус", "животное"), ("эму", "животное"), ("касуар", "животное"), ("киви", "животное"), ("нанду", "животное")]
    },
    "место": {
        "easy": [("школа", "место"), ("больница", "место"), ("магазин", "место"), ("кинотеатр", "место"), ("парк", "место"), 
                 ("пляж", "место"), ("город", "место"), ("деревня", "место"), ("ресторан", "место"), ("стадион", "место"),
                 ("дом", "место"), ("квартира", "место"), ("офис", "место"), ("завод", "место"), ("фабрика", "место"),
                 ("банк", "место"), ("почта", "место"), ("библиотека", "место"), ("музей", "место"), ("театр", "место"),
                 ("цирк", "место"), ("зоопарк", "место"), ("аквапарк", "место"), ("бассейн", "место"), ("спортзал", "место"),
                 ("поликлиника", "место"), ("аптека", "место"), ("салон красоты", "место"), ("парикмахерская", "место"), ("барбершоп", "место"),
                 ("кафе", "место"), ("бар", "место"), ("клуб", "место"), ("дискотека", "место"), ("караоке", "место"),
                 ("отель", "место"), ("гостиница", "место"), ("хостел", "место"), ("мотель", "место"), ("кемпинг", "место"),
                 ("дача", "место"), ("сад", "место"), ("огород", "место"), ("поле", "место"), ("лес", "место")],
        "medium": [("библиотека", "место"), ("музей", "место"), ("театр", "место"), ("зоопарк", "место"), ("аквапарк", "место"), 
                   ("бассейн", "место"), ("спортзал", "место"), ("поликлиника", "место"), ("университет", "место"), ("аэропорт", "место"),
                   ("вокзал", "место"), ("порт", "место"), ("метро", "место"), ("автовокзал", "место"), ("трамвайное депо", "место"),
                   ("троллейбусное депо", "место"), ("парковка", "место"), ("гараж", "место"), ("автосервис", "место"), ("заправка", "место"),
                   ("торговый центр", "место"), ("супермаркет", "место"), ("гипермаркет", "место"), ("рынок", "место"), ("базар", "место"),
                   ("склад", "место"), ("логистический центр", "место"), ("таможня", "место"), ("пограничный пункт", "место"), ("визовый центр", "место"),
                   ("суд", "место"), ("прокуратура", "место"), ("полиция", "место"), ("миграционная служба", "место"), ("паспортный стол", "место"),
                   ("загс", "место"), ("нотариус", "место"), ("адвокатская контора", "место"), ("бухгалтерия", "место"), ("аудиторская фирма", "место"),
                   ("архив", "место"), ("картотека", "место"), ("хранилище", "место"), ("сейф", "место"), ("банковская ячейка", "место")],
        "hard": [("обсерватория", "место"), ("крематорий", "место"), ("санаторий", "место"), ("пансионат", "место"), ("хостел", "место"), 
                 ("мотель", "место"), ("вокзал", "место"), ("порт", "место"), ("фуникулер", "место"), ("монорельс", "место"),
                 ("канатная дорога", "место"), ("лифт", "место"), ("эскалатор", "место"), ("траволатор", "место"), ("подземный переход", "место"),
                 ("бункер", "место"), ("убежище", "место"), ("шахта", "место"), ("рудник", "место"), ("карьер", "место"),
                 ("нефтяная вышка", "место"), ("газовая платформа", "место"), ("ветряная электростанция", "место"), ("солнечная электростанция", "место"), ("атомная электростанция", "место"),
                 ("гидроэлектростанция", "место"), ("теплоэлектростанция", "место"), ("электроподстанция", "место"), ("трансформаторная будка", "место"), ("радиовышка", "место"),
                 ("телебашня", "место"), ("сотовая вышка", "место"), ("спутниковая антенна", "место"), ("радар", "место"), ("сонар", "место"),
                 ("лаборатория", "место"), ("чистая комната", "место"), ("изолятор", "место"), ("карантин", "место"), ("биологическая станция", "место")]
    },
    "бравл старс": {
        "easy": [("шелли", "бравл старс"), ("кольт", "бравл старс"), ("булл", "бравл старс"), ("джесси", "бравл старс"), ("брок", "бравл старс"), 
                 ("нита", "бравл старс"), ("динамайк", "бравл старс"), ("эль примо", "бравл старс"), ("леон", "бравл старс"), ("спайк", "бравл старс"),
                 ("кроу", "бравл старс"), ("мортис", "бравл старс"), ("тар", "бравл старс"), ("эмз", "бравл старс"), ("8 бит", "бравл старс"),
                 ("рико", "бравл старс"), ("барли", "бравл старс"), ("поко", "бравл старс"), ("бо", "бравл старс"), ("тик", "бравл старс"),
                 ("дэррил", "бравл старс"), ("пенни", "бравл старс"), ("карл", "бравл старс"), ("фрэнк", "бравл старс"), ("биби", "бравл старс"),
                 ("беззубик", "бравл старс"), ("макс", "бравл старс"), ("мистер пи", "бравл старс"), ("джин", "бравл старс"), ("трофим", "бравл старс")],
        "medium": [("рико", "бравл старс"), ("барли", "бравл старс"), ("поко", "бравл старс"), ("бо", "бравл старс"), ("тик", "бравл старс"), 
                   ("дэррил", "бравл старс"), ("пенни", "бравл старс"), ("карл", "бравл старс"), ("фрэнк", "бравл старс"), ("мортис", "бравл старс"), 
                   ("тара", "бравл старс"), ("джин", "бравл старс"), ("макс", "бравл старс"), ("биби", "бравл старс"), ("беззубик", "бравл старс"),
                   ("вольт", "бравл старс"), ("клео", "бравл старс"), ("фэнг", "бравл старс"), ("базз", "бравл старс"), ("грифф", "бравл старс"),
                   ("гавс", "бравл старс"), ("бонни", "бравл старс"), ("джанет", "бравл старс"), ("отис", "бравл старс"), ("сэм", "бравл старс"),
                   ("бустер", "бравл старс"), ("мэйси", "бравл старс"), ("хэнк", "бравл старс"), ("корделиус", "бравл старс"), ("дублон", "бравл старс")],
        "hard": [("мистер пи", "бравл старс"), ("вольт", "бравл старс"), ("клео", "бравл старс"), ("фэнг", "бравл старс"), ("базз", "бравл старс"), 
                 ("грифф", "бравл старс"), ("гавс", "бравл старс"), ("бонни", "бравл старс"), ("джанет", "бравл старс"), ("отис", "бравл старс"), 
                 ("сэм", "бравл старс"), ("бустер", "бравл старс"), ("мэйси", "бравл старс"), ("хэнк", "бравл старс"), ("корделиус", "бравл старс"), 
                 ("дублон", "бравл старс"), ("пайпер", "бравл старс"), ("пэм", "бравл старс"), ("8 бит", "бравл старс"), ("эмз", "бравл старс"),
                 ("спраут", "бравл старс"), ("вирус", "бравл старс"), ("лу", "бравл старс"), ("гейл", "бравл старс"), ("нани", "бравл старс"),
                 ("сердж", "бравл старс"), ("кольт", "бравл старс"), ("роко", "бравл старс"), ("белль", "бравл старс"), ("скуик", "бравл старс")]
    },
    "клеш рояль": {
        "easy": [("рыцарь", "клеш рояль"), ("гигант", "клеш рояль"), ("минипека", "клеш рояль"), ("вальтир", "клеш рояль"), ("хог", "клеш рояль"), 
                 ("мегарыцарь", "клеш рояль"), ("дракон", "клеш рояль"), ("гоблин", "клеш рояль"), ("шкелет", "клеш рояль"), ("воздушный шар", "клеш рояль"),
                 ("варвары", "клеш рояль"), ("лучницы", "клеш рояль"), ("гоблины", "клеш рояль"), ("копейщики", "клеш рояль"), ("бомбардир", "клеш рояль"),
                 ("кannon", "клеш рояль"), ("мортир", "клеш рояль"), ("тесла", "клеш рояль"), ("инферно", "клеш рояль"), ("башня лучниц", "клеш рояль"),
                 ("король", "клеш рояль"), ("принцесса", "клеш рояль"), ("рыцарь", "клеш рояль"), ("гигант", "клеш рояль"), ("пекка", "клеш рояль"),
                 ("гоблинская бочка", "клеш рояль"), ("минион", "клеш рояль"), ("ведьма", "клеш рояль"), ("всадник на кабане", "клеш рояль"), ("гигантский скелет", "клеш рояль")],
        "medium": [("пекка", "клеш рояль"), ("принц", "клеш рояль"), ("принцесса", "клеш рояль"), ("колдунья", "клеш рояль"), ("электродракон", "клеш рояль"), 
                   ("инферно дракон", "клеш рояль"), ("лава хаунд", "клеш рояль"), ("гральный голем", "клеш рояль"), ("каменный голем", "клеш рояль"), ("бандитка", "клеш рояль"), 
                   ("ночная ведьма", "клеш рояль"), ("электровизард", "клеш рояль"), ("ледяной визард", "клеш рояль"), ("тесла", "клеш рояль"), ("мортир", "клеш рояль"),
                   ("рыбак", "клеш рояль"), ("скелет дракон", "клеш рояль"), ("электрогигант", "клеш рояль"), ("королевский гигант", "клеш рояль"), ("темный принц", "клеш рояль"), 
                   ("охотница", "клеш рояль"), ("палач", "клеш рояль"), ("клон", "клеш рояль"), ("зеркало", "клеш рояль"), ("пушка", "клеш рояль"), 
                   ("ракетница", "клеш рояль"), ("бочка с гоблинами", "клеш рояль"), ("огненный дух", "клеш рояль"), ("ледяной дух", "клеш рояль"), ("электродухи", "клеш рояль")],
        "hard": [("рыбак", "клеш рояль"), ("скелет дракон", "клеш рояль"), ("электрогигант", "клеш рояль"), ("королевский гигант", "клеш рояль"), ("темный принц", "клеш рояль"), 
                 ("охотница", "клеш рояль"), ("палач", "клеш рояль"), ("клон", "клеш рояль"), ("зеркало", "клеш рояль"), ("пушка", "клеш рояль"), 
                 ("ракетница", "клеш рояль"), ("бочка с гоблинами", "клеш рояль"), ("огненный дух", "клеш рояль"), ("ледяной дух", "клеш рояль"), ("электродухи", "клеш рояль"), 
                 ("дровосек", "клеш рояль"), ("королевский свин", "клеш рояль"), ("три мушкетера", "клеш рояль"), ("гоблинская бочка", "клеш рояль"), ("гигантский скелет", "клеш рояль"),
                 ("спарк", "клеш рояль"), ("мега миньон", "клеш рояль"), ("летающая машина", "клеш рояль"), ("боевая рамка", "клеш рояль"), ("здание", "клеш рояль"),
                 ("королевская гвардия", "клеш рояль"), ("элементаль огня", "клеш рояль"), ("элементаль льда", "клеш рояль"), ("дух лечения", "клеш рояль"), ("дух ударов", "клеш рояль")]
    },
    "футбол": {
        "easy": [("роналду", "футбол"), ("месси", "футбол"), ("неймар", "футбол"), ("зидан", "футбол"), ("мбаппе", "футбол"), 
                 ("бекхэм", "футбол"), ("роналдиньо", "футбол"), ("роoney", "футбол"), ("тотти", "футбол"), ("каннаваро", "футбол"),
                 ("марадона", "футбол"), ("пеле", "футбол"), ("круифф", "футбол"), ("платини", "футбол"), ("бест", "футбол"),
                 ("чарльтон", "футбол"), ("эйсебио", "футбол"), ("пушкаш", "футбол"), ("герд мюллер", "футбол"), ("бобби мур", "футбол"),
                 ("йохан кройф", "футбол"), ("франц беккенбауэр", "футбол"), ("марко ван бастен", "футбол"), ("руд гуллит", "футбол"), ("роберто баджо", "футбол"),
                 ("паоло мальдини", "футбол"), ("алессандро дель пьеро", "футбол"), ("габриэль батистута", "футбол"), ("ромарио", "футбол"), ("карлос альберто", "футбол")],
        "medium": [("бензема", "футбол"), ("суарес", "футбол"), ("левандовски", "футбол"), ("холанд", "футбол"), ("гризманн", "футбол"), 
                   ("кроос", "футбол"), ("модрич", "футбол"), ("погба", "футбол"), ("де брюйне", "футбол"), ("ибрагимович", "футбол"), 
                   ("салах", "футбол"), ("мане", "футбол"), ("обамеянг", "футбол"), ("азар", "футбол"), ("касильяс", "футбол"),
                   ("буффон", "футбол"), ("нэймар", "футбол"), ("кавани", "футбол"), ("хигуайн", "футбол"), ("агуэро", "футбол"),
                   ("торрес", "футбол"), ("вилья", "футбол"), ("иниэста", "футбол"), ("хави", "футбол"), ("бускетс", "футбол"),
                   ("рамос", "футбол"), ("пике", "футбол"), ("пуйоль", "футбол"), ("альба", "футбол"), ("алвес", "футбол")],
        "hard": [("марадона", "футбол"), ("пеле", "футбол"), ("круифф", "футбол"), ("платини", "футбол"), ("бест", "футбол"), 
                 ("чарльтон", "футбол"), ("эйсебио", "футбол"), ("пушкаш", "футбол"), ("герд мюллер", "футбол"), ("бобби мур", "футбол"), 
                 ("йохан кройф", "футбол"), ("франц беккенбауэр", "футбол"), ("марко ван бастен", "футбол"), ("руд гуллит", "футбол"), ("роберто баджо", "футбол"), 
                 ("паоло мальдини", "футбол"), ("алессандро дель пьеро", "футбол"), ("габриэль батистута", "футбол"), ("ромарио", "футбол"), ("карлос альберто", "футбол"),
                 ("зико", "футбол"), ("сократес", "футбол"), ("карека", "футбол"), ("карлос", "футбол"), ("роберто карлос", "футбол"),
                 ("кафу", "футбол"), ("роналдо", "футбол"), ("ривалдо", "футбол"), ("роналдиньо", "футбол"), ("адриано", "футбол")]
    },
    "абсолютный рандом": {
        "easy": [],
        "medium": [],
        "hard": []
    }
}

# Дополнительные слова для категории "абсолютный рандом"
RANDOM_WORDS = [
    "стул", "стол", "кровать", "шкаф", "диван", "кресло", "полка", "зеркало", "часы", "лампа",
    "люстра", "торшер", "ночник", "ковер", "шторы", "гардина", "тюль", "покрывало", "одеяло", "подушка",
    "матрас", "простыня", "наволочка", "плед", "полотенце", "салфетка", "скатерть", "посуда", "тарелка", "чашка",
    "кружка", "блюдце", "ложка", "вилка", "нож", "чайник", "кофейник", "кастрюля", "сковорода", "сотейник",
    "блендер", "миксер", "тостер", "микроволновка", "духовка", "плита", "холодильник", "морозилка", "посудомойка", "стиралка",
    "футболка", "рубашка", "блузка", "кофта", "свитер", "джемпер", "пуловер", "кардиган", "пиджак", "жакет",
    "куртка", "пальто", "плащ", "дождевик", "ветровка", "пуховик", "шуба", "полушубок", "жилет", "безрукавка",
    "брюки", "джинсы", "штаны", "шорты", "юбка", "платье", "сарафан", "комбинезон", "костюм", "смокинг",
    "галстук", "бабочка", "шарф", "платок", "шапка", "шляпа", "кепка", "берет", "варежки", "перчатки",
    "дерево", "куст", "трава", "цветок", "роза", "тюльпан", "ромашка", "василек", "одуванчик", "подсолнух",
    "лилия", "орхидея", "кактус", "папоротник", "мох", "гриб", "береза", "дуб", "сосна", "ель",
    "радость", "счастье", "любовь", "нежность", "страсть", "восторг", "восхищение", "удивление", "шок", "испуг",
    ("страх", "абсолютный рандом"), ("ужас", "абсолютный рандом"), ("тревога", "абсолютный рандом"), ("беспокойство", "абсолютный рандом"), ("волнение", "абсолютный рандом"),
    ("время", "абсолютный рандом"), ("пространство", "абсолютный рандом"), ("вселенная", "абсолютный рандом"), ("галактика", "абсолютный рандом"), ("звезда", "абсолютный рандом"),
    ("компьютер", "абсолютный рандом"), ("ноутбук", "абсолютный рандом"), ("планшет", "абсолютный рандом"), ("смартфон", "абсолютный рандом"), ("телефон", "абсолютный рандом"),
    ("велосипед", "абсолютный рандом"), ("самокат", "абсолютный рандом"), ("ролики", "абсолютный рандом"), ("скейтборд", "абсолютный рандом"), ("лонгборд", "абсолютный рандом"),
]

# Заполняем категорию "абсолютный рандом"
for i, word in enumerate(RANDOM_WORDS):
    if i < 300:
        WORDS_DATABASE["абсолютный рандом"]["easy"].append((word, "абсолютный рандом") if isinstance(word, str) else word)
    elif i < 700:
        WORDS_DATABASE["абсолютный рандом"]["medium"].append((word, "абсолютный рандом") if isinstance(word, str) else word)
    else:
        WORDS_DATABASE["абсолютный рандом"]["hard"].append((word, "абсолютный рандом") if isinstance(word, str) else word)

# ==================== КЛАССЫ ====================

class GameState(Enum):
    WAITING = "waiting"
    SELECTING_CATEGORY = "selecting_category"
    SELECTING_DIFFICULTY = "selecting_difficulty"
    SHOWING_WORDS = "showing_words"
    PLAYING = "playing"
    VOTING = "voting"
    SPY_GUESS = "spy_guess"
    FINISHED = "finished"

@dataclass
class Player:
    user_id: int
    username: str
    full_name: str
    is_spy: bool = False
    word: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    votes_received: int = 0
    has_voted: bool = False
    voted_for: Optional[int] = None

@dataclass
class GameRoom:
    chat_id: int
    host_id: int
    host_name: str = ""
    state: GameState = GameState.WAITING
    players: Dict[int, Player] = field(default_factory=dict)
    spy_id: Optional[int] = None
    secret_word: Optional[str] = None
    secret_category: Optional[str] = None
    selected_category: Optional[str] = None
    difficulty: str = "medium"
    turn_order: List[int] = field(default_factory=list)
    current_player_index: int = 0
    votes: Dict[int, int] = field(default_factory=dict)
    descriptions_done: List[int] = field(default_factory=list)
    spy_guess_used: bool = False

# ==================== МЕНЕДЖЕР ====================

class GameManager:
    def __init__(self):
        self.games: Dict[int, GameRoom] = {}
        self.user_games: Dict[int, int] = {}
    
    def create_game(self, chat_id: int, host_id: int, host_name: str, username: str) -> GameRoom:
        game = GameRoom(chat_id=chat_id, host_id=host_id, host_name=host_name)
        game.players[host_id] = Player(
            user_id=host_id,
            username=username,
            full_name=host_name
        )
        self.games[chat_id] = game
        self.user_games[host_id] = chat_id
        return game
    
    def join_game(self, chat_id: int, user_id: int, full_name: str, username: str) -> bool:
        if chat_id not in self.games:
            return False
        game = self.games[chat_id]
        if game.state != GameState.WAITING:
            return False
        if user_id in game.players:
            return False
        
        game.players[user_id] = Player(
            user_id=user_id,
            username=username,
            full_name=full_name
        )
        self.user_games[user_id] = chat_id
        return True
    
    def leave_game(self, chat_id: int, user_id: int) -> bool:
        if chat_id not in self.games:
            return False
        game = self.games[chat_id]
        if user_id not in game.players:
            return False
        
        del game.players[user_id]
        del self.user_games[user_id]
        
        if user_id == game.host_id:
            if game.players:
                new_host = next(iter(game.players.keys()))
                game.host_id = new_host
                game.host_name = game.players[new_host].full_name
            else:
                del self.games[chat_id]
                return True
        return True
    
    def start_game(self, chat_id: int) -> Optional[GameRoom]:
        game = self.games.get(chat_id)
        if not game or len(game.players) < 3:
            return None
        
        words = WORDS_DATABASE.get(game.selected_category, {}).get(game.difficulty, [])
        if not words:
            words = WORDS_DATABASE.get("абсолютный рандом", {}).get("easy", [("слово", "категория")])
        
        word_data = random.choice(words)
        game.secret_word, game.secret_category = word_data
        
        game.spy_id = random.choice(list(game.players.keys()))
        
        for player_id, player in game.players.items():
            if player_id == game.spy_id:
                player.is_spy = True
                player.word = "???"
                player.category = game.secret_category
            else:
                player.is_spy = False
                player.word = game.secret_word
                player.category = game.secret_category
        
        game.turn_order = list(game.players.keys())
        random.shuffle(game.turn_order)
        game.current_player_index = 0
        game.state = GameState.SHOWING_WORDS
        game.descriptions_done = []
        game.spy_guess_used = False
        return game
    
    def get_game_by_user(self, user_id: int) -> Optional[GameRoom]:
        chat_id = self.user_games.get(user_id)
        if chat_id:
            return self.games.get(chat_id)
        return None

game_manager = GameManager()

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def format_lobby_text(game: GameRoom):
    text = f"🎮 <b>Лобби игры 'Шпион'</b>\n\n"
    text += f"👑 Организатор: {game.host_name}\n\n"
    text += "👥 <b>Игроки:</b>\n"
    
    for i, (pid, p) in enumerate(game.players.items(), 1):
        mark = "👑 " if pid == game.host_id else ""
        text += f"{i}. {mark}{p.full_name}\n"
    
    text += f"\n📊 Всего: {len(game.players)} игроков\n"
    
    if len(game.players) < 3:
        text += "\n⚠️ Нужно минимум 3 игрока!"
    else:
        text += "\n✅ Можно начинать!"
    
    return text

def make_lobby_keyboard(chat_id: int, players_count: int):
    buttons = []
    buttons.append([InlineKeyboardButton(text="✅ Присоединиться", callback_data=f"join_{chat_id}")])
    
    if players_count >= 3:
        buttons.append([InlineKeyboardButton(text="🚀 НАЧАТЬ ИГРУ", callback_data=f"start_{chat_id}")])
    
    buttons.append([InlineKeyboardButton(text="❌ Выйти", callback_data=f"leave_{chat_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_category_keyboard(chat_id: int):
    """Клавиатура выбора категории"""
    buttons = []
    categories = list(CATEGORIES.items())
    for i in range(0, len(categories), 2):
        row = []
        for key, name in categories[i:i+2]:
            row.append(InlineKeyboardButton(text=name, callback_data=f"cat_{key}_{chat_id}"))
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_difficulty_keyboard(chat_id: int, category: str):
    """Клавиатура выбора сложности для категории"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Легко", callback_data=f"diff_easy_{category}_{chat_id}"),
            InlineKeyboardButton(text="🟡 Средне", callback_data=f"diff_medium_{category}_{chat_id}"),
            InlineKeyboardButton(text="🔴 Сложно", callback_data=f"diff_hard_{category}_{chat_id}")
        ],
        [InlineKeyboardButton(text="◀️ Назад к категориям", callback_data=f"back_cat_{chat_id}")]
    ])

def get_show_word_keyboard(chat_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Показать моё слово", callback_data=f"myword_{chat_id}")],
    ])

def get_vote_keyboard(game: GameRoom, voter_id: int):
    """Персональная клавиатура для каждого игрока"""
    buttons = []
    for pid, player in game.players.items():
        if pid != voter_id and not player.has_voted:
            votes = player.votes_received
            vote_text = f"👤 {player.full_name}" + (f" ({votes}👎)" if votes > 0 else "")
            buttons.append([InlineKeyboardButton(text=vote_text, callback_data=f"vote_{game.chat_id}_{pid}_{voter_id}")])
    
    if not buttons:
        return None
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ==================== КОМАНДЫ ====================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Логируем пользователя
    stats_manager.log_user(message.from_user.id)
    stats_manager.log_command("start")
    
    await message.answer(
        "🕵️ <b>Добро пожаловать в 'Шпион'!</b>\n\n"
        "Добавь меня в группу и напиши /game",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("game"))
async def cmd_game(message: types.Message):
    chat_id = message.chat.id
    user = message.from_user
    
    # Логируем
    stats_manager.log_user(user.id)
    stats_manager.log_command("game")
    
    if message.chat.type == "private":
        await message.answer("❌ Только в группах!")
        return
    
    if chat_id in game_manager.games:
        del game_manager.games[chat_id]
    
    game = game_manager.create_game(
        chat_id=chat_id,
        host_id=user.id,
        host_name=user.full_name,
        username=user.username or user.full_name
    )
    
    await message.answer(
        format_lobby_text(game),
        parse_mode=ParseMode.HTML,
        reply_markup=make_lobby_keyboard(chat_id, len(game.players))
    )

@dp.message(Command("rules"))
async def cmd_rules(message: types.Message):
    stats_manager.log_command("rules")
    
    await message.answer("""
📜 <b>ПРАВИЛА:</b>
• Выбираем категорию и сложность
• Нажми "Показать моё слово" — увидишь слово ТОЛЬКО ТЫ
• Описывай слово когда хочешь (последовательности нет!)
• Любой игрок может начать голосование командой /vote
• Шпион угадывает слово командой /guess [твоё слово] (1 попытка!)
""", parse_mode=ParseMode.HTML)

@dp.message(Command("vote"))
async def cmd_vote(message: types.Message):
    """Любой игрок может начать голосование"""
    chat_id = message.chat.id
    user = message.from_user
    
    stats_manager.log_command("vote")
    
    game = game_manager.games.get(chat_id)
    if not game or game.state not in [GameState.PLAYING, GameState.SHOWING_WORDS]:
        await message.answer("❌ Игра не идёт!")
        return
    
    if user.id not in game.players:
        await message.answer("❌ Ты не в игре!")
        return
    
    await start_voting(chat_id, game)

# ==================== КОМАНДА СТАТИСТИКИ (ТОЛЬКО ДЛЯ АДМИНА) ====================

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Только админ может смотреть статистику"""
    # Проверяем ID отправителя
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Эта команда только для администратора бота!")
        return
    
    # Получаем статистику за 7 дней (или указанное количество)
    days = 7
    try:
        args = message.text.split()
        if len(args) > 1:
            days = int(args[1])
            if days > 30:
                days = 30  # Максимум 30 дней
    except:
        pass
    
    data = stats_manager.get_stats(days)
    
    if not data:
        await message.answer("📊 Нет данных за указанный период")
        return
    
    # Считаем итоги
    total_users = sum(d["unique_users_count"] for d in data)
    total_games = sum(d["games_started"] for d in data)
    total_finished = sum(d["games_finished"] for d in data)
    
    text = f"📊 <b>СТАТИСТИКА БОТА 'ШПИОН'</b>\n"
    text += f"📅 За последние <b>{days}</b> дней\n\n"
    
    text += f"👥 Уникальных пользователей: <b>{total_users}</b>\n"
    text += f"🎮 Игр начато: <b>{total_games}</b>\n"
    text += f"🏁 Игр завершено: <b>{total_finished}</b>\n"
    
    if total_games > 0:
        conversion = (total_finished / total_games) * 100
        text += f"📈 Доигрываемость: <b>{conversion:.1f}%</b>\n"
    
    text += f"\n<b>📆 По дням:</b>\n"
    
    for day in data[:10]:  # Последние 10 дней
        text += f"\n📅 <b>{day['date']}</b>\n"
        text += f"  ├ 👤 Пользователей: {day['unique_users_count']}\n"
        text += f"  ├ 🎮 Игр начато: {day['games_started']}\n"
        text += f"  └ 🏁 Игр завершено: {day['games_finished']}\n"
        
        # Показываем популярные команды если есть
        if day['commands_used']:
            top_cmds = sorted(day['commands_used'].items(), key=lambda x: x[1], reverse=True)[:3]
            cmds_str = ", ".join([f"/{cmd} ({count})" for cmd, count in top_cmds])
            text += f"      💬 Команды: {cmds_str}\n"
    
    text += f"\n<i>💡 Используй /stats 30 для статистики за 30 дней</i>"
    
    await message.answer(text, parse_mode=ParseMode.HTML)

# ==================== CALLBACK ====================

@dp.callback_query(F.data.startswith("join_"))
async def cb_join(callback: types.CallbackQuery):
    user = callback.from_user
    chat_id = int(callback.data.split("_")[1])
    
    stats_manager.log_user(user.id)
    
    game = game_manager.games.get(chat_id)
    if not game:
        await callback.answer("Игра не найдена!", show_alert=True)
        return
    
    if user.id in game.players:
        await callback.answer("Ты уже в игре!", show_alert=True)
        return
    
    success = game_manager.join_game(
        chat_id=chat_id,
        user_id=user.id,
        full_name=user.full_name,
        username=user.username or user.full_name
    )
    
    if not success:
        await callback.answer("Не удалось!", show_alert=True)
        return
    
    await callback.answer(f"✅ {user.full_name} в игре!")
    
    try:
        await callback.message.edit_text(
            format_lobby_text(game),
            parse_mode=ParseMode.HTML,
            reply_markup=make_lobby_keyboard(chat_id, len(game.players))
        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")

@dp.callback_query(F.data.startswith("leave_"))
async def cb_leave(callback: types.CallbackQuery):
    user = callback.from_user
    chat_id = int(callback.data.split("_")[1])
    
    game = game_manager.games.get(chat_id)
    if not game or user.id not in game.players:
        await callback.answer("Ты не в игре!", show_alert=True)
        return
    
    game_manager.leave_game(chat_id, user.id)
    await callback.answer("👋 Ты вышел")
    
    if not game.players:
        try:
            await callback.message.delete()
        except:
            pass
        return
    
    try:
        await callback.message.edit_text(
            format_lobby_text(game),
            parse_mode=ParseMode.HTML,
            reply_markup=make_lobby_keyboard(chat_id, len(game.players))
        )
    except:
        pass

@dp.callback_query(F.data.startswith("start_"))
async def cb_start(callback: types.CallbackQuery):
    user = callback.from_user
    chat_id = int(callback.data.split("_")[1])
    
    game = game_manager.games.get(chat_id)
    if not game:
        await callback.answer("Игра не найдена!", show_alert=True)
        return
    
    if user.id != game.host_id:
        await callback.answer(f"❌ Только {game.host_name} может начать!", show_alert=True)
        return
    
    if len(game.players) < 3:
        await callback.answer("Нужно 3 игрока!", show_alert=True)
        return
    
    game.state = GameState.SELECTING_CATEGORY
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await bot.send_message(
        chat_id=chat_id,
        text="🎮 <b>Выбор категории</b>\n\n"
        "Выбери тему для игры:\n\n"
        "👇 Нажми на категорию:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_category_keyboard(chat_id)
    )
    
    await callback.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def cb_category(callback: types.CallbackQuery):
    data = callback.data.split("_")
    category = data[1]
    chat_id = int(data[2])
    
    game = game_manager.games.get(chat_id)
    if not game:
        await callback.answer("Игра не найдена!", show_alert=True)
        return
    
    if callback.from_user.id != game.host_id:
        await callback.answer(f"❌ Только {game.host_name} выбирает!", show_alert=True)
        return
    
    game.selected_category = category
    game.state = GameState.SELECTING_DIFFICULTY
    
    category_name = CATEGORIES.get(category, category)
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await bot.send_message(
        chat_id=chat_id,
        text=f"🎮 <b>Категория: {category_name}</b>\n\n"
        f"Теперь выбери сложность:\n"
        f"🟢 Легко — известные слова\n"
        f"🟡 Средне — менее известные\n"
        f"🔴 Сложно — редкие слова\n\n"
        f"👇 Выбери сложность:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_difficulty_keyboard(chat_id, category)
    )
    
    await callback.answer()

@dp.callback_query(F.data.startswith("diff_"))
async def cb_difficulty(callback: types.CallbackQuery):
    data = callback.data.split("_")
    difficulty = data[1]
    category = data[2]
    chat_id = int(data[3])
    
    game = game_manager.games.get(chat_id)
    if not game:
        return
    
    if callback.from_user.id != game.host_id:
        await callback.answer(f"❌ Только {game.host_name} выбирает!", show_alert=True)
        return
    
    game.difficulty = difficulty
    game.selected_category = category
    game = game_manager.start_game(chat_id)
    
    if not game:
        await callback.message.edit_text("❌ Ошибка запуска")
        return
    
    # Логируем начало игры
    stats_manager.log_game_start()
    
    category_name = CATEGORIES.get(game.selected_category, game.selected_category)
    difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(game.difficulty, "🟡")
    difficulty_text = {"easy": "Легко", "medium": "Средне", "hard": "Сложно"}.get(game.difficulty, "Средне")
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await bot.send_message(
        chat_id=chat_id,
        text=f"🚀 <b>ИГРА НАЧАЛАСЬ!</b>\n\n"
        f"📁 Категория: <b>{category_name}</b>\n"
        f"📊 Сложность: {difficulty_emoji} {difficulty_text}\n"
        f"👥 Игроков: {len(game.players)}\n\n"
        f"🎯 <b>Каждый нажимает кнопку ниже, чтобы увидеть своё слово!</b>\n"
        f"👀 <i>Только ты увидишь своё слово через всплывающее окно!</i>\n\n"
        f"📝 <b>Команды:</b>\n"
        f"• /vote — начать голосование (любой игрок)\n"
        f"• /guess [твоё слово] — угадать слово шпиону (1 попытка!)\n\n"
        f"✏️ Описывайте слова в любом порядке!",
        parse_mode=ParseMode.HTML,
        reply_markup=get_show_word_keyboard(chat_id)
    )

@dp.callback_query(F.data.startswith("myword_"))
async def cb_my_word(callback: types.CallbackQuery):
    user = callback.from_user
    chat_id = int(callback.data.split("_")[1])
    
    game = game_manager.games.get(chat_id)
    if not game:
        await callback.answer("Игра не найдена!", show_alert=True)
        return
    
    if user.id not in game.players:
        await callback.answer("Ты не в игре!", show_alert=True)
        return
    
    player = game.players[user.id]
    
    if player.is_spy:
        await callback.answer(
            f"🕵️‍♂️ ТЫ ШПИОН! Категория: {player.category}. Слова не знаешь!",
            show_alert=True
        )
    else:
        await callback.answer(
            f"🎯 Твоё слово: {player.word}! Не выдай шпиону!",
            show_alert=True
        )

@dp.callback_query(F.data.startswith("startvote_"))
async def cb_start_vote(callback: types.CallbackQuery):
    user = callback.from_user
    chat_id = int(callback.data.split("_")[1])
    
    game = game_manager.games.get(chat_id)
    if not game or game.state not in [GameState.PLAYING, GameState.SHOWING_WORDS]:
        await callback.answer("Игра не идёт!", show_alert=True)
        return
    
    if user.id not in game.players:
        await callback.answer("Ты не в игре!", show_alert=True)
        return
    
    await callback.answer("Начинаем голосование!")
    await start_voting(chat_id, game)

# ==================== ИГРОВОЙ ПРОЦЕСС ====================

@dp.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_msg(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Логируем активного пользователя
    stats_manager.log_user(user_id)
    
    game = game_manager.games.get(chat_id)
    if not game:
        return
    
    if user_id not in game.players:
        return
    
    text = message.text.strip().lower()
    
    # Шпион угадывает слово командой /guess
    if game.state in [GameState.PLAYING, GameState.SHOWING_WORDS, GameState.VOTING, GameState.SPY_GUESS] and text.startswith("/guess"):
        if user_id != game.spy_id:
            await message.reply("❌ Только шпион может угадывать слово!")
            return
        
        if game.spy_guess_used:
            await message.reply("❌ У тебя была только одна попытка!")
            return
        
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) < 2:
            await message.reply("❌ Напиши: /guess [твоё слово]")
            return
        
        guess = parts[1].lower().strip()
        correct = game.secret_word.lower()
        
        game.spy_guess_used = True
        
        if guess == correct:
            await message.reply(f"✅ <b>ПРАВИЛЬНО!</b>\n🎯 Слово: {game.secret_word}\n\n🏆 ШПИОН ПОБЕДИЛ!")
            await end_game(game, "spy", f"Шпион угадал слово '{game.secret_word}'!")
        else:
            await message.reply(f"❌ <b>НЕПРАВИЛЬНО!</b>\nТы сказал: {guess}\n🎯 Было: {game.secret_word}\n\n🏆 МИРНЫЕ ПОБЕДИЛИ!")
            await end_game(game, "citizens", f"Шпион не угадал (сказал '{guess}'). Правильное слово: '{game.secret_word}'")
        return
    
    # Обычные описания (только в активных состояниях игры, не во время угадывания шпиона)
    if game.state in [GameState.PLAYING, GameState.SHOWING_WORDS]:
        if game.state == GameState.SHOWING_WORDS:
            game.state = GameState.PLAYING
        
        player = game.players[user_id]
        player.description = message.text

async def start_voting(chat_id: int, game: GameRoom):
    game.state = GameState.VOTING
    
    # Сбрасываем голоса
    for p in game.players.values():
        p.votes_received = 0
        p.has_voted = False
        p.voted_for = None
    
    game.votes = {}
    
    desc = "📝 <b>ОПИСАНИЯ ИГРОКОВ:</b>\n\n"
    for pid, p in game.players.items():
        if p.description:
            desc += f"• <b>{p.full_name}</b>: {p.description}\n"
    
    if not any(p.description for p in game.players.values()):
        desc += "<i>Пока нет описаний...</i>\n"
    
    await bot.send_message(
        chat_id,
        f"{desc}\n🗳 <b>ГОЛОСОВАНИЕ!</b>\nКто шпион? Каждый голосует через свою кнопку ниже:",
        parse_mode=ParseMode.HTML
    )
    
    for pid in game.players:
        keyboard = get_vote_keyboard(game, pid)
        if keyboard:
            try:
                await bot.send_message(
                    chat_id,
                    f"🗳 <b>{game.players[pid].full_name}</b>, за кого голосуешь?",
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.error(f"Ошибка отправки кнопок: {e}")

@dp.callback_query(F.data.startswith("vote_"))
async def cb_vote(callback: types.CallbackQuery):
    data = callback.data.split("_")
    chat_id = int(data[1])
    target_id = int(data[2])
    voter_id = int(data[3])
    
    if callback.from_user.id != voter_id:
        await callback.answer("❌ Это не твоя кнопка!", show_alert=True)
        return
    
    game = game_manager.games.get(chat_id)
    if not game or game.state != GameState.VOTING:
        await callback.answer("Голосование окончено!", show_alert=True)
        return
    
    if game.players[voter_id].has_voted:
        await callback.answer("Ты уже голосовал!", show_alert=True)
        return
    
    game.votes[voter_id] = target_id
    game.players[voter_id].has_voted = True
    game.players[target_id].votes_received += 1
    
    await callback.answer(f"✅ Проголосовал против {game.players[target_id].full_name}!")
    
    try:
        await callback.message.delete()
    except:
        pass
    
    voted_count = sum(1 for p in game.players.values() if p.has_voted)
    
    await bot.send_message(
        chat_id,
        f"🗳 {game.players[voter_id].full_name} проголосовал! ({voted_count}/{len(game.players)})",
        parse_mode=ParseMode.HTML
    )
    
    if voted_count >= len(game.players):
        await end_voting(game)

async def end_voting(game: GameRoom):
    max_votes = -1
    suspects = []
    
    for pid, p in game.players.items():
        if p.votes_received > max_votes:
            max_votes = p.votes_received
            suspects = [pid]
        elif p.votes_received == max_votes:
            suspects.append(pid)
    
    suspected_id = random.choice(suspects)
    suspected = game.players[suspected_id]
    
    if suspected.is_spy:
        game.state = GameState.SPY_GUESS
        await bot.send_message(
            game.chat_id,
            f"🎯 <b>{suspected.full_name}</b> выгнан!\n🕵️‍♂️ Это ШПИОН!\n\n"
            f"🕵️‍♂️ <b>{suspected.full_name}</b>, у тебя ОДНА попытка!\n"
            f"Напиши: <code>/guess [твоё слово]</code>\n"
            f"📁 Категория: {game.secret_category}",
            parse_mode=ParseMode.HTML
        )
    else:
        spy = game.players[game.spy_id]
        await end_game(game, "spy", f"Ошибка! {suspected.full_name} не шпион. Шпион был {spy.full_name}")

async def end_game(game: GameRoom, winner: str, reason: str):
    # Логируем завершение игры
    stats_manager.log_game_end()
    
    game.state = GameState.FINISHED
    spy = game.players[game.spy_id]
    
    category_name = CATEGORIES.get(game.selected_category, game.selected_category)
    
    result = f"🏁 <b>ИГРА ОКОНЧЕНА!</b>\n\n"
    result += f"📁 Категория: {category_name}\n"
    result += f"🕵️‍♂️ Шпион: {spy.full_name}\n"
    result += f"🎯 Слово: {game.secret_word}\n\n"
    result += f"🏆 {'ПОБЕДА ШПИОНА!' if winner == 'spy' else 'ПОБЕДА МИРНЫХ!'}\n"
    result += f"📋 {reason}"
    
    await bot.send_message(game.chat_id, result, parse_mode=ParseMode.HTML)
    
    for pid in list(game.players.keys()):
        if pid in game_manager.user_games:
            del game_manager.user_games[pid]
    if game.chat_id in game_manager.games:
        del game_manager.games[game.chat_id]

# ==================== ЗАПУСК ====================

async def main():
    logger.info("Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())