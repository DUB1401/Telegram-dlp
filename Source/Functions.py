from Source.YtDlp import YtDlp

from dublib.Polyglot import Markdown
from telebot import TeleBot, types

def SendFormatSelector(bot: TeleBot, chat_id: int, info: dict):
	"""
	Отправляет пользователю сообщение с выбором формата.
		bot – бот Telegram;
		chat_id – идентификатор чата;
		info – данные видео.
	"""

	# Получение разрешений.
	Resolutions = YtDlp("yt-dlp/yt-dlp").get_resolutions(info)
	# Дополнительное описание.
	Title = ""
	Views = ""
	Likes = ""
	Newline = ""
	Uploader = ""
	Duration = ""

	#---> Генерация кнопочного интерфейса.
	#==========================================================================================#
	# Кнопочное меню.
	Menu = types.InlineKeyboardMarkup()

	# Для каждого названия разрешения.
	for ResolutionName in Resolutions.keys():
		# Генерация кнопки.
		Button = types.InlineKeyboardButton("🎬 " + ResolutionName, callback_data = f"download_video_{ResolutionName}_" + Resolutions[ResolutionName])
		# Добавление кнопки в меню.
		Menu.add(Button, row_width = 1)

	# Добавление кнопки загрузки аудиодорожки.
	Menu.add(types.InlineKeyboardButton("🎵 Только аудио", callback_data = f"download_audio"), row_width = 1)

	#---> Составление описания.
	#==========================================================================================#

	# Если у видео есть заголовок, сформировать его описание.
	if "title" in info.keys() and info["title"]: Title = "*" +  Markdown(info["title"]).escaped_text + "*\n"

	# Если у видео есть данные о просмотре.
	if "view_count" in info.keys() and info["view_count"]:
		# Количество просотров.
		ViewsCount = info["view_count"]

		# Если нужно округлить тясячидо одного числа после запятой.
		if ViewsCount >= 1000 and ViewsCount < 10000:
			# Перевод в тысячи и округление.
			ViewsCount = round(float(ViewsCount) / 1000.0, 1)
			# Конвертирование в строку.
			ViewsCount = f"{ViewsCount}K"

		# Если нужно округлить тысячи до целого числа.
		elif ViewsCount >= 10000 and ViewsCount < 1000000:
			# Перевод в тысячи и округление.
			ViewsCount = int(ViewsCount / 1000)
			# Конвертирование в строку.
			ViewsCount = f"{ViewsCount}K"

		# Если нужно округлить миллионы до одного числа после запятой.
		elif ViewsCount >= 1000000 and ViewsCount < 10000000:
			# Перевод в миллионы и округление.
			ViewsCount = round(float(ViewsCount) / 1000000.0, 1)
			# Конвертирование в строку.
			ViewsCount = f"{ViewsCount}M"

		# Если нужно округлить миллионы до целого числа.
		elif ViewsCount >= 10000000:
			# Перевод в миллионы и округление.
			ViewsCount = int(ViewsCount / 1000000)
			# Конвертирование в строку.
			ViewsCount = f"{ViewsCount}M"

		# Составление описания.
		Views = f"👀 {ViewsCount}  "

	# Если у видео есть данные о лайках.
	if "like_count" in info.keys() and info["like_count"]:
		# Количество лайков.
		LikesCount = info["like_count"]

		# Если нужно округлить тясячидо одного числа после запятой.
		if LikesCount >= 1000 and LikesCount < 10000:
			# Перевод в тысячи и округление.
			LikesCount = round(float(LikesCount) / 1000.0, 1)
			# Конвертирование в строку.
			LikesCount = f"{LikesCount}K"

		# Если нужно округлить тысячи до целого числа.
		elif LikesCount >= 10000 and LikesCount < 1000000:
			# Перевод в тысячи и округление.
			LikesCount = int(LikesCount / 1000)
			# Конвертирование в строку.
			LikesCount = f"{LikesCount}K"

		# Если нужно округлить миллионы до одного числа после запятой.
		elif LikesCount >= 1000000 and LikesCount < 10000000:
			# Перевод в миллионы и округление.
			LikesCount = round(float(LikesCount) / 1000000.0, 1)
			# Конвертирование в строку.
			LikesCount = f"{LikesCount}M"

		# Если нужно округлить миллионы до целого числа.
		elif LikesCount >= 10000000:
			# Перевод в миллионы и округление.
			LikesCount = int(LikesCount / 1000000)
			# Конвертирование в строку.
			LikesCount = f"{LikesCount}M"

		# Составление описания.
		Likes = f"👍 {LikesCount}  "

	# Если у видео есть данные об авторе.
	if "uploader_id" in info.keys() and info["uploader_id"]:
		# Составление описания автора.
		Uploader = f"[{info["uploader_id"]}]({info["uploader_url"]})"

	# Если у видео есть данные о продолжительности.
	if "duration" in info.keys() and info["duration"]:
		# Продолжительность.
		DurationSeconds = info["duration"]

		# Если продолжительность больше минуты.
		if DurationSeconds >= 60:
			# Части длительности.
			Minutes = str(int(DurationSeconds / 60))
			Seconds = str(DurationSeconds % 60).ljust(2, "0")
			# Составление времени длительности.
			DurationSeconds = f"{Minutes}:{Seconds}"

		# Составление описания.
		Duration = f"🕓 {DurationSeconds}"

	# Расстановка символов новой строки.
	if Likes or Views or Duration: Newline = "\n "

	#---> Отправка сообщения.
	#==========================================================================================#

	# Если у видео есть миниатюры.
	if "thumbnail" in info.keys() and info["thumbnail"]:
		# Отправка сообщения: формат загрузки (с миниатюрой).
		bot.send_photo(
			chat_id = chat_id,
			photo = info["thumbnail"],
			caption = f"{Title}{Views}{Likes}{Duration}{Newline}{Uploader}\n\nВыберите формат загрузки:",
			parse_mode = "MarkdownV2",
			reply_markup = Menu
		)

	else:
		# Отправка сообщения: формат загрузки.
		bot.send_message(
			chat_id = chat_id,
			text = f"{Title}{Views}{Likes}{Duration}{Newline}{Uploader}\n\nВыберите формат загрузки:",
			parse_mode = "MarkdownV2",
			reply_markup = Menu
		)