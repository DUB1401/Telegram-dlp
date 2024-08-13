from Source.Core.YtDlp import YtDlp

from dublib.Polyglot import Markdown
from telebot import TeleBot, types
from dublib.Methods.JSON import *

import requests

class InlineKeyboards:
	"""Генератор кнопочного интерфейса."""

	def __init__(self):
		"""Генератор кнопочного интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		pass

	def send_fromat_selector(self, bot: TeleBot, chat_id: int, info: dict):
		"""
		Отправляет пользователю сообщение с выбором формата.
			bot – бот Telegram;
			chat_id – идентификатор чата;
			info – данные видео.
		"""

		Resolutions = YtDlp("yt-dlp/yt-dlp").get_resolutions(info)
		Title = ""
		Views = ""
		Likes = ""
		Newline = ""
		Uploader = ""
		Duration = ""

		#---> Генерация кнопочного интерфейса.
		#==========================================================================================#
		Menu = types.InlineKeyboardMarkup()

		for ResolutionName in Resolutions.keys():

			if not ResolutionName.endswith("w"):
				Button = types.InlineKeyboardButton("🎬 " + ResolutionName, callback_data = f"download_video_{ResolutionName.replace(" ", "%")}+" + Resolutions[ResolutionName].replace(" ", "%"))
				Menu.add(Button, row_width = 1)

			else:
				Resolution = ResolutionName.rstrip("w")
				ButtolLabel = ""
				if ResolutionName == "nullw": ButtolLabel = "С водяным знаком"
				else: ButtolLabel = Resolution + " (с водяным знаком)"
				Menu.add(types.InlineKeyboardButton("🎞️ " + ButtolLabel, callback_data = f"download_watermarked_{Resolution.replace(" ", "%")}+" + Resolutions[ResolutionName].replace(" ", "%")), row_width = 1)
		
		Menu.add(types.InlineKeyboardButton("🎵 Только аудио", callback_data = f"download_audio"), row_width = 1)
		
		#---> Составление описания.
		#==========================================================================================#

		if "title" in info.keys() and info["title"]:
			if len(info["title"]) > 64: Title = info["title"][:64] + "..."
			Title = "*" +  Markdown(Title).escaped_text + "*\n"

		if "view_count" in info.keys() and info["view_count"]:
			ViewsCount = info["view_count"]

			if ViewsCount >= 1000 and ViewsCount < 10000:
				ViewsCount = round(float(ViewsCount) / 1000.0, 1)
				ViewsCount = f"{ViewsCount}K"

			elif ViewsCount >= 10000 and ViewsCount < 1000000:
				ViewsCount = int(ViewsCount / 1000)
				ViewsCount = f"{ViewsCount}K"

			elif ViewsCount >= 1000000 and ViewsCount < 10000000:
				ViewsCount = round(float(ViewsCount) / 1000000.0, 1)
				ViewsCount = f"{ViewsCount}M"

			elif ViewsCount >= 10000000:
				ViewsCount = int(ViewsCount / 1000000)
				ViewsCount = f"{ViewsCount}M"

			Views = Markdown(f"👀 {ViewsCount}  ").escaped_text

		if "like_count" in info.keys() and info["like_count"]:
			LikesCount = info["like_count"]

			if LikesCount >= 1000 and LikesCount < 10000:
				LikesCount = round(float(LikesCount) / 1000.0, 1)
				LikesCount = f"{LikesCount}K"

			elif LikesCount >= 10000 and LikesCount < 1000000:
				LikesCount = int(LikesCount / 1000)
				LikesCount = f"{LikesCount}K"

			elif LikesCount >= 1000000 and LikesCount < 10000000:
				LikesCount = round(float(LikesCount) / 1000000.0, 1)
				LikesCount = f"{LikesCount}M"

			elif LikesCount >= 10000000:
				LikesCount = int(LikesCount / 1000000)
				LikesCount = f"{LikesCount}M"

			Likes = Markdown(f"👍 {LikesCount}  ").escaped_text

		if "uploader" in info.keys() and info["uploader"] and "uploader_url" in info.keys() and info["uploader_url"]:
			Uploader = "[@" + Markdown(info["uploader"].strip()).escaped_text + "](" + info["uploader_url"] + ")\n"

		if "duration" in info.keys() and info["duration"]:
			DurationSeconds = info["duration"]
			Minutes = str(int(DurationSeconds / 60))
			Seconds = str(int(DurationSeconds % 60)).ljust(2, "0")
			DurationSeconds = f"{Minutes}:{Seconds}"
			Duration = f"🕓 {DurationSeconds}"

		if Likes or Views or Duration: Newline = "\n"

		#---> Отправка сообщения.
		#==========================================================================================#
		
		if "thumbnail" in info.keys() and info["thumbnail"] and requests.get(info["thumbnail"]).status_code == 200:
			bot.send_photo(
				chat_id = chat_id,
				photo = info["thumbnail"],
				caption = f"{Title}{Views}{Likes}{Duration}{Newline}{Uploader}\nВыберите формат загрузки:",
				parse_mode = "MarkdownV2",
				reply_markup = Menu
			)

		else:
			bot.send_message(
				chat_id = chat_id,
				text = f"{Title}{Views}{Likes}{Duration}{Newline}{Uploader}\n\nВыберите формат загрузки:",
				parse_mode = "MarkdownV2",
				disable_web_page_preview = True,
				reply_markup = Menu
			)