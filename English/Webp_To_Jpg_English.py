import os
from PIL import Image

# ------------------------------------------------------------
# Settings: paths and conversion parameters (you can change these)
# ------------------------------------------------------------

# ⚠️⚠️⚠️ When copying a Windows path, use a raw string - r"...", where ... is your folder path copied from Windows.
# This prevents Python from interpreting \U or any other character after a backslash as an escape sequence.
# (Otherwise, an error will definitely occur!)

input_path = r""               # folder with source WebP files (empty = current folder)
output_path = r""              # folder for JPG results (empty = creates "converted" subfolder in source folder)
jpg_quality = 85               # JPEG quality (1-100, default 85)

# ------------------------------------------------------------
# Helper function to convert bytes to megabytes
# ------------------------------------------------------------

def bytes_to_mb(bytes_count):
    return bytes_count / (1024 * 1024)

# ------------------------------------------------------------
# Preparation
# ------------------------------------------------------------

if input_path == "":
    input_path = os.getcwd()

print(f"🔍 Source folder: {input_path}")

webp_files = []
for f in os.listdir(input_path):
    if f.lower().endswith('.webp'):
        webp_files.append(f)
        # print(f"📄 File {f} added to processing list.")

total_files = len(webp_files)

if total_files == 0:
    print("❌ No WebP files found. Program finished.")
    input("\nPress Enter to exit...")
    exit()

print(f"📊 WebP files found: {total_files}")

total_all_webp_size = 0
for f in webp_files:
    file_path = os.path.join(input_path, f)
    total_all_webp_size += os.path.getsize(file_path)

print(f"💾 Total size of source WebP files: {bytes_to_mb(total_all_webp_size):.2f} MB")

if output_path == "":
    output_dir = os.path.join(input_path, "converted")
else:
    output_dir = output_path

os.makedirs(output_dir, exist_ok=True)
print(f"📁 Results will be saved in: {output_dir}")

# ------------------------------------------------------------
# Conversion
# ------------------------------------------------------------

print("\n🚀 Conversion started.")
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
        # print(f"⏭️ File {jpg_filename} already exists. Skipping.")
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
            # print(f"✅ Converted {filename} -> {jpg_filename} ({bytes_to_mb(original_size):.2f} MB -> {bytes_to_mb(converted_size):.2f} MB)")
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    if idx % 10 == 0 or idx == total_files:
        print(f"📈 Progress: {idx}/{total_files} processed")

# ------------------------------------------------------------
# Final statistics
# ------------------------------------------------------------

print("\n🏁 Conversion completed!")
print(f"✅ Files converted: {converted_count}")
print(f"⏭️ Skipped (JPG already exists): {skipped_count}")

if converted_count > 0:
    original_total_mb = bytes_to_mb(total_original_size_converted)
    converted_total_mb = bytes_to_mb(total_converted_size)
    print(f"\n📊 Statistics for converted files:")
    print(f"   Total size of source WebP: {original_total_mb:.2f} MB")
    print(f"   Total size of resulting JPG: {converted_total_mb:.2f} MB")
    print(f"   Change: {original_total_mb:.2f} MB -> {converted_total_mb:.2f} MB")
    if original_total_mb > 0:
        ratio = (converted_total_mb / original_total_mb) * 100
        print(f"   JPG size is {ratio:.1f}% of original WebP size")
else:
    print("📊 No new files were converted.")

# ------------------------------------------------------------
# Pause before exit (so the CMD window doesn't close immediately)
# ------------------------------------------------------------
input("\n👋 Press Enter to exit...")