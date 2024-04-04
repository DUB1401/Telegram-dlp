# Telegram-dlp
**Telegram-dlp** – это бот Telegram для упрощения загрузки видео из множества источников. Поддерживается широкий список [сайтов](https://github.com/yt-dlp/yt-dlp).

## Порядок установки и использования
1. Загрузить последний релиз скрипта. Распаковать.
2. Установить Python версии не старше 3.10. Рекомендуется добавить в PATH.
3. В среду исполнения установить следующие пакеты: [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI), [Telethon](https://github.com/LonamiWebs/Telethon), [dublib](https://github.com/DUB1401/dublib).
```
pip install pyTelegramBotAPI
pip install Telethon
pip install dublib
```
Либо установить сразу все пакеты при помощи следующей команды, выполненной из директории скрипта.
```
pip install -r requirements.txt
```
4. Настроить скрипт путём редактирования _Settings.json_.
5. Перейти на [сайт](https://my.telegram.org) Telegram и зарегистрировать приложение. Получить ID и хеш API.
6. Открыть директорию со скриптом в терминале. Можно использовать метод `cd` и прописать путь к папке, либо запустить терминал из проводника.
7. Выполнить авторизацию аккаунта Telegram методом запуска главного файла скрипта с аргументами: `main.py {PHONE_NUMBER} {API_ID} {API_HASH}`.
8. Указать для выполнения главный файл скрипта `main.py`, перейти в Telegram, отправить в чат с ботом команду `/start`.
9. Для автоматического запуска службы рекомендуется провести инициализацию скрипта через [systemd](systemd/README.md) на Linux или путём добавления его в автозагрузку на Windows.

## Версии поставляемых бинарных файлов
| Файл        | Версия                        | Источник                                                           |
|-------------|-------------------------------|--------------------------------------------------------------------|
| yt-dlp      | _2024.03.10_                  | [ссылка](https://github.com/yt-dlp/yt-dlp/releases/tag/2024.03.10) |
| yt-dlp.exe  | _2024.03.10_                  | [ссылка](https://github.com/yt-dlp/yt-dlp/releases/tag/2024.03.10) |
| ffmpeg.exe  | _6.0 2023-03-04 (essentials)_ | [ссылка](https://github.com/GyanD/codexffmpeg/releases/tag/6.0)    |
| ffprobe.exe | _6.0 2023-03-04 (essentials)_ | [ссылка](https://github.com/GyanD/codexffmpeg/releases/tag/6.0)    |

# Settings.json
```JSON
"token": ""
```
Сюда необходимо занести токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).
___
```JSON
"bot-name": ""
```
Сюда необходимо занести название бота (можно получить из ссылки на бота, например: `https://t.me/bot_name`).
___
```JSON
"trusted-source-id": null
```
Сюда необходимо занести ID пользователя Telegram, от имени которого выполняется загрузка файлов на сервер (можно узнать у [Chat ID Bot](https://t.me/chat_id_echo_bot)).
___

```JSON
"premium": false
```
Здесь указывается, имеется ли у хозяина бота Premium-подписка. Влияет на максимальный размер загружаемого файла. Определяется автоматически.
___

```JSON
"original-filenames": false
```
Если включено, в качестве названия файла будет использоваться оригинальная подпись вместо идентификатора, что на некоторых системах может привести к ошибкам кодировки.
___

```JSON
"proxy": ""
```
Здесь указывается прокси для обхода региональных ограничений в формате `http://login:password@host:port`.

# Благодарность
* [@yt-dlp](https://github.com/yt-dlp) – библиотека загрузки потокового видео.

_Copyright © DUB1401. 2024._