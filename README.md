English (на русском будет тоже, см. в этом же readme ниже):

# Simple WebP to JPEG Converter

A batch conversion tool for WebP images to JPEG, preserving original resolution, displaying statistics, and offering flexible settings.

## About the Project

> Dear community! This code was generated with AI assistance under my close guidance. I designed all the logic and structure myself, and I independently performed all the work on improvement, testing, and bug fixing.
>
> Initially, this project was intended for personal use, but since no similar programs were found online, I decided to release this program to the public in the hope that it will be useful to you.
>
> I'd appreciate your feedback and suggestions via Issues and Pull Requests. If something doesn't work as expected, or if you have ideas on how to improve the program — let's polish it together.

## Requirements

- Python **3.6** or higher
- Pillow library (install: `pip install Pillow`)
- (Recommended) `colorama` for colored output in the command prompt: `pip install colorama`
- (Recommended) `send2trash` to send files to the recycle bin instead of permanent deletion: `pip install send2trash`

## Important Recommendations (especially for Overkill version)

1. **Run the program by double-clicking** (or in a cmd), not via IDLE – this ensures colored output works correctly.
2. **Install `colorama` and `send2trash`** – they improve safety (colorful warnings are easier to notice, and the recycle bin lets you recover files if something goes wrong).
3. **Always work on a copy of your data!** The developer has thoroughly tested all possible configurations, but the risk is not zero. First run the program on a duplicate of your storage, verify everything works as expected, and only then apply it to the original.

> **The most reliable way to avoid mistakes – both yours and the program's – is to always work on a duplicate/copy of your storage, and after successful conversion, simply replace the original storage with the resulting one.**

---

### Settings

At the top of the file you'll find:

```python
input_path = r""          # folder with source WebP files (empty means working in python-file directory)
output_path = r""         # folder for JPG results (if empty - creates "converted" subfolder)
jpg_quality = 85          # JPEG quality (1-100)

# ⚠️ DANGEROUS OPTIONS: Delete original WebP files?
delete_original = False        # set to True to enable deletion.
delete_on_skip = False         # delete source if file skipped due to conflict (only if delete_original=True)
delete_on_rename = False       # delete source if file renamed due to conflict (only if delete_original=True)

# Deletion method (only used if delete_original=True)
deletion_method = "recycle"    # "recycle" (send to recycle bin) or "permanent" (delete forever)

# Behavior on name conflict
on_name_conflict = "ask"       # "skip", "rename", or "ask" (default ask)
```

If delete_original = False, then delete_on_skip and delete_on_rename are ignored (even if set to True). The program will warn you about this at startup.

### What it does
1. Finds all .webp files in the specified folder.

2. Shows their count and total size.

3. Converts each file to .jpg at the same resolution.
If a JPG with the same name already exists in the target folder, programm will ask you, what to do.

4. Displays progress every 10 files and final statistics (sizes before/after, percentage change).

5. Waits for Enter before closing, so you can read the results.

### Example output
```text
🔍 Source folder: D:\Photos\2024
📊 WebP files found: 124
💾 Total size of source WebP files: 232.15 MB
📁 All JPGs will be saved in: D:\Photos\2024\converted

🚀 Conversion started.
📈 Progress: 10/124 processed
...
📈 Progress: 124/124 processed

🏁 Conversion completed!
✅ Files converted: 118
⏭️ Skipped (JPG already exists): 6

📊 Statistics for converted files:
   Total size of source WebP: 232.15 MB
   Total size of resulting JPG: 198.42 MB
   Change: 232.15 MB -> 198.42 MB
   JPG size is 85.5% of original WebP size

👋 Press Enter to exit...
```
### Third‑Party Licenses

This project uses the following open‑source libraries:

- **[Pillow](https://github.com/python-pillow/Pillow)** – HPND License  
  Copyright (c) 1995–2011 Fredrik Lundh, 2010–2023 Alex Clark and contributors  
  ([Full license text](https://github.com/python-pillow/Pillow/blob/main/LICENSE))

- **[colorama](https://github.com/tartley/colorama)** – BSD‑3‑Clause License  
  Copyright (c) 2010 Jonathan Hartley  
  ([Full license text](https://github.com/tartley/colorama/blob/master/LICENSE.txt))

- **[send2trash](https://github.com/hsoft/send2trash)** – BSD‑3‑Clause License  
  Copyright (c) 2013 Virgil Dupras  
  ([Full license text](https://github.com/hsoft/send2trash/blob/master/LICENSE))

### License
The program is distributed under the MIT license.

<br>

# Простой конвертер WebP в JPEG

Программа для пакетной конвертации изображений WebP в JPEG с сохранением исходного разрешения, подсчётом статистики и гибкими настройками.

> ## О проекте
> 
> Уважаемое сообщество! Данный код был сгенерирован ИИ под моим чутким руководством. Всю логику и структуру я придумал сам, а также всю работу по улучшению, тестированию и исправлению ошибок я провёл самостоятельно.
> 
> Изначально этот проект рассчитывался для домашнего использования, но поскольку аналогичных программ в сети найдено не было, я решил выложить данную программу в открытый доступ, в надежде что она будет вам полезна.
> 
> Буду благодарен вашим замечаниям и предложениям через Issues и Pull Requests. Если что-то работает не так или Вы знаете, как можно сделать программу лучше - давайте вместе доведём её до ума.

## Требования

- Python **3.6** или выше
- Библиотека Pillow (установка: `pip install Pillow`)
- (Рекомендуется) `colorama` для цветного вывода в командной строке: `pip install colorama`
- (Рекомендуется) `send2trash` для отправки файлов в корзину вместо безвозвратного удаления: `pip install send2trash`

## Важные рекомендации перед использованием

1. **Запускайте программу двойным кликом** (или в командной строке), а не через IDLE – так цветное оформление будет работать корректно.
2. **Установите `colorama` и `send2trash`** – это повысит безопасность (цветные предупреждения легче заметить, а корзина позволит восстановить файлы в случае ошибки).
3. **Всегда работайте с копией своих данных!** Разработчик тщательно проверил все возможные конфигурации, но существует небольшой шанс упущения. Сначала запустите программу на дубликате хранилища, убедитесь, что всё работает как надо, и только потом применяйте к оригиналу.
> **Самый надёжный способ не ошибиться Вам и не дать ошибиться программе – всегда работать с дубликатом/копией хранилища, а после правильной отработки просто заменить исходное хранилище на получившееся.**

---

### Настройки

В начале файла найдите блок настроек, и откалибруйте так, как Вам нужно:

```python
input_path = r""          # папка с исходными WebP файлами (если пусто, ищет в текущей папке)
output_path = r""         # папка для сохранения сконвертированных JPG файлов (если пусто, то создаст подпапку "converted")
jpg_quality = 85          # качество JPG (1-100)

# ⚠️ ОПАСНЫЕ ОПЦИИ: Удалять исходные WebP?
delete_original = False        # установите True, чтобы включить удаление исходных .WebP. 
delete_on_skip = False         # удалять исходный WebP при пропуске (только если delete_original=True)?
delete_on_rename = False       # удалять исходный WebP при переименовании (только если delete_original=True)?

# Способ удаления (используется только при delete_original=True)
deletion_method = "recycle"    # "recycle" (в корзину) или "permanent" (безвозвратно)

# Поведение при конфликте имён
on_name_conflict = "ask"       # "skip", "rename" или "ask" (по умолчанию ask)
```

Если delete_original = False, то delete_on_skip и delete_on_rename игнорируются (даже если установлены в True).


### Что делает программа
1. Находит все файлы .webp в указанной папке.

2. Показывает их количество и общий объём.

3. Конвертирует каждый файл в .jpg с тем же разрешением.
Если в целевой папке уже есть .jpg с таким именем, по умолчанию программа задаёт вопрос, как следует поступить.

4. Выводит прогресс каждые 10 файлов и итоговую статистику (размеры до/после, процент изменения).

5. После завершения ждёт нажатия Enter, чтобы Вы могли посмотреть статистику.

### Пример вывода
```text
🔍 Исходная папка: D:\Фото\2024
📊 Найдено WebP-файлов: 124
💾 Общий объём исходных WebP-файлов: 245.78 МБ
📁 Все JPG будут сохранены в: D:\Фото\2024\converted

🚀 Конвертация запущена.
📈 Прогресс: 10/124 обработано
...
📈 Прогресс: 124/124 обработано

🏁 Конвертация завершена!
✅ Сконвертировано файлов: 118
⏭️ Пропущено (JPG уже существует): 6

📊 Статистика по сконвертированным файлам:
   Суммарный объём исходных WebP: 232.15 МБ
   Суммарный объём полученных JPG: 198.42 МБ
   Изменение: 232.15 МБ -> 198.42 МБ
   Размер JPG составляет 85.5% от исходного WebP

👋 Нажмите Enter для выхода...
```

### Лицензии сторонних библиотек

В этом проекте используются следующие библиотеки с открытым исходным кодом:

- **[Pillow](https://github.com/python-pillow/Pillow)** – лицензия HPND  
  Copyright (c) 1995–2011 Fredrik Lundh, 2010–2023 Alex Clark и соавторы  
  ([Полный текст лицензии](https://github.com/python-pillow/Pillow/blob/main/LICENSE))

- **[colorama](https://github.com/tartley/colorama)** – лицензия BSD‑3‑Clause  
  Copyright (c) 2010 Jonathan Hartley  
  ([Полный текст лицензии](https://github.com/tartley/colorama/blob/master/LICENSE.txt))

- **[send2trash](https://github.com/hsoft/send2trash)** – лицензия BSD‑3‑Clause  
  Copyright (c) 2013 Virgil Dupras  
  ([Полный текст лицензии](https://github.com/hsoft/send2trash/blob/master/LICENSE))

### Лицензия
Программа распространяется под лицензией MIT.

