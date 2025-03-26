from dataclasses import dataclass
from bs4 import BeautifulSoup
from datetime import datetime

import requests
import enum
import json
import re

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass
class TrendData:
	"""Данные ролика в тренде."""

	link: str
	title: str

@dataclass
class TrendsTypes(enum.Enum):
	"""Типы поддерживаемых трендов."""

	News = 0
	Music = 1

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Trends:
	"""Парсер трендов YouTube."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetTrendsData(self, trend: TrendsTypes) -> tuple[TrendData]:
		"""
		Возвращает список данных роликов в тренде.
			trent – тип тренда.
		"""

		Data = list()
		CurrentData = self.__NewsData if trend is TrendsTypes.News else self.__MusicData
		Index = 3 if self.__English and trend is TrendsTypes.News else 0

		RenderData = CurrentData["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][trend.value]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][Index]["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]
		
		for Item in RenderData:
			Item: dict
			ItemLink = Item["videoRenderer"]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
			ItemTitle = Item["videoRenderer"]["title"]["runs"][0]["text"]
			Data.append(TrendData("https://www.youtube.com" + ItemLink, ItemTitle))

		return tuple(Data)

	def __ParseTrendsPage(self, trend: TrendsTypes) -> dict | None:
		"""
		Возвращает данные рендерера страницы трендов YouTube.
			trent – тип тренда.
		"""

		Request = "?bp=6gQJRkVleHBsb3Jl"
		if trend is TrendsTypes.Music: Request = "?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D"
		if self.__English: Request += "&persist_gl=1&gl=US"

		Response = requests.get(f"https://www.youtube.com/feed/trending{Request}")
		Soup = BeautifulSoup(Response.content, "html.parser")
		Scripts = Soup.find_all("script")

		for Script in Scripts:
			Script: BeautifulSoup
			ScriptContent = Script.get_text()

			if ScriptContent and "var ytInitialData =" in ScriptContent:
				if trend is TrendsTypes.News: self.__NewsUpdateDate = datetime.now()
				elif trend is TrendsTypes.Music: self.__MusicUpdateDate = datetime.now()
				
				return json.loads(ScriptContent[20:-1])

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, english: bool = False):
		"""
		Парсер трендов YouTube.
			english – запрашивать ли данные на английском.
		"""

		self.__English = english

		self.__NewsUpdateDate = None
		self.__MusicUpdateDate = None

		self.__NewsData = None
		self.__MusicData = None

		try: self.__NewsData = self.__ParseTrendsPage(TrendsTypes.News)
		except: pass

		try: self.__MusicData = self.__ParseTrendsPage(TrendsTypes.Music)
		except: pass

		self.__CachedNews = tuple()
		self.__CachedMusic = tuple()

	def get_music(self) -> tuple[TrendData]:
		"""Возвращает кортеж данных трендов музыки."""

		if not self.__MusicUpdateDate: self.__MusicData = self.__ParseTrendsPage(TrendsTypes.Music)

		Delta = datetime.now() - self.__MusicUpdateDate
		if Delta.seconds / 3600 >= 1: self.__MusicData = self.__ParseTrendsPage(TrendsTypes.Music)
		if not self.__MusicData: return self.__CachedMusic
		self.__CachedMusic = self.__GetTrendsData(TrendsTypes.Music)
		
		return self.__CachedMusic

	def get_news(self) -> tuple[TrendData]:
		"""Возвращает кортеж данных трендов новостей."""

		if not self.__NewsUpdateDate: self.__NewsData = self.__ParseTrendsPage(TrendsTypes.News)

		Delta = datetime.now() - self.__NewsUpdateDate
		if Delta.seconds / 3600 >= 1: self.__NewsData = self.__ParseTrendsPage(TrendsTypes.News)
		if not self.__NewsData: return self.__CachedNews
		self.__CachedNews = self.__GetTrendsData(TrendsTypes.News)
		
		return self.__CachedNews