English (на русском будет тоже, см. в этом же readme ниже):

# WebP to JPEG Converter

A batch conversion tool for WebP images to JPEG, preserving original resolution, displaying statistics, and offering flexible settings.

## Two Versions

- **Standard version (`Webp_To_Jpg_English.py`)** – works only with files in the specified folder (no subfolders).
- **Overkill version (`Webp_To_Jpg_Overkill_English.py`)** – behaves like the standard one by default, but allows recursive scanning of all subfolders and provides advanced options for name conflict handling and file deletion.

Both versions share the same basic settings. The Overkill version adds an extra settings block described below.

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

## Standard Version (`Webp_To_Jpg_English.py`)

### Settings

At the top of the file you'll find:

```python
input_path = r""          # folder with source WebP files (empty = current folder)
output_path = r""         # folder for JPG results (empty = creates "converted" subfolder)
jpg_quality = 85          # JPEG quality (1-100)

# ⚠️ DANGEROUS OPTIONS: Delete original WebP files?
delete_original = False        # set to True to enable deletion (highly recommended to keep False)
delete_on_skip = False         # delete source if file skipped due to conflict (only if delete_original=True)
delete_on_rename = False       # delete source if file renamed due to conflict (only if delete_original=True)

# Deletion method (only used if delete_original=True)
deletion_method = "recycle"    # "recycle" (send to recycle bin) or "permanent" (delete forever)

# Behavior on name conflict
on_name_conflict = "ask"       # "skip", "rename", or "ask" (default ask)
```
- **input_path** – path to the folder with WebP files. If left empty, the current folder is used.

- **output_path** – where to save JPGs. If empty, a subfolder converted is created inside the source folder.

- **jpg_quality** – JPEG quality (default 85 – a good balance between size and quality).

- **delete_original** – master switch for deletion. If False, source files are never deleted.

- **delete_on_skip** – when delete_original=True, deletes the source WebP if conversion was skipped (file already exists as JPG). Logically, you may want this True because the existing JPG is considered correct.

- **delete_on_rename** – when delete_original=True, deletes the source WebP if a conflict was resolved by renaming (e.g., (2)). Logically, you may want this True because the file was still converted (just with a different name).

- **deletion_method** – "recycle" (recycle bin, requires send2trash) or "permanent" (irreversible). Recommended "recycle".

- **on_name_conflict** – behavior when a JPG with the same name already exists (see below).

If delete_original = False, then delete_on_skip and delete_on_rename are ignored (even if set to True). The program will warn you about this at startup.

### What it does
1. Finds all .webp files in the specified folder.

2. Shows their count and total size.

3. Converts each file to .jpg at the same resolution.
If a JPG with the same name already exists in the target folder, the file is skipped (the original is not deleted).

4. Displays progress every 10 files and final statistics (sizes before/after, percentage change).

5. Waits for Enter before closing, so you can read the results.

### Example output
```text
🔍 Source folder: D:\Photos\2024
📊 WebP files found: 124
💾 Total size of source WebP files: 245.78 MB
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

## Overkill Version (Webp_To_Jpg_Overkill_English.py)
This version includes all features of the standard one but adds recursive subfolder scanning and fine-grained control over name conflicts and deletion. Please read the warnings in the script and during execution carefully.

### Additional settings (OVERKILL block)
```python
overkill_mode = False      # True = scan all subfolders
exclude_folders = []       # list of folder names or relative paths to exclude

delete_original = False    # delete source WebP after conversion (default False)
delete_on_skip = False     # delete source WebP when skipped (only if delete_original=True)
delete_on_rename = False   # delete source WebP when renamed (only if delete_original=True)

deletion_method = "recycle"   # "recycle" (recycle bin) or "permanent"
on_recycle_error = "ask"      # action on recycle bin error: "ask", "permanent", "skip", "stop"

save_in_place = False      # True = save JPG next to WebP, False = all into one folder
on_name_conflict = "ask"   # "rename", "skip", or "ask" (default ask)
```
delete_on_skip and delete_on_rename work exactly as in the standard version: they only take effect if delete_original = True. Otherwise they are ignored (with a warning).

### Explanations
- **overkill_mode** – if True, the program traverses all subfolders inside input_path.

- **exclude_folders** – list of folders to skip even when overkill_mode=True. You can use simple folder names (e.g., "temp") or relative paths ("docs/old"). Spaces and non-English characters are supported.

- **delete_original** – whether to delete the source WebP after successful conversion (dangerous!).

- **delete_on_skip** – whether to delete the source WebP if conversion was skipped due to a name conflict (also dangerous!).

- **deletion_method** – "recycle" (send to recycle bin) or "permanent" (delete forever). Recycle bin requires send2trash.

- **`on_recycle_error`** – what to do if sending to recycle bin fails:

  - `"ask"` – ask the user (default)

  - `"permanent"` – delete permanently

  - `"skip"` – skip deletion

  - `"stop"` – stop the program

- **save_in_place** – if True, the JPG is created in the same folder as the WebP; if False, all JPGs are collected in a single folder (set by output_path or a default overkill_converted folder).

- **`on_name_conflict`** – behavior when a JPG with the same name already exists in the target folder:

  - `"rename"` – automatically add a number like (2), (3), etc.

  - `"skip"` – skip the file

  - `"ask"` – ask the user (default)

If you know what you are doing, you may need to choose something other than ask.

### Overkill version specifics
- When overkill_mode is enabled, the program first displays a tree of all folders that will be affected and asks for confirmation before proceeding. You'll see which folders are processed and which are excluded.

- If a name conflict occurs and on_name_conflict = "ask", the program shows a list of existing JPG files with that name (including their sizes) and prompts you to choose an action.

- On recycle bin errors, the program may ask further questions (if on_recycle_error = "ask").

- File deletion (if enabled) goes to the recycle bin by default (if send2trash is installed), allowing you to recover files in case of a mistake.

### Example configuration for recursive processing
```python
input_path = r"D:\My Storage\Photos"
overkill_mode = True
exclude_folders = ["temp", "private", "Secret folder"]
delete_original = False          # don't delete until you've verified the results
save_in_place = True             # JPGs saved next to WebP
on_name_conflict = "ask"         # ask on conflict
```

### Developer's warnings (for Overkill version)
> **A story of disaster:**
> The overconfident developer once rushed, enabled recursive scanning and original deletion, not fully remembering his storage structure. Not everything could be recovered. To prevent you from repeating this mistake, the program now:
> - asks for confirmation after displaying the folder tree;
> - offers choices on name conflicts;
> - uses the recycle bin by default (if send2trash is installed).

> **For your safety:**
> - Install colorama – colorful warnings will catch your attention.
> - Install send2trash – accidentally deleted files will go to the recycle bin instead of vanishing forever.
> - Run the program by double-clicking, not via IDLE – colors will work properly.

> **And most importantly:**
> The developer has thoroughly tested all possible configuration combinations, but something might still have been overlooked. The chance is extremely small, but not zero.
> **It is HIGHLY RECOMMENDED to work on a DUPLICATE/COPY of your storage.**
> After verifying that everything is correct, simply replace the original with the modified copy (delete the original and paste the new folder).

### License
The program is distributed under the MIT license. Use at your own risk.

<br>

# Конвертер WebP в JPEG

Программа для пакетной конвертации изображений WebP в JPEG с сохранением исходного разрешения, подсчётом статистики и гибкими настройками.

## Две версии программы

- **Обычная версия (`Webp_To_Jpg.py`)** – работает только с файлами в указанной папке (без подпапок).
- **Overkill-версия (`Webp_To_Jpg_Overkill.py`)** – по умолчанию ведёт себя как обычная, но позволяет включить рекурсивный обход всех подпапок и предоставляет расширенные возможности управления конфликтами имён и удалением файлов.

Обе версии используют одинаковый базовый набор настроек. Overkill-версия добавляет блок дополнительных параметров, описанный ниже.

## Требования

- Python **3.6** или выше
- Библиотека Pillow (установка: `pip install Pillow`)
- (Рекомендуется) `colorama` для цветного вывода в командной строке: `pip install colorama`
- (Рекомендуется) `send2trash` для отправки файлов в корзину вместо безвозвратного удаления: `pip install send2trash`

## Важные рекомендации перед использованием (особенно для Overkill-версии)

1. **Запускайте программу двойным кликом** (или в командной строке), а не через IDLE – так цветное оформление будет работать корректно.
2. **Установите `colorama` и `send2trash`** – это повысит безопасность (цветные предупреждения легче заметить, а корзина позволит восстановить файлы в случае ошибки).
3. **Всегда работайте с копией своих данных!** Разработчик тщательно проверил все возможные конфигурации, но существует небольшой шанс упущения. Сначала запустите программу на дубликате хранилища, убедитесь, что всё работает как надо, и только потом применяйте к оригиналу.
> **Самый надёжный способ не ошибиться Вам и не дать ошибиться программе – всегда работать с дубликатом/копией хранилища, а после правильной отработки просто заменить исходное хранилище на получившееся.**

---

## Обычная версия (`Webp_To_Jpg.py`)

### Настройки

В начале файла найдите блок настроек:

```python
input_path = r""          # папка с исходными WebP (пусто = текущая папка)
output_path = r""         # папка для JPG (пусто = создаст подпапку "converted")
jpg_quality = 85          # качество JPEG (1-100)

# ⚠️ ОПАСНЫЕ ОПЦИИ: Удалять исходные WebP?
delete_original = False        # установите True, чтобы включить удаление (настоятельно рекомендуется False)?
delete_on_skip = False         # удалять исходный WebP при пропуске (только если delete_original=True)?
delete_on_rename = False       # удалять исходный WebP при переименовании (только если delete_original=True)?

# Способ удаления (используется только при delete_original=True)
deletion_method = "recycle"    # "recycle" (в корзину) или "permanent" (безвозвратно)

# Поведение при конфликте имён
on_name_conflict = "ask"       # "skip", "rename" или "ask" (по умолчанию ask)
```
- **input_path** – путь к папке с WebP. Если оставить пустым, используется текущая папка.

- **output_path** – куда сохранять JPG. Если пусто, создаётся подпапка converted в исходной папке.

- **jpg_quality** – качество JPEG (по умолчанию 85 – хороший баланс размера и качества).

- **delete_original** – главный выключатель удаления. Если False, исходные файлы никогда не удаляются.

- **delete_on_skip** – при delete_original=True удаляет исходный WebP, если конвертация была пропущена (файл уже существует в виде JPG). Логично включить, так как существующий JPG считается верным.

- **delete_on_rename** – при delete_original=True удаляет исходный WebP, если конфликт разрешён переименованием (например, создан файл с номером). Логично включить, так как файл всё равно сконвертирован (хоть и с другим именем).

- **deletion_method** – "recycle" (в корзину, требует send2trash) или "permanent" (безвозвратно). Рекомендуется "recycle".

- **on_name_conflict** – поведение при конфликте имён (см. выше).

Если delete_original = False, то delete_on_skip и delete_on_rename игнорируются (даже если установлены в True).


### Что делает программа
1. Находит все файлы .webp в указанной папке.

2. Показывает их количество и общий объём.

3. Конвертирует каждый файл в .jpg с тем же разрешением.
Если в целевой папке уже есть .jpg с таким именем, файл пропускается (оригинал не удаляется).

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
## Overkill-версия (Webp_To_Jpg_Overkill.py)
Эта версия включает все возможности обычной, но добавляет режим рекурсивной обработки подпапок и тонкое управление конфликтами имён и удалением. Внимательно прочитайте предупреждения в начале файла и в процессе работы программы.

### Дополнительные настройки (блок OVERKILL)
```python
overkill_mode = False      # True = сканировать все подпапки
exclude_folders = []       # список папок или относительных путей для исключения

delete_original = False    # удалять исходные WebP после конвертации (по умолчанию False)?
delete_on_skip = False     # удалять исходные WebP при пропуске (только если delete_original=True)?
delete_on_rename = False   # удалять исходные WebP при переименовании (только если delete_original=True)?

deletion_method = "recycle"   # "recycle" (в корзину) или "permanent" (безвозвратно)
on_recycle_error = "ask"      # действие при ошибке отправки в корзину: "ask", "permanent", "skip", "stop"

save_in_place = False      # True = JPG сохранять рядом с WebP, False = все в одну папку
on_name_conflict = "ask"   # поведение при конфликте имени. "rename", "skip" или "ask" (по умолчанию ask)
```
### Пояснения
- **overkill_mode** – если True, программа обойдёт все подпапки внутри input_path.

- **exclude_folders** – список папок, которые не нужно обрабатывать (даже если overkill_mode=True). Можно указывать как имена папок (например, "temp"), так и относительные пути ("docs/old"). Поддерживаются пробелы и русские буквы.

- **delete_original** – удалять ли исходный WebP после успешной конвертации? (опасно!).

- **delete_on_skip** – удалять ли исходный WebP, если конвертация была пропущена из-за конфликта имён? (тоже опасно!).

- **deletion_method** – "recycle" (отправлять в корзину) или "permanent" (удалять навсегда). Для корзины требуется send2trash.

- **`on_recycle_error`** – что делать, если не удалось отправить в корзину:
  - `"ask"` – спросить пользователя (по умолчанию)
  - `"permanent"` – удалить безвозвратно
  - `"skip"` – пропустить удаление
  - `"stop"` – остановить программу

- **save_in_place** – если True, JPG будет создан в той же папке, где лежит WebP; если False – все JPG собираются в единую папку (задаётся output_path или создаётся overkill_converted).

- **on_name_conflict** – поведение при конфликте имён (когда в целевой папке уже есть JPG с таким же именем):

  - "rename" – автоматически добавлять номер (2), (3) и т.д.

  - "skip" – пропускать файл,

  - "ask" – спрашивать пользователя (по умолчанию).

  Если Вы знаете, что делаете, Вам может потребоваться выбрать что-то, кроме ask.

### Особенности работы Overkill-версии
- При включённом overkill_mode программа сначала покажет дерево всех папок, которые будут затронуты, и попросит подтверждение для продолжения. Вы увидите, какие папки обрабатываются, а какие исключены.

- Если в процессе работы возникнет конфликт имён и включён режим "ask", программа покажет список уже существующих JPG с этим именем (включая их размеры) и предложит выбрать действие.

- При ошибках отправки в корзину программа может задать уточняющие вопросы (если on_recycle_error = "ask").

- Удаление файлов (если включено) по умолчанию происходит через корзину (при наличии send2trash). Это позволяет восстановить файлы, если вы ошиблись.

### Пример настройки для рекурсивной обработки
```python
input_path = r"D:\Моё хранилище\Фото"
overkill_mode = True
exclude_folders = ["temp", "private", "Секретная папка"]
delete_original = False          # пока не проверите результат – не удаляйте!
save_in_place = True             # JPG сохраняются рядом с WebP
on_name_conflict = "ask"         # спрашивать при конфликте
```

### Предупреждения от разработчика (для Overkill-версии)
> **История одной катастрофы**  
> Самоуверенный разработчик однажды поторопился, включил обход подпапок и удаление оригиналов, не до конца помня структуру своего хранилища. Восстановить всё до конца не удалось. Чтобы вы не повторили эту ошибку, программа теперь:  
> - требует подтверждения после показа дерева папок;  
> - предлагает выбор при конфликтах имён;  
> - по умолчанию использует корзину (если установлена `send2trash`).

> **Для вашей безопасности:**  
> - Установите `colorama` – цветные предупреждения привлекут внимание.  
> - Установите `send2trash` – случайно удалённые файлы окажутся в корзине, а не исчезнут навсегда.  
> - Запускайте программу двойным кликом, а не через IDLE – так цвета будут работать.

> **И главное:**  
> Разработчик тщательно проверил все возможные комбинации настроек, но может случиться так, что что-то было упущено. Шанс на это крайне мал, но не равен нулю.  
> **НАСТОЯТЕЛЬНО РЕКОМЕНДУЕМ работать именно с ДУБЛИКАТОМ/КОПИЕЙ хранилища.**  
> После проверки, что всё сделано правильно, просто замените оригинал на изменённую копию (удалите оригинал и вставьте новую папку).

### Лицензия
Программа распространяется под лицензией MIT. Используйте на свой страх и риск.

~~P.S. писать readme всё ещё сложнее чем питонировать~~

