import os
import sys
from PIL import Image

# ------------------------------------------------------------
# Runtime environment detection (IDLE does not support colors)
# ------------------------------------------------------------
def is_running_in_idle():
    """Checks if the script is running in IDLE (where ANSI colors don't work)."""
    return 'idlelib' in sys.modules or 'idlelib.run' in sys.modules

# For colored output in terminal (Windows CMD supported)
try:
    from colorama import init, Fore, Style
    init()  # initialization for Windows
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# If we are in IDLE, disable colors (even if colorama is installed)
if is_running_in_idle():
    COLORAMA_AVAILABLE = False

if not COLORAMA_AVAILABLE:
    # Dummy color classes (empty strings)
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
        # If colorama not installed and we're not in IDLE, suggest installation
        print("For colored output install colorama: pip install colorama")

# ------------------------------------------------------------
# Settings: paths and conversion parameters (you can change these)
# ------------------------------------------------------------

# ⚠️⚠️⚠️ When copying a Windows path, use a raw string - r"...",
# where ... is your folder path copied from Windows. This prevents Python
# from interpreting \U or any other character after a backslash as an escape sequence.
# (It will definitely happen otherwise!)

input_path = r""               # folder with source WebP files (empty = current folder)
output_path = r""              # folder for JPGs (empty = creates "converted" subfolder in the working folder (input_path))
jpg_quality = 85               # JPEG quality (1-100, default 85)

# ⚠️⚠️⚠️ DANGEROUS OPTION: Delete original WebP files after successful conversion?
# It is strongly recommended to keep False and later delete files manually via file search (e.g., in Windows: [*.webp]).
# The developer learned this the hard way.
delete_original = False

# ⚠️⚠️⚠️ Delete original WebP if the file was skipped due to name conflict?
# Works only if delete_original = True.
# Default is False for safety. But logically, if delete_original = True, you might want to set this True,
# because the converted file already exists and you consider it correct. Hence the original is no longer needed.
delete_on_skip = False

# ⚠️⚠️⚠️ Delete original WebP if renaming was chosen during a name conflict?
# Works only if delete_original = True.
# Default is False for safety. But logically, if delete_original = True, you might want to set this True,
# because the new file is still created, just renamed. So the original is no longer needed.
delete_on_rename = False

# ------------------------------------------------------------
# Deletion settings (permanent or recycle bin)
# ------------------------------------------------------------
# File deletion method:
#   "recycle"   - send to recycle bin (requires send2trash library, otherwise permanent deletion)
#   "permanent" - delete permanently
deletion_method = "recycle"     # default recycle bin

# ------------------------------------------------------------
# Behavior on name conflict (when a JPG with the same name already exists)
# ------------------------------------------------------------
# Possible values:
#   "skip"   - skip conversion of this file
#   "rename" - automatically rename by adding (2), (3) etc.
#   "ask"    - ask the user what to do (default)
on_name_conflict = "ask"

# ------------------------------------------------------------
# Validate settings correctness
# ------------------------------------------------------------
def validate_settings():
    errors = []
    
    # Check delete_original
    if not isinstance(delete_original, bool):
        errors.append(f"delete_original must be True or False, got: {delete_original} (type {type(delete_original).__name__})")
    
    # Check delete_on_skip
    if not isinstance(delete_on_skip, bool):
        errors.append(f"delete_on_skip must be True or False, got: {delete_on_skip} (type {type(delete_on_skip).__name__})")
    
    # Check delete_on_rename
    if not isinstance(delete_on_rename, bool):
        errors.append(f"delete_on_rename must be True or False, got: {delete_on_rename} (type {type(delete_on_rename).__name__})")
    
    # Check jpg_quality (must be integer from 1 to 100)
    if not isinstance(jpg_quality, int):
        errors.append(f"jpg_quality must be an integer, got: {jpg_quality} (type {type(jpg_quality).__name__})")
    elif not (1 <= jpg_quality <= 100):
        errors.append(f"jpg_quality must be in range 1-100, got: {jpg_quality}")
    
    # Check deletion_method
    valid_deletion = ["recycle", "permanent"]
    if deletion_method not in valid_deletion:
        errors.append(f"deletion_method must be one of {valid_deletion}, got: {deletion_method}")
    
    # Check on_name_conflict
    valid_conflict = ["skip", "rename", "ask"]
    if on_name_conflict not in valid_conflict:
        errors.append(f"on_name_conflict must be one of {valid_conflict}, got: {on_name_conflict}")
    
    return errors

# Perform validation
validation_errors = validate_settings()
if validation_errors:
    print(f"{Fore.RED}❌ Errors found in settings:{Style.RESET_ALL}")
    for err in validation_errors:
        print(f"   {Fore.RED}• {err}{Style.RESET_ALL}")
    print()
    input(f"{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}")
    sys.exit(1)

# ------------------------------------------------------------
# Check for send2trash library for recycle bin
# ------------------------------------------------------------
RECYCLE_BIN_AVAILABLE = False
if deletion_method == "recycle":
    try:
        from send2trash import send2trash
        RECYCLE_BIN_AVAILABLE = True
    except ImportError:
        print(f"{Fore.YELLOW}⚠️ send2trash library is not installed. Files will be deleted permanently.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   To use recycle bin install: pip install send2trash{Style.RESET_ALL}")
        print()
        input(f"{Fore.CYAN}Press Enter to continue with permanent deletion, or close the window to cancel...{Style.RESET_ALL}")
        deletion_method = "permanent"  # automatically switch to permanent

# ------------------------------------------------------------
# Helper function: delete file according to settings
# ------------------------------------------------------------
def delete_file(file_path):
    """Deletes a file according to deletion_method setting."""
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
# Helper function: format bytes to human readable
# ------------------------------------------------------------
def format_size(bytes_count):
    """Converts bytes to string with automatic unit selection (B, KB, MB, GB, TB)."""
    if bytes_count < 1024:
        return f"{bytes_count} B"
    elif bytes_count < 1024**2:
        return f"{bytes_count/1024:.2f} KB"
    elif bytes_count < 1024**3:
        return f"{bytes_count/1024**2:.2f} MB"
    elif bytes_count < 1024**4:
        return f"{bytes_count/1024**3:.2f} GB"
    else:
        return f"{bytes_count/1024**4:.2f} TB"

# ------------------------------------------------------------
# Helper function: get list of existing JPGs with the same base name
# ------------------------------------------------------------
def get_existing_jpgs(directory, base_name):
    """Returns a list of dicts with info about existing JPG files
       starting with base_name (possibly with (n) suffix)."""
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
                rest = name_without_ext[len(base_name)+2:]  # skip " ("
                if rest.endswith(')') and rest[:-1].isdigit():
                    num = int(rest[:-1])
                    full = os.path.join(directory, f)
                    size = os.path.getsize(full)
                    existing.append({'name': f, 'size': size, 'number': num})
    return existing

# ------------------------------------------------------------
# Helper function: determine next number for renaming
# ------------------------------------------------------------
def get_next_number(existing_list):
    """Finds the maximum number among existing files and returns the next one."""
    max_num = 0
    for item in existing_list:
        if item['number'] > max_num:
            max_num = item['number']
    return max_num + 1

# ------------------------------------------------------------
# Helper function: show conflict information (improved readability)
# ------------------------------------------------------------
def show_conflict_info(base_name, existing_list, new_file_size, dest_dir):
    print(f"\n{Fore.YELLOW}⚠️ Name conflict for file {Fore.CYAN}{Style.BRIGHT}{base_name}.jpg{Style.RESET_ALL}")
    print(f"   Target folder: {dest_dir}")
    print()
    # Alignment: "New file:" (9 chars) + 5 spaces = 14 chars,
    # "Existing:" (9 chars) + 5 spaces = 14 chars.
    # File names start at the same position.
    print(f"   {Fore.CYAN}New file:     {Style.RESET_ALL}{Fore.CYAN}{Style.BRIGHT}{base_name}.jpg{Style.RESET_ALL} (source WebP: {format_size(new_file_size)})")
    for item in sorted(existing_list, key=lambda x: x['number']):
        print(f"   {Fore.CYAN}Existing:     {Style.RESET_ALL}{Fore.CYAN}{item['name']}{Style.RESET_ALL} ({format_size(item['size'])})")
    print()

# ------------------------------------------------------------
# Preparation
# ------------------------------------------------------------
# If input_path is not empty, check if it exists
if input_path != "" and not os.path.exists(input_path):
    print(f"{Fore.RED}❌ Specified folder does not exist: {input_path}{Style.RESET_ALL}")
    input("\nPress Enter to exit...")
    sys.exit(1)

if input_path == "":
    input_path = os.getcwd()

print(f"{Fore.BLUE}🔍 Source folder:{Style.RESET_ALL} {input_path}")
print()  # blank line

webp_files = []
for f in os.listdir(input_path):
    if f.lower().endswith('.webp'):
        webp_files.append(f)
        # print(f"📄 File {f} added to processing list.")

total_files = len(webp_files)

if total_files == 0:
    print(f"{Fore.RED}❌ No WebP files found. Program finished.{Style.RESET_ALL}")
    input("\nPress Enter to exit...")
    sys.exit()

print(f"{Fore.BLUE}📊 WebP files found:{Style.RESET_ALL} {total_files}")

total_all_webp_size = 0
for f in webp_files:
    file_path = os.path.join(input_path, f)
    total_all_webp_size += os.path.getsize(file_path)

print(f"{Fore.BLUE}💾 Total size of source WebP files:{Style.RESET_ALL} {format_size(total_all_webp_size)}")

if output_path == "":
    output_dir = os.path.join(input_path, "converted")
else:
    output_dir = output_path

os.makedirs(output_dir, exist_ok=True)
print(f"{Fore.CYAN}📁 Results will be saved in:{Style.RESET_ALL} {output_dir}")

# ------------------------------------------------------------
# Conversion
# ------------------------------------------------------------
print(f"\n{Fore.GREEN}🚀 Conversion started.{Style.RESET_ALL}")
converted_count = 0
skipped_count = 0
total_original_size_converted = 0
total_converted_size = 0

for idx, filename in enumerate(webp_files, start=1):
    src_path = os.path.join(input_path, filename)
    base_name = os.path.splitext(filename)[0]
    original_size = os.path.getsize(src_path)

    # Check existing JPGs in target folder
    existing_jpgs = get_existing_jpgs(output_dir, base_name)
    dst_path = None
    action_performed = False  # flag that file is already handled (skipped or renamed)
    was_conflict = bool(existing_jpgs)  # remember if there was a conflict
    was_renamed = False       # flag that renaming was chosen

    if existing_jpgs:
        # Name conflict
        print()  # blank line for readability
        if on_name_conflict == "skip":
            skipped_count += 1
            action_performed = True
            if delete_original and delete_on_skip:
                success, error = delete_file(src_path)
                if success:
                    print(f"{Fore.CYAN}🗑️ Source file {filename} deleted/sent to recycle bin (skip due to conflict){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Could not delete {filename}: {error}{Style.RESET_ALL}")
        elif on_name_conflict == "rename":
            show_conflict_info(base_name, existing_jpgs, original_size, output_dir)
            next_num = get_next_number(existing_jpgs)
            new_filename = f"{base_name} ({next_num}).jpg"
            dst_path = os.path.join(output_dir, new_filename)
            print(f"{Fore.CYAN}   Will create file: {new_filename}{Style.RESET_ALL}")
            action_performed = False  # will convert with new name
            was_renamed = True
        elif on_name_conflict == "ask":
            show_conflict_info(base_name, existing_jpgs, original_size, output_dir)
            while True:
                print(f"{Fore.YELLOW}Choose action:{Style.RESET_ALL}")
                print("   1 - Rename and save (create file with number)")
                print("   2 - Skip this file")
                print("   3 - Abort entire process (exit)")
                choice = input("Enter 1, 2 or 3: ").strip()
                if choice == '1':
                    next_num = get_next_number(existing_jpgs)
                    new_filename = f"{base_name} ({next_num}).jpg"
                    dst_path = os.path.join(output_dir, new_filename)
                    print(f"{Fore.CYAN}   Will create file: {new_filename}{Style.RESET_ALL}")
                    action_performed = False
                    was_renamed = True
                    break
                elif choice == '2':
                    skipped_count += 1
                    action_performed = True
                    if delete_original and delete_on_skip:
                        success, error = delete_file(src_path)
                        if success:
                            print(f"{Fore.CYAN}🗑️ Source file {filename} deleted/sent to recycle bin (skip by request){Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}❌ Could not delete {filename}: {error}{Style.RESET_ALL}")
                    break
                elif choice == '3':
                    print(f"{Fore.RED}Aborted by user.{Style.RESET_ALL}")
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}Invalid input. Please enter 1, 2 or 3.{Style.RESET_ALL}")
        else:
            # Unknown value – skip by default
            skipped_count += 1
            action_performed = True
            if delete_original and delete_on_skip:
                success, error = delete_file(src_path)
                if success:
                    print(f"{Fore.CYAN}🗑️ Source file {filename} deleted/sent to recycle bin (skip by default){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Could not delete {filename}: {error}{Style.RESET_ALL}")
    else:
        # No conflict
        dst_path = os.path.join(output_dir, base_name + ".jpg")
        action_performed = False

    # If file not skipped and destination path is set, convert it
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

            # Decision whether to delete source file
            should_delete = False
            if delete_original:
                if was_conflict and was_renamed:
                    # On conflict and renaming, respect delete_on_rename
                    should_delete = delete_on_rename
                else:
                    # No conflict – just delete_original
                    should_delete = True

            if should_delete:
                success, error = delete_file(src_path)
                if success:
                    print(f"{Fore.CYAN}🗑️ Source file {filename} deleted/sent to recycle bin{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Could not delete {filename}: {error}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Error processing {filename}: {e}{Style.RESET_ALL}")

    # If there was a conflict, add an extra blank line
    if existing_jpgs:
        print()

    # Progress output
    if idx % 10 == 0 or idx == total_files:
        print(f"{Fore.BLUE}📈 Progress: {idx}/{total_files} processed{Style.RESET_ALL}")

# ------------------------------------------------------------
# Final statistics
# ------------------------------------------------------------
print("\n\n")
print(f"{Fore.GREEN}🏁 Conversion completed!{Style.RESET_ALL}")
print(f"{Fore.GREEN}✅ Files converted:{Style.RESET_ALL} {converted_count}")
print(f"{Fore.YELLOW}⏭️ Skipped (name conflict):{Style.RESET_ALL} {skipped_count}")

if converted_count > 0:
    print(f"\n{Fore.CYAN}📊 Statistics for converted files:{Style.RESET_ALL}")
    print(f"   Total size of source WebP: {Fore.YELLOW}{format_size(total_original_size_converted)}{Style.RESET_ALL}")
    print(f"   Total size of resulting JPG: {Fore.YELLOW}{format_size(total_converted_size)}{Style.RESET_ALL}")
    print(f"   Change: {Fore.YELLOW}{format_size(total_original_size_converted)}{Style.RESET_ALL} -> {Fore.YELLOW}{format_size(total_converted_size)}{Style.RESET_ALL}")
    if total_original_size_converted > 0:
        ratio = (total_converted_size / total_original_size_converted) * 100
        print(f"   JPG size is {Fore.YELLOW}{ratio:.1f}%{Style.RESET_ALL} of original WebP size")
else:
    print("📊 No new files were converted.")

# ------------------------------------------------------------
# Pause before exit
# ------------------------------------------------------------
input(f"\n{Fore.CYAN}👋 Press Enter to exit...{Style.RESET_ALL}")