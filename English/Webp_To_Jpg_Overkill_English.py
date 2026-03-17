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
        # If colorama is not installed and we are not in IDLE, suggest installation
        print("For colored output install colorama: pip install colorama")

# ------------------------------------------------------------
# Settings: paths and conversion parameters (you can change these)
# ------------------------------------------------------------

# ⚠️ When copying a Windows path, use a raw string - r"...",
# where ... is your folder path copied from Windows. This prevents Python
# from interpreting \U or any other character after a backslash as an escape sequence.
# (Otherwise an error will definitely occur!)

input_path = r""               # folder with source WebP files (empty = current folder)
output_path = r""              # folder for JPG results (empty = creates subfolder, see below)
jpg_quality = 85               # JPEG quality (1-100, default 85)


# ------------------------------------------------------------
# OVERKILL mode (recursive processing of all subfolders)
# ------------------------------------------------------------

# ⚠️⚠️⚠️ OVERKILL MODE: if enabled, the program will find ALL .webp files in ALL SUBFOLDERS of input_path.
# Please double-check your folders before enabling this! The developer once rushed and ruined important files. It was a disaster.
# Use the exclude_folders list to skip certain subfolders (see examples).

overkill_mode = False           # False = only files directly in input_path; True = search all subfolders!

# List of folder names (or relative paths) to EXCLUDE from scanning when overkill_mode = True.
# You can specify simple folder names (e.g., "backup", "old") or subpaths like "archive/2020".
# All paths are interpreted relative to input_path. Examples:
#   exclude_folders = ["temp", "private"]                    # skips any folders named "temp" or "private"
#   exclude_folders = ["temp folder", "private data", "Do not enter", "Absolutely do not enter"]  # names with spaces (English/Russian examples)
#   exclude_folders = ["docs/old"]                           # skips the specific subfolder "docs/old"
# When using Windows paths with backslashes, use raw strings or double backslashes:
#   exclude_folders = ["docs/old", r"temp\backup", "archive\\2024"]  # all these variants will work

exclude_folders = []            # empty list = no exclusions

# ⚠️⚠️⚠️ DANGEROUS OPTION: Delete original WebP files after successful conversion?
# It is strongly recommended to keep this False and later delete files manually via Windows search (*.webp).
# The developer learned this the hard way.
# The deletion method (recycle bin or permanent) is set by the deletion_method variable below.
delete_original = False

# ⚠️⚠️⚠️ Delete original WebP if the file was skipped due to name conflict?
# Default is False, because it's easy to rush and delete needed files.
# Enable this option only if you are absolutely sure about your storage understanding. The developer burned himself on this.
delete_on_skip = False


# ------------------------------------------------------------
# Deletion settings (permanent or recycle bin)
# ------------------------------------------------------------
# File deletion method:
#   "recycle"   - send to recycle bin (requires send2trash library, otherwise permanent deletion)
#   "permanent" - delete permanently
deletion_method = "recycle"     # default recycle bin

# Action when recycle bin error occurs (if recycle is used):
#   "ask"        - ask the user (default)
#   "permanent"  - delete permanently
#   "skip"       - skip the file (do not delete, do not convert?)
#   "stop"       - stop the program
on_recycle_error = "ask"

# ------------------------------------------------------------
# Save JPG in the same folder where the WebP was found?
#   True  -> JPG will be placed next to the source WebP.
#   False -> All JPGs will be saved into a single folder (output_path, or default overkill_converted folder).
save_in_place = False

# ------------------------------------------------------------
# Behavior on name conflict (when a JPG with the same name already exists)
# ------------------------------------------------------------
# Possible values:
#   "rename" - automatically rename by adding (2), (3) etc.
#   "skip"   - skip conversion of this file
#   "ask"    - ask the user what to do (default)
on_name_conflict = "ask"

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
    """Deletes a file according to deletion_method and on_recycle_error settings."""
    global deletion_method  # may change if user chooses permanent deletion on error
    
    if deletion_method == "permanent":
        try:
            os.remove(file_path)
            return True, None
        except Exception as e:
            return False, str(e)
    
    # Otherwise deletion_method == "recycle" and RECYCLE_BIN_AVAILABLE must be True
    try:
        send2trash(file_path)
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Handle error according to on_recycle_error
        if on_recycle_error == "permanent":
            # Try permanent deletion
            try:
                os.remove(file_path)
                print(f"{Fore.YELLOW}⚠️ Could not send to recycle bin, permanently deleted.{Style.RESET_ALL}")
                return True, None
            except Exception as e2:
                return False, f"Permanent deletion error: {e2}"
        elif on_recycle_error == "skip":
            # Skip file (do not delete)
            return False, f"Recycle bin error, file skipped: {error_msg}"
        elif on_recycle_error == "stop":
            # Stop program
            print(f"{Fore.RED}❌ Error sending to recycle bin: {error_msg}{Style.RESET_ALL}")
            print(f"{Fore.RED}Program stopped due to on_recycle_error = 'stop'.{Style.RESET_ALL}")
            sys.exit(1)
        else:  # "ask" or any other default value
            while True:
                print(f"\n{Fore.RED}❌ Error sending file to recycle bin: {error_msg}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}File: {file_path}{Style.RESET_ALL}")
                print("Choose action:")
                print("   1 - Try again (send to recycle bin once more)")
                print("   2 - Skip this file (do not delete, continue)")
                print("   3 - Delete permanently (for this file)")
                print("   4 - Use permanent deletion for all remaining files")
                print("   5 - Stop program")
                choice = input("Enter 1, 2, 3, 4 or 5: ").strip()
                if choice == '1':
                    try:
                        send2trash(file_path)
                        return True, None
                    except Exception as e2:
                        error_msg = str(e2)
                        continue  # show menu again
                elif choice == '2':
                    return False, f"Skipped by user: {error_msg}"
                elif choice == '3':
                    try:
                        os.remove(file_path)
                        return True, None
                    except Exception as e2:
                        return False, f"Permanent deletion error: {e2}"
                elif choice == '4':
                    # Switch to permanent for the whole session
                    deletion_method = "permanent"
                    try:
                        os.remove(file_path)
                        return True, None
                    except Exception as e2:
                        return False, f"Permanent deletion error: {e2}"
                elif choice == '5':
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}Invalid input. Please enter 1-5.{Style.RESET_ALL}")

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
# Helper function: get all WebP files (recursive with exclusions)
# ------------------------------------------------------------
def get_webp_files(root_path, recursive=False, exclude_list=None):
    if exclude_list is None:
        exclude_list = []
    # Normalize all exclude_list items: replace backslashes with forward slashes for uniformity
    exclude_norm = [e.replace('\\', '/') for e in exclude_list]
    webp_files = []
    if recursive:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Relative path of current folder
            rel_dir = os.path.relpath(dirpath, root_path)
            if rel_dir == '.':
                rel_dir = ''
            # Convert to uniform forward slashes
            rel_dir_norm = rel_dir.replace('\\', '/')
            # Remove excluded folders from dirnames (so os.walk does not go into them)
            to_remove = []
            for d in dirnames:
                # Full relative path to subfolder
                full_rel = os.path.join(rel_dir_norm, d).replace('\\', '/')
                # Check if this folder (by name or full path) is in the exclusion list
                if d in exclude_norm or full_rel in exclude_norm:
                    to_remove.append(d)
            for d in to_remove:
                dirnames.remove(d)
            # Now collect .webp files
            for f in filenames:
                if f.lower().endswith('.webp'):
                    webp_files.append(os.path.join(dirpath, f))
    else:
        # Non-recursive: only files directly in root_path
        for f in os.listdir(root_path):
            if f.lower().endswith('.webp'):
                webp_files.append(os.path.join(root_path, f))
    return webp_files

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
            # Check if name starts with base_name
            name_without_ext = os.path.splitext(f)[0]
            if name_without_ext == base_name:
                # exact match
                full = os.path.join(directory, f)
                size = os.path.getsize(full)
                existing.append({'name': f, 'size': size, 'number': 0})
            elif name_without_ext.startswith(base_name + " ("):
                # check that after parenthesis there is a number and closing parenthesis
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
# Helper function: show conflict information
# ------------------------------------------------------------
def show_conflict_info(base_name, existing_list, new_file_size, dest_dir):
    print(f"\n{Fore.YELLOW}⚠️ Name conflict for file {base_name}.jpg{Style.RESET_ALL}")
    print(f"   Target folder: {dest_dir}")
    print(f"   New file size: {format_size(new_file_size)}")
    print(f"   Existing files in this folder with similar names:")
    for item in sorted(existing_list, key=lambda x: x['number']):
        print(f"     - {item['name']} ({format_size(item['size'])})")
    print()

# ------------------------------------------------------------
# Function to display folder tree nicely
# ------------------------------------------------------------
def print_folder_tree(folder_paths, root_display_name):
    """Prints a folder tree based on a list of relative paths."""
    if not folder_paths:
        return
    # Build nested dictionary
    tree = {}
    for path in folder_paths:
        if path == '':
            continue  # root is handled separately
        parts = path.split(os.sep)
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    # Recursive printing
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

    # Print root
    print(f"{Fore.CYAN}📁 {root_display_name}/{Style.RESET_ALL}")
    print_node(tree)

# ------------------------------------------------------------
# Preparation
# ------------------------------------------------------------
if input_path == "":
    input_path = os.getcwd()

print(f"{Fore.BLUE}🔍 Source folder:{Style.RESET_ALL} {input_path}")
print()  # blank line after source folder

# Gather WebP files according to mode
if overkill_mode:
    print(f"{Fore.MAGENTA}⚡ OVERKILL MODE ENABLED: scanning all subfolders (with exclusions)...{Style.RESET_ALL}")
    webp_files = get_webp_files(input_path, recursive=True, exclude_list=exclude_folders)
else:
    webp_files = get_webp_files(input_path, recursive=False)

print()  # blank line after mode message
total_files = len(webp_files)

if total_files == 0:
    print(f"{Fore.RED}❌ No WebP files found. Program finished.{Style.RESET_ALL}")
    input("\nPress Enter to exit...")
    exit()

print(f"{Fore.BLUE}📊 WebP files found:{Style.RESET_ALL} {total_files}")

# Calculate total size of all found WebP files
total_all_webp_size = 0
for f in webp_files:
    total_all_webp_size += os.path.getsize(f)

print(f"{Fore.BLUE}💾 Total size of source WebP files:{Style.RESET_ALL} {format_size(total_all_webp_size)}")

# Determine output folder
if save_in_place:
    output_dir = None   # will be determined per file later
    print(f"{Fore.CYAN}📁 Save mode:{Style.RESET_ALL} JPGs will be placed next to source WebP files.")
else:
    if output_path == "":
        if overkill_mode:
            output_dir = os.path.join(input_path, "overkill_converted")
        else:
            output_dir = os.path.join(input_path, "converted")
    else:
        output_dir = output_path
    os.makedirs(output_dir, exist_ok=True)
    print(f"{Fore.CYAN}📁 All JPGs will be saved in:{Style.RESET_ALL} {output_dir}")

# If overkill mode is on, show folder tree and ask for confirmation
if overkill_mode:
    # Get unique folders containing WebP files
    folders_with_webp = set(os.path.dirname(f) for f in webp_files)
    # Convert to relative paths for display
    rel_folders = [os.path.relpath(f, input_path) if os.path.relpath(f, input_path) != '.' else '' for f in folders_with_webp]
    # Show tree
    print(f"\n{Fore.YELLOW}📁 Folders containing WebP (will be processed):{Style.RESET_ALL}")
    print_folder_tree(rel_folders, os.path.basename(input_path) or input_path)
    # Additional warnings
    if exclude_folders:
        print(f"\n{Fore.YELLOW}⏭️ The following folders were excluded (will NOT be processed):{Style.RESET_ALL}")
        for ex in exclude_folders:
            # Use bright cyan (visible on black background)
            print(f"   {Fore.CYAN}{Style.BRIGHT}❌ {ex}{Style.RESET_ALL}")
    # Important developer recommendation
    print(f"\n{Fore.YELLOW}🔬 DEVELOPER'S RECOMMENDATION:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   The developer thoroughly tested all possible configuration combinations and found no issues,{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   but something might still have been overlooked. The chance is extremely small, but not zero.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   It is HIGHLY RECOMMENDED to work on a DUPLICATE/COPY of your storage.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   After verifying that everything is correct, simply replace the original with the modified copy{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   (delete the original and paste the new folder).{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}⚠️  You are about to process ALL folders shown above. If in doubt, close the program now – nothing has been changed yet.{Style.RESET_ALL}")
    if delete_original:
        print()
        print(f"{Fore.RED}❗❗❗ WARNING: DELETE ORIGINAL FILES ENABLED! WebP files WILL BE DELETED after conversion.{Style.RESET_ALL}")
    if delete_on_skip:
        print(f"{Fore.RED}❗❗❗ WARNING: DELETE ON SKIP ENABLED! WebP files will be deleted if conversion is skipped due to name conflict.{Style.RESET_ALL}")
    print()
    # Recommendation to run in command prompt, not IDLE
    if is_running_in_idle():
        print(f"{Fore.YELLOW}💡 It is recommended to run the program by double-clicking (in command prompt),{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   so that colored output displays correctly.{Style.RESET_ALL}")
        print()
    input(f"{Fore.CYAN}Press Enter to continue or close the window to cancel...{Style.RESET_ALL}")

# ------------------------------------------------------------
# Conversion
# ------------------------------------------------------------
print(f"\n{Fore.GREEN}🚀 Conversion started.{Style.RESET_ALL}")
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
    
    # Get size of source file (needed for conflict info)
    try:
        original_size = os.path.getsize(src_path)
    except:
        original_size = 0

    # Check if there are existing JPGs with the same base name (or variations)
    existing_jpgs = get_existing_jpgs(dest_dir, base_name)
    
    # We'll store the final destination path
    dst_path = None
    action_performed = False  # flag indicating file was handled (converted or skipped)
    
    if existing_jpgs:
        # Add a blank line for visual separation between conflicts of different files
        print()
        # Conflict: one or more files with the same base name exist
        if on_name_conflict == "skip":
            skipped_count += 1
            action_performed = True
            # If delete_on_skip is enabled
            if delete_on_skip:
                success, error = delete_file(src_path)
                if success:
                    deleted_count += 1
                    # Use CYAN for informational deletion messages
                    print(f"{Fore.CYAN}🗑️ Source file {filename} deleted/sent to recycle bin (skip due to conflict){Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Could not delete {filename}: {error}{Style.RESET_ALL}")
            else:
                # Optionally output skip info
                # print(f"{Fore.YELLOW}⏭️ Skipped {filename} (JPG already exists){Style.RESET_ALL}")
                pass
        elif on_name_conflict == "rename":
            # Show conflict info
            show_conflict_info(base_name, existing_jpgs, original_size, dest_dir)
            next_num = get_next_number(existing_jpgs)
            new_filename = f"{base_name} ({next_num}).jpg"
            dst_path = os.path.join(dest_dir, new_filename)
            print(f"{Fore.CYAN}   Will create file: {new_filename}{Style.RESET_ALL}")
            action_performed = False  # proceed to conversion
        elif on_name_conflict == "ask":
            show_conflict_info(base_name, existing_jpgs, original_size, dest_dir)
            # Ask user
            while True:
                print(f"{Fore.YELLOW}Choose action:{Style.RESET_ALL}")
                print("   1 - Rename and save (create file with number)")
                print("   2 - Skip this file")
                print("   3 - Abort entire process (exit)")
                choice = input("Enter 1, 2 or 3: ").strip()
                if choice == '1':
                    next_num = get_next_number(existing_jpgs)
                    new_filename = f"{base_name} ({next_num}).jpg"
                    dst_path = os.path.join(dest_dir, new_filename)
                    print(f"{Fore.CYAN}   Will create file: {new_filename}{Style.RESET_ALL}")
                    action_performed = False
                    break
                elif choice == '2':
                    skipped_count += 1
                    action_performed = True
                    # If delete_on_skip is enabled
                    if delete_on_skip:
                        success, error = delete_file(src_path)
                        if success:
                            deleted_count += 1
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
            # Unknown value - treat as rename
            show_conflict_info(base_name, existing_jpgs, original_size, dest_dir)
            next_num = get_next_number(existing_jpgs)
            new_filename = f"{base_name} ({next_num}).jpg"
            dst_path = os.path.join(dest_dir, new_filename)
            print(f"{Fore.CYAN}   Will create file: {new_filename}{Style.RESET_ALL}")
            action_performed = False
    else:
        # No conflict
        dst_path = os.path.join(dest_dir, base_name + ".jpg")
        action_performed = False
    
    # If file was not skipped, convert it
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
                    # Use CYAN for informational deletion messages
                    print(f"{Fore.CYAN}🗑️ Source file {filename} deleted/sent to recycle bin after conversion{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Could not delete {filename}: {error}{Style.RESET_ALL}")
            
            # Optionally uncomment for detailed per-file output:
            # print(f"✅ Converted {filename} -> {os.path.basename(dst_path)} ({format_size(original_size)} -> {format_size(converted_size)})")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error processing {src_path}: {e}{Style.RESET_ALL}")
    
    # If there was a conflict, add an extra blank line for better separation between files
    if existing_jpgs:
        print()
    
    # Progress output
    if idx % 10 == 0 or idx == total_files:
        print(f"{Fore.BLUE}📈 Progress: {idx}/{total_files} processed{Style.RESET_ALL}")

# ------------------------------------------------------------
# Final statistics
# ------------------------------------------------------------
# Add two blank lines before final heading for better readability
print("\n\n")
print(f"{Fore.GREEN}🏁 Conversion completed!{Style.RESET_ALL}")
print(f"{Fore.GREEN}✅ Files converted:{Style.RESET_ALL} {converted_count}")
print(f"{Fore.YELLOW}⏭️ Skipped (name conflict):{Style.RESET_ALL} {skipped_count}")
if delete_original or delete_on_skip:
    # Use CYAN for final deletion stats
    print(f"{Fore.CYAN}🗑️ Source files deleted/sent to recycle bin:{Style.RESET_ALL} {deleted_count}")

if converted_count > 0:
    original_total = total_original_size_converted
    converted_total = total_converted_size
    print(f"\n{Fore.CYAN}📊 Statistics for converted files:{Style.RESET_ALL}")
    print(f"   Total size of source WebP: {Fore.YELLOW}{format_size(original_total)}{Style.RESET_ALL}")
    print(f"   Total size of resulting JPG: {Fore.YELLOW}{format_size(converted_total)}{Style.RESET_ALL}")
    print(f"   Change: {Fore.YELLOW}{format_size(original_total)}{Style.RESET_ALL} -> {Fore.YELLOW}{format_size(converted_total)}{Style.RESET_ALL}")
    if original_total > 0:
        ratio = (converted_total / original_total) * 100
        print(f"   JPG size is {Fore.YELLOW}{ratio:.1f}%{Style.RESET_ALL} of original WebP size")
else:
    print("📊 No new files were converted.")

# ------------------------------------------------------------
# Pause before exit
# ------------------------------------------------------------
input(f"\n{Fore.CYAN}👋 Press Enter to exit...{Style.RESET_ALL}")