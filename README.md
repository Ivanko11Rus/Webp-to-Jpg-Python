English (russian will be there too):

# 🔄 WebP to JPEG Converter

**A simple program for batch converting WebP images to JPEG, preserving original resolution, displaying statistics, and easy configuration.**

## ⚙️ Requirements

- Python **3.6** or higher
- Pillow library (install with one command):
  ```bash
  pip install Pillow
  ```
## 🚀 How to Use
Download the Webp_To_Jpg.py file to any folder.

Open the file in a text editor (Notepad, VS Code, etc.).

Adjust the settings at the very top of the script (see the Settings section below).

Save the changes and close the editor.

Run the program.

Review the results – after completion, the program will show statistics and wait for you to press Enter, so the window stays open.

## ⚙️ Settings
At the top of the file you'll find a block with variables.

```python
# ⚠️⚠️⚠️ When copying a Windows path, use a raw string - r"...", where ... is your folder path copied from Windows.
# This prevents Python from interpreting \U or any other character after a backslash as an escape sequence.

input_path = r""               # folder with source WebP files (empty = current folder)
output_path = r""              # folder for JPG results (empty = creates "converted" subfolder in source folder)
jpg_quality = 85               # JPEG quality (1-100, default 85)
```
### 📂 Specifying Paths (important!)
Raw strings – always put an r before the quotes, for example:
```python
input_path = r"D:\My Photos\webp_folder"
```
This ensures that backslashes \ are treated as literal characters and not as escape sequences.

If you leave a field empty (""), the program will use the current folder (the one where the script is located).

Path to output folder (output_path) can also be empty – then a subfolder named converted will be created automatically inside the source folder.

## 🎚️ JPEG Quality
jpg_quality = 85 (recommended) – good quality with a reasonable file size.

You can set it from 1 (lowest quality, smallest size) to 100 (highest quality, largest size).

Experiment: for web use, 80–85 is often enough; for archiving, 90–95 may be preferred.

## 📊 Why Can JPG Be Larger Than WebP?
WebP is a modern format with efficient compression – it often produces smaller files at the same visual quality.
Example with quality 85:
```text
Source WebP files: 2.50 MB

Resulting JPG files: 6.09 MB (2.4 times larger)
```
This is perfectly normal! JPEG is an older format, and even at moderate compression settings it can occupy more space. If you want to reduce the output size, lower the quality setting (e.g., to 75–80).

### 📈 Example Output (quality 85)

```text
🔍 Source folder: D:\webp to jpg\Russian
📊 WebP files found: 13
💾 Total size of source WebP files: 2.50 MB
📁 Results will be saved in: D:\webp to jpg\converted

🚀 Conversion started.
📈 Progress: 10/13 processed
📈 Progress: 13/13 processed

🏁 Conversion completed!
✅ Files converted: 13
⏭️ Skipped (JPG already exists): 0

📊 Statistics for converted files:
   Total size of source WebP: 2.50 MB
   Total size of resulting JPG: 6.09 MB
   Change: 2.50 MB -> 6.09 MB
   JPG size is 243.5% of original WebP size

👋 Press Enter to exit...
```
## 🔍 Additional Features (for the curious)
The code contains commented lines (starting with #). If you want a detailed report on each file (e.g., which file is being processed and its size), simply remove the # in the appropriate places:
```python
# print(f"📄 File {f} added to processing list.") – shows all found WebP files.

# print(f"⏭️ File {jpg_filename} already exists. Skipping.") – tells you which files were already converted.

# print(f"✅ Converted {filename} -> {jpg_filename} (... MB -> ... MB)") – details for every conversion.
```
## ❗ Frequently Asked Questions
1. I get a SyntaxWarning: invalid escape sequence error when starting.
You've entered a path incorrectly. Fix it by using raw strings (r"...") or double backslashes ("C:\\Users\\...").

2. Error ModuleNotFoundError: No module named 'PIL'
Pillow is not installed. Run this in a command prompt:
pip install Pillow

3. The program doesn't see my WebP files.
Check that the folder actually contains files with the .webp extension (case doesn't matter). Also verify the path is correct and the folder exists.

4. Can it process files in subfolders?
For now - no, the program only handles files directly in the specified folder (non‑recursive). We'll make it later (we hope).

5. Why does the window stay open after finishing?
The program waits for you to press Enter so you have time to read the statistics. This is convenient regardless of how you run it.

## 📃 License
This program is free to use and modify.



# 🔄 Конвертер WebP в JPEG

**Простая программа для пакетной конвертации изображений WebP в JPEG с сохранением исходного разрешения, подсчётом статистики и удобной настройкой.**

## ⚙️ Требования

- Python **3.6** или выше
- Библиотека Pillow (установка одной командой):
  ```bash
  pip install Pillow
  ```
## 🚀 Как пользоваться
Скачайте файл Webp_To_Jpg.py в любую папку.

Откройте файл в текстовом редакторе (Блокнот, VS Code и т.п.).

Настройте параметры в самом начале скрипта (см. раздел Настройка ниже).

Сохраните изменения и закройте редактор.

Запустите программу.

Изучите результаты – после завершения программа покажет статистику и будет ждать нажатия Enter, чтобы окно не закрылось.

## ⚙️ Настройка
В самом начале файла есть блок с переменными.

```python
# ⚠️⚠️⚠️ When copying a Windows path, use a raw string - r"...", where ... is your folder path copied from Windows.
# This prevents Python from interpreting \U or any other character after a backslash as an escape sequence.

input_path = r""               # папка с исходными WebP (пусто = текущая папка)
output_path = r""              # папка для JPG (пусто = создастся "converted" в исходной)
jpg_quality = 85               # качество JPEG (1-100, по умолч. 85)
```
### 📂 Указание путей (важно!)
Сырые строки (raw strings) – всегда ставьте r перед кавычками, например:
```python
input_path = r"D:\Мои фото\webp_папка"
```
Это гарантирует, что обратная косая черта \ не будет воспринята как спецсимвол.

Если оставить поле пустым (""), программа возьмёт текущую папку (ту, где лежит скрипт).

Путь к папке для результатов (output_path) тоже может быть пустым – тогда автоматически создастся подпапка converted в исходной папке.

## 🎚️ Качество JPEG
jpg_quality = 85 (рекомендуется) – хорошее качество при умеренном размере файла.

Можно ставить от 1 (минимальное качество, маленький размер) до 100 (максимальное качество, большой размер).

Экспериментируйте: для веба часто хватает 80–85, для архива – 90–95.

## 📊 Почему JPG может быть больше WebP?
WebP – современный формат с эффективным сжатием, он часто даёт меньший размер при том же качестве.
Пример при качестве 85:
```python
Исходные WebP: 2.50 МБ

Полученные JPG: 6.09 МБ (в 2.4 раза больше)
```
Это нормально! JPG – более старый формат, и даже при средних настройках сжатия он может занимать больше места. Если хотите уменьшить размер, снизьте качество в настройках (например, до 75–80).

### 📈 Пример работы программы (качество 85)
```text
🔍 Исходная папка: D:\webp to jpg\Russian
📊 Найдено WebP-файлов: 13
💾 Общий объём исходных WebP-файлов: 2.50 МБ
📁 Результаты будут сохранены в: D:\webp to jpg\converted

🚀 Конвертация запущена.
📈 Прогресс: 10/13 обработано
📈 Прогресс: 13/13 обработано

🏁 Конвертация завершена!
✅ Сконвертировано файлов: 13
⏭️ Пропущено (уже есть JPG): 0

📊 Статистика по сконвертированным файлам:
   Суммарный объём исходных WebP: 2.50 МБ
   Суммарный объём полученных JPG: 6.09 МБ
   Изменение: 2.50 МБ -> 6.09 МБ
   Размер JPG составляет 243.5% от исходного WebP

👋 Нажмите Enter для выхода...
```
## 🔍 Дополнительные возможности (для любопытных ценителей прекрасного)
В коде есть закомментированные строки (начинаются с #). Если хотите видеть подробный отчёт по каждому файлу (например, какой файл сейчас обрабатывается и его размер), удалите # в соответствующих местах:
```python
# print(f"📄 File {f} added to processing list.") – увидите все найденные WebP.

# print(f"⏭️ File {jpg_filename} already exists. Skipping.") – узнаете, какие файлы уже были сконвертированы.

# print(f"✅ Converted {filename} -> {jpg_filename} (... MB -> ... MB)") – детали по каждому преобразованию.
```
## ❗ Часто задаваемые вопросы
1. При запуске появляется ошибка про SyntaxWarning: invalid escape sequence
Вы неправильно указали путь. Исправьте: используйте raw-строки (r"...") или удвойте обратные слеши ("C:\\Users\\...").

2. Ошибка ModuleNotFoundError: No module named 'PIL'
Не установлена библиотека Pillow. Выполните в командной строке:
pip install Pillow

3. Программа не видит мои WebP-файлы
Проверьте, что в папке действительно есть файлы с расширением .webp (регистр не важен). Убедитесь, что путь указан правильно и папка существует.

4. Можно ли обрабатывать файлы во вложенных папках?
Пока что нет, программа работает только с файлами в указанной папке (без рекурсии). Думаю, я скоро это исправлю (если лень не окажется сильнее).

5. Почему после завершения окно не закрывается?
Программа ждёт нажатия Enter, чтобы вы успели прочитать статистику. Это удобно при любом способе запуска.

## 📃 Лицензия
Программа распространяется свободно, можете использовать и модифицировать как угодно.

~~P.S. писать readme всё ещё сложнее чем питонировать~~