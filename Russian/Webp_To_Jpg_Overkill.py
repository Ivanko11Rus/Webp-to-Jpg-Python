import os
import sys
from PIL import Image

# ------------------------------------------------------------
# Определение среды выполнения (IDLE не поддерживает цвета)
# ------------------------------------------------------------
def is_running_in_idle():
    """Проверяет, запущен ли скрипт в IDLE (где ANSI-цвета не работают)."""
    return 'idlelib' in sys.modules or 'idlelib.run' in sys.modules

# Для цветного вывода в терминале (Windows CMD поддерживается)
try:
    from colorama import init, Fore, Style
    init()  # инициализация для Windows
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Если мы в IDLE, отключаем цвета (даже если colorama установлена)
if is_running_in_idle():
    COLORAMA_AVAILABLE = False

if not COLORAMA_AVAILABLE:
    # Заглушки для цветов (пустые строки)
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''
    if not is_running_in_idle():
        # Если colorama не установлена и мы не в IDLE, подскажем пользователю
        print("Для цветного вывода установите colorama: pip install colorama")

# ------------------------------------------------------------
# Настройки: пути и параметры конвертации (можно изменить)
# ------------------------------------------------------------

# ⚠️ При копировании пути с Windows используйте особый тип строки - r"...",
# где вместо ... Ваш путь к папке, скопированный из Windows. Это поможет избежать ошибки,
# при которой Python воспримет \U или любой другой символ после косой черты как команду.
# (иначе ошибка точно будет!)

input_path = r""               # папка с исходными WebP (пусто = текущая папка)
output_path = r""              # папка для JPG (пусто = создаст подпапку, см. ниже)
jpg_quality = 85               # качество JPEG (1-100, по умолч. 85)


# ------------------------------------------------------------
# Режим OVERKILL (рекурсивная обработка всех подпапок)
# ------------------------------------------------------------

# ⚠️⚠️⚠️ РЕЖИМ OVERKILL: если включён, программа найдёт ВСЕ .webp файлы ВО ВСЕХ ПОДПАПКАХ input_path.
# Пожалуйста, перед включением проверьте свои папки! Разработчик однажды поторопился и испортил нужные файлы. И это была катастрофа.
# Используйте список exclude_folders, чтобы исключить некоторые подпапки (см. примеры).

overkill_mode = False           # False = только файлы в основной папке input_path; True = поиск во всех подпапках!

# Список имён папок (или относительных путей), которые НЕ нужно сканировать, когда overkill_mode = True.
# Можно указывать как простые имена папок (например, "backup", "old"), так и подпути вроде "archive/2020".
# Все пути интерпретируются относительно input_path. Примеры:
#   exclude_folders = ["temp", "private"]                    # пропустит любые папки с именами "temp" или "private"
#   exclude_folders = ["temp folder", "private data", "Сюда нельзя", "Сюда нельзя абсолютно точно"]  # имена с пробелами (русские/английские)
#   exclude_folders = ["docs/old"]                           # пропустит конкретную подпапку "docs/old"
# При указании Windows-путей с обратными слешами используйте raw-строки или удваивайте слеши:
#   exclude_folders = ["docs/old", r"temp\backup", "archive\\2024"]  # все из перечисленных вариантов сработают

exclude_folders = []            # пустой список = нет исключений

# ⚠️⚠️⚠️ ОПАСНАЯ ОПЦИЯ: Удалять исходные WebP после успешной конвертации?
# Настоятельно рекомендуется оставить False, а позже удалить файлы вручную через поиск Windows (*.webp).
# Разработчик обжёгся на этом.
# Способ удаления (корзина или безвозвратно) задаётся переменной deletion_method ниже.
delete_original = False

# ⚠️⚠️⚠️ Удалять исходные WebP, если файл был пропущен при конфликте имён?
# По умолчанию установлено False, потому что легко поторопиться и удалить нужные файлы.
# Включайте эту опцию, только если абсолютно уверены в понимании своего хранилища. Разработчик обжёгся на этом.
delete_on_skip = False


# ------------------------------------------------------------
# Настройки удаления (безвозвратно или в корзину)
# ------------------------------------------------------------
# Способ удаления файлов:
#   "recycle"   - отправлять в корзину (требуется библиотека send2trash, иначе будет безвозвратное удаление)
#   "permanent" - удалять безвозвратно
deletion_method = "recycle"     # по умолчанию корзина

# Действие при ошибке отправки в корзину (если используется recycle):
#   "ask"        - спросить пользователя (по умолчанию)
#   "permanent"  - безвозвратно удалить
#   "skip"       - пропустить файл (не удалять, не конвертировать?)
#   "stop"       - остановить программу
on_recycle_error = "ask"

# ------------------------------------------------------------
# Сохранять JPG в той же папке, где найден WebP?
#   True  -> JPG будет создан рядом с исходным WebP.
#   False -> Все JPG сохранятся в единую папку (output_path, либо папка overkill_converted по умолчанию).
save_in_place = False

# ------------------------------------------------------------
# Настройка поведения при конфликте имён (когда JPG с таким именем уже существует)
# ------------------------------------------------------------
# Возможные значения:
#   "rename" - автоматически переименовывать, добавляя (2), (3) и т.д.
#   "skip"   - пропускать конвертацию этого файла
#   "ask"    - спрашивать пользователя, что делать (по умолчанию)
on_name_conflict = "ask"

# ------------------------------------------------------------
# Проверка наличия send2trash для корзины
# ------------------------------------------------------------
RECYCLE_BIN_AVAILABLE = False
if deletion_method == "recycle":
    try:
        from send2trash import send2trash
        RECYCLE_BIN_AVAILABLE = True
    except ImportError:
        print(f"{Fore.YELLOW}⚠️ Библиотека send2trash не установлена. Файлы будут удаляться безвозвратно.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Для работы с корзиной установите: pip install send2trash{Style.RESET_ALL}")
        print()
        input(f"{Fore.CYAN}Нажмите Enter, чтобы продолжить с безвозвратным удалением, или закройте окно для отмены...{Style.RESET_ALL}")
        deletion_method = "permanent"  # автоматически переключаем на безвозвратное

# ------------------------------------------------------------
# Вспомогательная функция: удаление файла с учётом настроек
# ------------------------------------------------------------
def delete_file(file_path):
    """Удаляет файл согласно настройкам deletion_method и on_recycle_error."""
    global deletion_method  # может измениться, если пользователь выберет опцию "навсегда" при ошибке
    
    if deletion_method == "permanent":
        try:
            os.remove(file_path)
            return True, None
        except Exception as e:
            return False, str(e)
    
    # Иначе deletion_method == "recycle" и RECYCLE_BIN_AVAILABLE должно быть True
    try:
        send2trash(file_path)
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Обработка ошибки согласно on_recycle_error
        if on_recycle_error == "permanent":
            # Пробуем безвозвратно
            try:
                os.remove(file_path)
                print(f"{Fore.YELLOW}⚠️ Не удалось отправить в корзину, выполнено безвозвратное удаление.{Style.RESET_ALL}")
                return True, None
            except Exception as e2:
                return False, f"Ошибка безвозвратного удаления: {e2}"
        elif on_recycle_error == "skip":
            # Пропускаем файл (не удаляем)
            return False, f"Ошибка корзины, файл пропущен: {error_msg}"
        elif on_recycle_error == "stop":
            # Останавливаем программу
            print(f"{Fore.RED}❌ Ошибка отправки в корзину: {error_msg}{Style.RESET_ALL}")
            print(f"{Fore.RED}Программа остановлена по настройке on_recycle_error = 'stop'.{Style.RESET_ALL}")
            sys.exit(1)
        else:  # "ask" или любое другое значение по умолчанию
            while True:
                print(f"\n{Fore.RED}❌ Ошибка отправки файла в корзину: {error_msg}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Файл: {file_path}{Style.RESET_ALL}")
                print("Выберите действие:")
                print("   1 - Попытаться ещё раз (отправить в корзину снова)")
                print("   2 - Пропустить этот файл (не удалять, продолжить)")
                print("   3 - Удалить безвозвратно (для этого файла)")
                print("   4 - Для всех последующих файлов использовать безвозвратное удаление")
                print("   5 - Остановить программу")
                choice = input("Введите 1, 2, 3, 4 или 5: ").strip()
                if choice == '1':
                    try:
                        send2trash(file_path)
                        return True, None
                    except Exception as e2:
                        error_msg = str(e2)
                        continue  # опять покажем меню
                elif choice == '2':
                    return False, f"Пропущено по запросу: {error_msg}"
                elif choice == '3':
                    try:
                        os.remove(file_path)
                        return True, None
                    except Exception as e2:
                        return False, f"Ошибка безвозвратного удаления: {e2}"
                elif choice == '4':
                    # Переключаем режим на permanent для всей сессии
                    deletion_method = "permanent"
                    try:
                        os.remove(file_path)
                        return True, None
                    except Exception as e2:
                        return False, f"Ошибка безвозвратного удаления: {e2}"
                elif choice == '5':
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}Неверный ввод. Пожалуйста, введите 1-5.{Style.RESET_ALL}")

# ------------------------------------------------------------
# Вспомогательная функция: форматирование размера в байтах в человекочитаемый вид
# ------------------------------------------------------------
def format_size(bytes_count):
    """Конвертирует байты в строку с автоматическим выбором единиц (Б, КБ, МБ, ГБ, ТБ)."""
    if bytes_count < 1024:
        return f"{bytes_count} Б"
    elif bytes_count < 1024**2:
        return f"{bytes_count/1024:.2f} КБ"
    elif bytes_count < 1024**3:
        return f"{bytes_count/1024**2:.2f} МБ"
    elif bytes_count < 1024**4:
        return f"{bytes_count/1024**3:.2f} ГБ"
    else:
        return f"{bytes_count/1024**4:.2f} ТБ"

# ------------------------------------------------------------
# Вспомогательная функция: получить все WebP-файлы (рекурсивно с исключениями)
# ------------------------------------------------------------
def get_webp_files(root_path, recursive=False, exclude_list=None):
    if exclude_list is None:
        exclude_list = []
    # Нормализуем все элементы exclude_list: заменяем обратные слеши на прямые для единообразия
    exclude_norm = [e.replace('\\', '/') for e in exclude_list]
    webp_files = []
    if recursive:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Относительный путь текущей папки
            rel_dir = os.path.relpath(dirpath, root_path)
            if rel_dir == '.':
                rel_dir = ''
            # Приводим к единому виду (прямые слеши)
            rel_dir_norm = rel_dir.replace('\\', '/')
            # Удаляем исключённые папки из dirnames (чтобы os.walk не заходил в них)
            to_remove = []
            for d in dirnames:
                # Полный относительный путь к подпапке
                full_rel = os.path.join(rel_dir_norm, d).replace('\\', '/')
                # Проверяем, есть ли эта папка (по имени или полному пути) в списке исключений
                if d in exclude_norm or full_rel in exclude_norm:
                    to_remove.append(d)
            for d in to_remove:
                dirnames.remove(d)
            # Теперь собираем .webp файлы
            for f in filenames:
                if f.lower().endswith('.webp'):
                    webp_files.append(os.path.join(dirpath, f))
    else:
        # Нерекурсивно: только файлы непосредственно в root_path
        for f in os.listdir(root_path):
            if f.lower().endswith('.webp'):
                webp_files.append(os.path.join(root_path, f))
    return webp_files

# ------------------------------------------------------------
# Вспомогательная функция: получить список всех существующих JPG с таким же базовым именем
# ------------------------------------------------------------
def get_existing_jpgs(directory, base_name):
    """Возвращает список словарей с информацией о существующих файлах JPG,
       начинающихся с base_name (возможно с суффиксом (n))."""
    existing = []
    if not os.path.exists(directory):
        return existing
    for f in os.listdir(directory):
        if f.lower().endswith('.jpg'):
            # Проверяем, начинается ли имя с base_name
            name_without_ext = os.path.splitext(f)[0]
            if name_without_ext == base_name:
                # точное совпадение
                full = os.path.join(directory, f)
                size = os.path.getsize(full)
                existing.append({'name': f, 'size': size, 'number': 0})
            elif name_without_ext.startswith(base_name + " ("):
                # проверяем, что после скобки идёт число и закрывающая скобка
                rest = name_without_ext[len(base_name)+2:]  # пропускаем " ("
                if rest.endswith(')') and rest[:-1].isdigit():
                    num = int(rest[:-1])
                    full = os.path.join(directory, f)
                    size = os.path.getsize(full)
                    existing.append({'name': f, 'size': size, 'number': num})
    return existing

# ------------------------------------------------------------
# Вспомогательная функция: определить следующий номер для переименования
# ------------------------------------------------------------
def get_next_number(existing_list):
    """Находит максимальный номер среди существующих и возвращает следующий."""
    max_num = 0
    for item in existing_list:
        if item['number'] > max_num:
            max_num = item['number']
    return max_num + 1

# ------------------------------------------------------------
# Вспомогательная функция: показать информацию о конфликте
# ------------------------------------------------------------
def show_conflict_info(base_name, existing_list, new_file_size, dest_dir):
    print(f"\n{Fore.YELLOW}⚠️ Конфликт имён для файла {base_name}.jpg{Style.RESET_ALL}")
    print(f"   Целевая папка: {dest_dir}")
    print(f"   Размер нового файла: {format_size(new_file_size)}")
    print(f"   Существующие файлы в этой папке с похожим именем:")
    for item in sorted(existing_list, key=lambda x: x['number']):
        print(f"     - {item['name']} ({format_size(item['size'])})")
    print()

# ------------------------------------------------------------
# Функция для красивого вывода дерева папок
# ------------------------------------------------------------
def print_folder_tree(folder_paths, root_display_name):
    """Выводит дерево папок на основе списка относительных путей."""
    if not folder_paths:
        return
    # Строим вложенный словарь
    tree = {}
    for path in folder_paths:
        if path == '':
            continue  # корень обрабатываем отдельно
        parts = path.split(os.sep)
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    # Рекурсивный вывод
    def print_node(node, prefix=''):
        items = list(node.items())
        for i, (name, subtree) in enumerate(items):
            is_last = (i == len(items) - 1)
            if is_last:
                print(f"{prefix}└── {name}")
                new_prefix = prefix + '    '
            else:
                print(f"{prefix}├── {name}")
                new_prefix = prefix + '│   '
            if subtree:
                print_node(subtree, new_prefix)

    # Печатаем корень
    print(f"{Fore.CYAN}📁 {root_display_name}/{Style.RESET_ALL}")
    print_node(tree)

# ------------------------------------------------------------
# Подготовка
# ------------------------------------------------------------
if input_path == "":
    input_path = os.getcwd()

print(f"{Fore.BLUE}🔍 Исходная папка:{Style.RESET_ALL} {input_path}")
print()  # Отступ после исходной папки

# Собираем WebP-файлы в зависимости от режима
if overkill_mode:
    print(f"{Fore.MAGENTA}⚡ РЕЖИМ OVERKILL ВКЛЮЧЁН: сканирование всех подпапок (с исключениями)...{Style.RESET_ALL}")
    webp_files = get_webp_files(input_path, recursive=True, exclude_list=exclude_folders)
else:
    webp_files = get_webp_files(input_path, recursive=False)

print()  # Отступ после сообщения о режиме
total_files = len(webp_files)

if total_files == 0:
    print(f"{Fore.RED}❌ WebP-файлы не найдены. Программа завершена.{Style.RESET_ALL}")
    input("\nНажмите Enter для выхода...")
    exit()

print(f"{Fore.BLUE}📊 Найдено WebP-файлов:{Style.RESET_ALL} {total_files}")

# Считаем общий размер всех найденных WebP
total_all_webp_size = 0
for f in webp_files:
    total_all_webp_size += os.path.getsize(f)

print(f"{Fore.BLUE}💾 Общий объём исходных WebP-файлов:{Style.RESET_ALL} {format_size(total_all_webp_size)}")

# Определяем папку для сохранения результатов
if save_in_place:
    output_dir = None   # будет определяться для каждого файла отдельно
    print(f"{Fore.CYAN}📁 Режим сохранения:{Style.RESET_ALL} JPG будут помещены рядом с исходными WebP.")
else:
    if output_path == "":
        if overkill_mode:
            output_dir = os.path.join(input_path, "overkill_converted")
        else:
            output_dir = os.path.join(input_path, "converted")
    else:
        output_dir = output_path
    os.makedirs(output_dir, exist_ok=True)
    print(f"{Fore.CYAN}📁 Все JPG будут сохранены в:{Style.RESET_ALL} {output_dir}")

# Если включён overkill, показываем дерево папок и запрашиваем подтверждение
if overkill_mode:
    # Получаем уникальные папки, содержащие WebP-файлы
    folders_with_webp = set(os.path.dirname(f) for f in webp_files)
    # Преобразуем в относительные пути для отображения
    rel_folders = [os.path.relpath(f, input_path) if os.path.relpath(f, input_path) != '.' else '' for f in folders_with_webp]
    # Показываем дерево
    print(f"\n{Fore.YELLOW}📁 Папки, в которых найдены WebP (будут обработаны):{Style.RESET_ALL}")
    print_folder_tree(rel_folders, os.path.basename(input_path) or input_path)
    # Дополнительные предупреждения
    if exclude_folders:
        print(f"\n{Fore.YELLOW}⏭️ Следующие папки были исключены (не будут обработаны):{Style.RESET_ALL}")
        for ex in exclude_folders:
            # Используем яркий голубой (хорошо виден на чёрном фоне)
            print(f"   {Fore.CYAN}{Style.BRIGHT}❌ {ex}{Style.RESET_ALL}")
    # Добавляем важное предупреждение от разработчика
    print(f"\n{Fore.YELLOW}🔬 РЕКОМЕНДАЦИЯ РАЗРАБОТЧИКА:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   Разработчик тщательно проверил все возможные варианты конфигураций и не обнаружил проблем,{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   но может случиться так, что что-то было упущено из внимания. Шанс на это крайне мал, но не равен нулю.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   НАСТОЯТЕЛЬНО РЕКОМЕНДУЕМ работать именно с ДУБЛИКАТОМ/КОПИЕЙ хранилища.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   После проверки, что всё сделано правильно, просто замените оригинал на изменённую копию{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   (удалите оригинал и вставьте новую папку).{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}⚠️  Вы собираетесь обработать ВСЕ показанные выше папки. Если есть сомнения, закройте программу сейчас – она ещё ничего не изменила.{Style.RESET_ALL}")
    if delete_original:
        print()
        print(f"{Fore.RED}❗❗❗ ВНИМАНИЕ: ВКЛЮЧЁН РЕЖИМ УДАЛЕНИЯ ИСХОДНЫХ ФАЙЛОВ! WebP будут удалены после конвертации.{Style.RESET_ALL}")
    if delete_on_skip:
        print(f"{Fore.RED}❗❗❗ ВНИМАНИЕ: ВКЛЮЧЁН РЕЖИМ УДАЛЕНИЯ ПРИ ПРОПУСКЕ! WebP будут удалены, если конвертация пропущена из-за конфликта.{Style.RESET_ALL}")
    print()
    # Рекомендация запускать в командной строке, а не в IDLE
    if is_running_in_idle():
        print(f"{Fore.YELLOW}💡 Рекомендуется запускать программу двойным кликом (в командной строке),{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   чтобы цветное оформление отображалось корректно.{Style.RESET_ALL}")
        print()
    input(f"{Fore.CYAN}Нажмите Enter для продолжения или закройте окно для отмены...{Style.RESET_ALL}")

# ------------------------------------------------------------
# Конвертация
# ------------------------------------------------------------
print(f"\n{Fore.GREEN}🚀 Конвертация запущена.{Style.RESET_ALL}")
converted_count = 0
skipped_count = 0
deleted_count = 0
total_original_size_converted = 0
total_converted_size = 0

for idx, src_path in enumerate(webp_files, start=1):
    filename = os.path.basename(src_path)
    base_name = os.path.splitext(filename)[0]
    
    if save_in_place:
        dest_dir = os.path.dirname(src_path)
    else:
        dest_dir = output_dir
    
    # Получаем размер исходного файла (понадобится для информации о конфликте)
    try:
        original_size = os.path.getsize(src_path)
    except:
        original_size = 0

    # Определяем, существует ли уже JPG с таким базовым именем (или вариациями)
    existing_jpgs = get_existing_jpgs(dest_dir, base_name)
    
    # Будем хранить итоговый путь для сохранения
    dst_path = None
    action_performed = False  # флаг, что файл был обработан (конвертирован или пропущен)
    
    if existing_jpgs:
        # Добавляем пустую строку для визуального разделения конфликтов разных файлов
        print()
        # Конфликт: есть один или несколько файлов с таким же базовым именем
        if on_name_conflict == "skip":
            skipped_count += 1
            action_performed = True
            # Если включено удаление при пропуске
            if delete_on_skip:
                success, error = delete_file(src_path)
                if success:
                    deleted_count += 1
                    # Используем CYAN для информационных сообщений об удалении
                    print(f"{Fore.CYAN}🗑️ Исходный файл {filename} удалён/отправлен в корзину (пропуск по конфликту){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Не удалось удалить {filename}: {error}{Style.RESET_ALL}")
            else:
                # Можно вывести информацию о пропуске
                # print(f"{Fore.YELLOW}⏭️ Пропущен {filename} (JPG уже существует){Style.RESET_ALL}")
                pass
        elif on_name_conflict == "rename":
            # Показываем информацию о серии
            show_conflict_info(base_name, existing_jpgs, original_size, dest_dir)
            next_num = get_next_number(existing_jpgs)
            new_filename = f"{base_name} ({next_num}).jpg"
            dst_path = os.path.join(dest_dir, new_filename)
            print(f"{Fore.CYAN}   Будет создан файл: {new_filename}{Style.RESET_ALL}")
            action_performed = False  # дальше будем конвертировать
        elif on_name_conflict == "ask":
            show_conflict_info(base_name, existing_jpgs, original_size, dest_dir)
            # Запрашиваем решение
            while True:
                print(f"{Fore.YELLOW}Выберите действие:{Style.RESET_ALL}")
                print("   1 - Переименовать и сохранить (создать файл с номером)")
                print("   2 - Пропустить этот файл")
                print("   3 - Отменить весь процесс (выйти)")
                choice = input("Введите 1, 2 или 3: ").strip()
                if choice == '1':
                    next_num = get_next_number(existing_jpgs)
                    new_filename = f"{base_name} ({next_num}).jpg"
                    dst_path = os.path.join(dest_dir, new_filename)
                    print(f"{Fore.CYAN}   Будет создан файл: {new_filename}{Style.RESET_ALL}")
                    action_performed = False
                    break
                elif choice == '2':
                    skipped_count += 1
                    action_performed = True
                    # Если включено удаление при пропуске
                    if delete_on_skip:
                        success, error = delete_file(src_path)
                        if success:
                            deleted_count += 1
                            print(f"{Fore.CYAN}🗑️ Исходный файл {filename} удалён/отправлен в корзину (пропуск по запросу){Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}❌ Не удалось удалить {filename}: {error}{Style.RESET_ALL}")
                    break
                elif choice == '3':
                    print(f"{Fore.RED}Отмена по запросу пользователя.{Style.RESET_ALL}")
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}Неверный ввод. Пожалуйста, введите 1, 2 или 3.{Style.RESET_ALL}")
        else:
            # Неизвестное значение - действуем как rename
            show_conflict_info(base_name, existing_jpgs, original_size, dest_dir)
            next_num = get_next_number(existing_jpgs)
            new_filename = f"{base_name} ({next_num}).jpg"
            dst_path = os.path.join(dest_dir, new_filename)
            print(f"{Fore.CYAN}   Будет создан файл: {new_filename}{Style.RESET_ALL}")
            action_performed = False
    else:
        # Конфликта нет
        dst_path = os.path.join(dest_dir, base_name + ".jpg")
        action_performed = False
    
    # Если файл не был пропущен, конвертируем
    if not action_performed and dst_path is not None:
        try:
            with Image.open(src_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(dst_path, 'JPEG', quality=jpg_quality)
            converted_size = os.path.getsize(dst_path)
            
            total_original_size_converted += original_size
            total_converted_size += converted_size
            converted_count += 1
            
            if delete_original:
                success, error = delete_file(src_path)
                if success:
                    deleted_count += 1
                    # Используем CYAN для информационных сообщений об удалении
                    print(f"{Fore.CYAN}🗑️ Исходный файл {filename} удалён/отправлен в корзину после конвертации{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Не удалось удалить {filename}: {error}{Style.RESET_ALL}")
            
            # При желании можно раскомментировать для подробного вывода:
            # print(f"✅ Конвертирован {filename} -> {os.path.basename(dst_path)} ({format_size(original_size)} -> {format_size(converted_size)})")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка при обработке {src_path}: {e}{Style.RESET_ALL}")
    
    # Если был конфликт, добавляем дополнительную пустую строку для увеличения отступа между файлами
    if existing_jpgs:
        print()
    
    # Вывод прогресса
    if idx % 10 == 0 or idx == total_files:
        print(f"{Fore.BLUE}📈 Прогресс: {idx}/{total_files} обработано{Style.RESET_ALL}")

# ------------------------------------------------------------
# Итоговая статистика
# ------------------------------------------------------------
# Добавляем две пустые строки перед финальным заголовком для лучшей читаемости
print("\n\n")
print(f"{Fore.GREEN}🏁 Конвертация завершена!{Style.RESET_ALL}")
print(f"{Fore.GREEN}✅ Сконвертировано файлов:{Style.RESET_ALL} {converted_count}")
print(f"{Fore.YELLOW}⏭️ Пропущено (конфликт имён):{Style.RESET_ALL} {skipped_count}")
if delete_original or delete_on_skip:
    # Используем CYAN для итоговой статистики удаления
    print(f"{Fore.CYAN}🗑️ Исходных файлов удалено/отправлено в корзину:{Style.RESET_ALL} {deleted_count}")

if converted_count > 0:
    original_total = total_original_size_converted
    converted_total = total_converted_size
    print(f"\n{Fore.CYAN}📊 Статистика по сконвертированным файлам:{Style.RESET_ALL}")
    print(f"   Суммарный объём исходных WebP: {Fore.YELLOW}{format_size(original_total)}{Style.RESET_ALL}")
    print(f"   Суммарный объём полученных JPG: {Fore.YELLOW}{format_size(converted_total)}{Style.RESET_ALL}")
    print(f"   Изменение: {Fore.YELLOW}{format_size(original_total)}{Style.RESET_ALL} -> {Fore.YELLOW}{format_size(converted_total)}{Style.RESET_ALL}")
    if original_total > 0:
        ratio = (converted_total / original_total) * 100
        print(f"   Размер JPG составляет {Fore.YELLOW}{ratio:.1f}%{Style.RESET_ALL} от исходного WebP")
else:
    print("📊 Новых файлов не сконвертировано.")

# ------------------------------------------------------------
# Пауза перед выходом
# ------------------------------------------------------------
input(f"\n{Fore.CYAN}👋 Нажмите Enter для выхода...{Style.RESET_ALL}")