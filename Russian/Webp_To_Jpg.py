import os
from PIL import Image

# ------------------------------------------------------------
# Настройки путей и параметров конвертации (можно изменить)
# ------------------------------------------------------------


#⚠️⚠️⚠️ При копировании пути с windows используйте особый тип строки - r"...", где вместо ... Ваш путь к папке, скопированный из Windows. Это поможет избежать ошибки, при которой Python воспримет \U или любой другой символ после косой черты в пути к папке как команду. (а ошибка точно будет!)

input_path = r""               # папка с исходными WebP (пусто = текущая папка)
output_path = r""              # папка для JPG (пусто = создастся "converted" в исходной)
jpg_quality = 85              # качество JPEG (1-100, по умолч. 85)

# ------------------------------------------------------------
# Вспомогательная функция для конвертации байтов в мегабайты
# ------------------------------------------------------------

def bytes_to_mb(bytes_count):
    return bytes_count / (1024 * 1024)

# ------------------------------------------------------------
# Подготовка
# ------------------------------------------------------------

if input_path == "":
    input_path = os.getcwd()

print(f"🔍 Исходная папка: {input_path}")

webp_files = []
for f in os.listdir(input_path):
    if f.lower().endswith('.webp'):
        webp_files.append(f)
        # print(f"📄 Файл {f} занесён в список обработчика.")

total_files = len(webp_files)

if total_files == 0:
    print("❌ WebP-файлы не найдены. Программа завершена.")
    input("\nНажмите Enter для выхода...")
    exit()

print(f"📊 Найдено WebP-файлов: {total_files}")

total_all_webp_size = 0
for f in webp_files:
    file_path = os.path.join(input_path, f)
    total_all_webp_size += os.path.getsize(file_path)

print(f"💾 Общий объём исходных WebP-файлов: {bytes_to_mb(total_all_webp_size):.2f} МБ")

if output_path == "":
    output_dir = os.path.join(input_path, "converted")
else:
    output_dir = output_path

os.makedirs(output_dir, exist_ok=True)
print(f"📁 Результаты будут сохранены в: {output_dir}")

# ------------------------------------------------------------
# Конвертация
# ------------------------------------------------------------

print("\n🚀 Конвертация запущена.")
converted_count = 0
skipped_count = 0
total_original_size_converted = 0
total_converted_size = 0

for idx, filename in enumerate(webp_files, start=1):
    src_path = os.path.join(input_path, filename)
    base_name = os.path.splitext(filename)[0]
    jpg_filename = base_name + ".jpg"
    dst_path = os.path.join(output_dir, jpg_filename)
    
    if os.path.exists(dst_path):
        skipped_count += 1
        # print(f"⏭️ Файл {jpg_filename} уже существует. Пропускаем.")
    else:
        try:
            original_size = os.path.getsize(src_path)
            with Image.open(src_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(dst_path, 'JPEG', quality=jpg_quality)
            converted_size = os.path.getsize(dst_path)
            total_original_size_converted += original_size
            total_converted_size += converted_size
            converted_count += 1
            # print(f"✅ Конвертирован {filename} -> {jpg_filename} ({bytes_to_mb(original_size):.2f} МБ -> {bytes_to_mb(converted_size):.2f} МБ)")
        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")
    
    if idx % 10 == 0 or idx == total_files:
        print(f"📈 Прогресс: {idx}/{total_files} обработано")

# ------------------------------------------------------------
# Итоговая статистика
# ------------------------------------------------------------

print("\n🏁 Конвертация завершена!")
print(f"✅ Сконвертировано файлов: {converted_count}")
print(f"⏭️ Пропущено (уже есть JPG): {skipped_count}")

if converted_count > 0:
    original_total_mb = bytes_to_mb(total_original_size_converted)
    converted_total_mb = bytes_to_mb(total_converted_size)
    print(f"\n📊 Статистика по сконвертированным файлам:")
    print(f"   Суммарный объём исходных WebP: {original_total_mb:.2f} МБ")
    print(f"   Суммарный объём полученных JPG: {converted_total_mb:.2f} МБ")
    print(f"   Изменение: {original_total_mb:.2f} МБ -> {converted_total_mb:.2f} МБ")
    if original_total_mb > 0:
        ratio = (converted_total_mb / original_total_mb) * 100
        print(f"   Размер JPG составляет {ratio:.1f}% от исходного WebP")
else:
    print("📊 Нет новых сконвертированных файлов.")

# ------------------------------------------------------------
# Пауза перед выходом (чтобы окно CMD не закрылось сразу)
# ------------------------------------------------------------
input("\n👋 Нажмите Enter для выхода...")