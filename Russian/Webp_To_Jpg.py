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

# ⚠️⚠️⚠️ При копировании пути с Windows используйте особый тип строки - r"...",
# где вместо ... Ваш путь к папке, скопированный из Windows. Это поможет избежать ошибки,
# при которой Python воспримет \U или любой другой символ после косой черты как команду.
# (а это точно случится!)

input_path = r""               # папка с исходными WebP (пусто = текущая папка)
output_path = r""              # папка для JPG (пусто = создаст подпапку "converted" в папке, над которой ведётся работа (input_path))
jpg_quality = 85               # качество JPEG (1-100, по умолч. 85)

# ⚠️⚠️⚠️ ОПАСНАЯ ОПЦИЯ: Удалять исходные WebP после успешной конвертации?
# Настоятельно рекомендуется оставить False, а позже удалить файлы вручную через их поиск в проводнике (например, в Windows: [*.webp]).
# Разработчик обжёгся на этом.
delete_original = False

# ⚠️⚠️⚠️ Удалять исходные WebP, если файл был пропущен при конфликте имён?
# Работает только если delete_original = True.
# По умолчанию для защиты стоит False. Но логично предположить, что в случае delete_original = True, вы захотите сделать True, поскольку сконвертированный файл уже существует, и Вы определили его как верный. А значит, оригинал Вам более не нужен.
delete_on_skip = False

# ⚠️⚠️⚠️ Удалять исходные WebP, если при конфликте имён было выбрано переименование?
# Работает только если delete_original = True.
# По умолчанию для защиты стоит False. Но логично предположить, что в случае delete_original = True, вы захотите сделать True, поскольку новый файл всё равно создан, просто с переименовыванием. А значит, оригинал Вам более не нужен.
delete_on_rename = False

# ------------------------------------------------------------
# Настройки удаления (безвозвратно или в корзину)
# ------------------------------------------------------------
# Способ удаления файлов:
#   "recycle"   - отправлять в корзину (требуется библиотека send2trash, иначе будет безвозвратное удаление)
#   "permanent" - удалять безвозвратно
deletion_method = "recycle"     # по умолчанию корзина

# ------------------------------------------------------------
# Настройка поведения при конфликте имён (когда JPG с таким именем уже существует)
# ------------------------------------------------------------
# Возможные значения:
#   "skip"   - пропускать конвертацию этого файла
#   "rename" - автоматически переименовывать, добавляя (2), (3) и т.д.
#   "ask"    - спрашивать пользователя, что делать (по умолчанию)
on_name_conflict = "ask"

# ------------------------------------------------------------
# Проверка корректности настроек
# ------------------------------------------------------------
def validate_settings():
    errors = []
    
    # Проверка delete_original
    if not isinstance(delete_original, bool):
        errors.append(f"delete_original должно быть True или False, получено: {delete_original} (тип {type(delete_original).__name__})")
    
    # Проверка delete_on_skip
    if not isinstance(delete_on_skip, bool):
        errors.append(f"delete_on_skip должно быть True или False, получено: {delete_on_skip} (тип {type(delete_on_skip).__name__})")
    
    # Проверка delete_on_rename
    if not isinstance(delete_on_rename, bool):
        errors.append(f"delete_on_rename должно быть True или False, получено: {delete_on_rename} (тип {type(delete_on_rename).__name__})")
    
    # Проверка jpg_quality (должно быть целым числом от 1 до 100)
    if not isinstance(jpg_quality, int):
        errors.append(f"jpg_quality должно быть целым числом, получено: {jpg_quality} (тип {type(jpg_quality).__name__})")
    elif not (1 <= jpg_quality <= 100):
        errors.append(f"jpg_quality должно быть в диапазоне от 1 до 100, получено: {jpg_quality}")
    
    # Проверка deletion_method
    valid_deletion = ["recycle", "permanent"]
    if deletion_method not in valid_deletion:
        errors.append(f"deletion_method должно быть одним из {valid_deletion}, получено: {deletion_method}")
    
    # Проверка on_name_conflict
    valid_conflict = ["skip", "rename", "ask"]
    if on_name_conflict not in valid_conflict:
        errors.append(f"on_name_conflict должно быть одним из {valid_conflict}, получено: {on_name_conflict}")
    
    return errors

# Выполняем проверку
validation_errors = validate_settings()
if validation_errors:
    print(f"{Fore.RED}❌ Обнаружены ошибки в настройках:{Style.RESET_ALL}")
    for err in validation_errors:
        print(f"   {Fore.RED}• {err}{Style.RESET_ALL}")
    print()
    input(f"{Fore.CYAN}Нажмите Enter для выхода...{Style.RESET_ALL}")
    sys.exit(1)

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
    """Удаляет файл согласно настройкам deletion_method."""
    if deletion_method == "permanent":
        try:
            os.remove(file_path)
            return True, None
        except Exception as e:
            return False, str(e)
    else:  # recycle
        try:
            send2trash(file_path)
            return True, None
        except Exception as e:
            return False, str(e)

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
            name_without_ext = os.path.splitext(f)[0]
            if name_without_ext == base_name:
                full = os.path.join(directory, f)
                size = os.path.getsize(full)
                existing.append({'name': f, 'size': size, 'number': 0})
            elif name_without_ext.startswith(base_name + " ("):
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
# Вспомогательная функция: показать информацию о конфликте (улучшенная читаемость)
# ------------------------------------------------------------
def show_conflict_info(base_name, existing_list, new_file_size, dest_dir):
    print(f"\n{Fore.YELLOW}⚠️ Конфликт имён для файла {Fore.CYAN}{Style.BRIGHT}{base_name}.jpg{Style.RESET_ALL}")
    print(f"   Целевая папка: {dest_dir}")
    print()
    # Выравнивание: "Новый файл:" (11 символов) + 3 пробела = 14 символов,
    # "Существующий:" (13 символов) + 1 пробел = 14 символов.
    # Имена файлов начинаются с одной позиции.
    print(f"   {Fore.CYAN}Новый файл:   {Style.RESET_ALL}{Fore.CYAN}{Style.BRIGHT}{base_name}.jpg{Style.RESET_ALL} (исходный WebP: {format_size(new_file_size)})")
    for item in sorted(existing_list, key=lambda x: x['number']):
        print(f"   {Fore.CYAN}Существующий:{Style.RESET_ALL} {Fore.CYAN}{item['name']}{Style.RESET_ALL} ({format_size(item['size'])})")
    print()

# ------------------------------------------------------------
# Подготовка
# ------------------------------------------------------------
# Если input_path не пустой, проверяем его существование
if input_path != "" and not os.path.exists(input_path):
    print(f"{Fore.RED}❌ Указанная папка не существует: {input_path}{Style.RESET_ALL}")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

if input_path == "":
    input_path = os.getcwd()

print(f"{Fore.BLUE}🔍 Исходная папка:{Style.RESET_ALL} {input_path}")
print()  # отступ

webp_files = []
for f in os.listdir(input_path):
    if f.lower().endswith('.webp'):
        webp_files.append(f)
        # print(f"📄 Файл {f} занесён в список обработчика.")

total_files = len(webp_files)

if total_files == 0:
    print(f"{Fore.RED}❌ WebP-файлы не найдены. Программа завершена.{Style.RESET_ALL}")
    input("\nНажмите Enter для выхода...")
    exit()

print(f"{Fore.BLUE}📊 Найдено WebP-файлов:{Style.RESET_ALL} {total_files}")

total_all_webp_size = 0
for f in webp_files:
    file_path = os.path.join(input_path, f)
    total_all_webp_size += os.path.getsize(file_path)

print(f"{Fore.BLUE}💾 Общий объём исходных WebP-файлов:{Style.RESET_ALL} {format_size(total_all_webp_size)}")

if output_path == "":
    output_dir = os.path.join(input_path, "converted")
else:
    output_dir = output_path

os.makedirs(output_dir, exist_ok=True)
print(f"{Fore.CYAN}📁 Результаты будут сохранены в:{Style.RESET_ALL} {output_dir}")

# ------------------------------------------------------------
# Конвертация
# ------------------------------------------------------------
print(f"\n{Fore.GREEN}🚀 Конвертация запущена.{Style.RESET_ALL}")
converted_count = 0
skipped_count = 0
total_original_size_converted = 0
total_converted_size = 0

for idx, filename in enumerate(webp_files, start=1):
    src_path = os.path.join(input_path, filename)
    base_name = os.path.splitext(filename)[0]
    original_size = os.path.getsize(src_path)

    # Проверяем существующие JPG в целевой папке
    existing_jpgs = get_existing_jpgs(output_dir, base_name)
    dst_path = None
    action_performed = False  # флаг, что файл уже обработан (пропущен или переименован)
    was_conflict = bool(existing_jpgs)  # запоминаем, был ли конфликт
    was_renamed = False       # флаг, что было выбрано переименование

    if existing_jpgs:
        # Конфликт имён
        print()  # отступ для читаемости
        if on_name_conflict == "skip":
            skipped_count += 1
            action_performed = True
            if delete_original and delete_on_skip:
                success, error = delete_file(src_path)
                if success:
                    print(f"{Fore.CYAN}🗑️ Исходный файл {filename} удалён/отправлен в корзину (пропуск по конфликту){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Не удалось удалить {filename}: {error}{Style.RESET_ALL}")
        elif on_name_conflict == "rename":
            show_conflict_info(base_name, existing_jpgs, original_size, output_dir)
            next_num = get_next_number(existing_jpgs)
            new_filename = f"{base_name} ({next_num}).jpg"
            dst_path = os.path.join(output_dir, new_filename)
            print(f"{Fore.CYAN}   Будет создан файл: {new_filename}{Style.RESET_ALL}")
            action_performed = False  # будем конвертировать с новым именем
            was_renamed = True
        elif on_name_conflict == "ask":
            show_conflict_info(base_name, existing_jpgs, original_size, output_dir)
            while True:
                print(f"{Fore.YELLOW}Выберите действие:{Style.RESET_ALL}")
                print("   1 - Переименовать и сохранить (создать файл с номером)")
                print("   2 - Пропустить этот файл")
                print("   3 - Отменить весь процесс (выйти)")
                choice = input("Введите 1, 2 или 3: ").strip()
                if choice == '1':
                    next_num = get_next_number(existing_jpgs)
                    new_filename = f"{base_name} ({next_num}).jpg"
                    dst_path = os.path.join(output_dir, new_filename)
                    print(f"{Fore.CYAN}   Будет создан файл: {new_filename}{Style.RESET_ALL}")
                    action_performed = False
                    was_renamed = True
                    break
                elif choice == '2':
                    skipped_count += 1
                    action_performed = True
                    if delete_original and delete_on_skip:
                        success, error = delete_file(src_path)
                        if success:
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
            # Неизвестное значение – по умолчанию пропускаем
            skipped_count += 1
            action_performed = True
            if delete_original and delete_on_skip:
                success, error = delete_file(src_path)
                if success:
                    print(f"{Fore.CYAN}🗑️ Исходный файл {filename} удалён/отправлен в корзину (пропуск по умолчанию){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Не удалось удалить {filename}: {error}{Style.RESET_ALL}")
    else:
        # Конфликта нет
        dst_path = os.path.join(output_dir, base_name + ".jpg")
        action_performed = False

    # Если файл не пропущен и путь назначения определён, конвертируем
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

            # Решение об удалении исходного файла
            should_delete = False
            if delete_original:
                if was_conflict and was_renamed:
                    # При конфликте и переименовании учитываем delete_on_rename
                    should_delete = delete_on_rename
                else:
                    # Без конфликта – просто delete_original
                    should_delete = True

            if should_delete:
                success, error = delete_file(src_path)
                if success:
                    print(f"{Fore.CYAN}🗑️ Исходный файл {filename} удалён/отправлен в корзину{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Не удалось удалить {filename}: {error}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка при обработке {filename}: {e}{Style.RESET_ALL}")

    # Если был конфликт, добавляем дополнительный отступ
    if existing_jpgs:
        print()

    # Вывод прогресса
    if idx % 10 == 0 or idx == total_files:
        print(f"{Fore.BLUE}📈 Прогресс: {idx}/{total_files} обработано{Style.RESET_ALL}")

# ------------------------------------------------------------
# Итоговая статистика
# ------------------------------------------------------------
print("\n\n")
print(f"{Fore.GREEN}🏁 Конвертация завершена!{Style.RESET_ALL}")
print(f"{Fore.GREEN}✅ Сконвертировано файлов:{Style.RESET_ALL} {converted_count}")
print(f"{Fore.YELLOW}⏭️ Пропущено (конфликт имён):{Style.RESET_ALL} {skipped_count}")

if converted_count > 0:
    print(f"\n{Fore.CYAN}📊 Статистика по сконвертированным файлам:{Style.RESET_ALL}")
    print(f"   Суммарный объём исходных WebP: {Fore.YELLOW}{format_size(total_original_size_converted)}{Style.RESET_ALL}")
    print(f"   Суммарный объём полученных JPG: {Fore.YELLOW}{format_size(total_converted_size)}{Style.RESET_ALL}")
    print(f"   Изменение: {Fore.YELLOW}{format_size(total_original_size_converted)}{Style.RESET_ALL} -> {Fore.YELLOW}{format_size(total_converted_size)}{Style.RESET_ALL}")
    if total_original_size_converted > 0:
        ratio = (total_converted_size / total_original_size_converted) * 100
        print(f"   Размер JPG составляет {Fore.YELLOW}{ratio:.1f}%{Style.RESET_ALL} от исходного WebP")
else:
    print("📊 Нет новых сконвертированных файлов.")

# ------------------------------------------------------------
# Пауза перед выходом
# ------------------------------------------------------------
input(f"\n{Fore.CYAN}👋 Нажмите Enter для выхода...{Style.RESET_ALL}")