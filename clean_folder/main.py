import sys
import pathlib
import shutil


def normalize(filename):
    translit_mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z', 'и': 'y',
        'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ь': '', 'ю': 'iu', 'я': 'ia',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Д': 'D', 'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y',
        'І': 'I', 'Ї': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
        'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ь': '', 'Ю': 'Yu', 'Я': 'Ya',
    }

    normalized = ''.join(translit_mapping.get(char, char) for char in filename if char.isalnum() or char == '.')

    return normalized


def collect_files_and_folders(path, excluded_folders=None):
    if excluded_folders is None:
        excluded_folders = set()

    items = []
    for item in path.iterdir():
        if item.is_dir() and item.name not in excluded_folders:
            sub_items = collect_files_and_folders(item, excluded_folders)
            items.extend(sub_items)
        else:
            items.append(item)

    return items


def check_folder(folder_name, known_extension, unknown_extension, archives_folder):
    if folder_name.is_file():
        print(f"I don't sort files")
    elif folder_name.is_dir():
        if not any(folder_name.iterdir()):
            if folder_name != archives_folder:
                shutil.rmtree(folder_name)
                print(f'Folder: {folder_name} was deleted')
            return  # Додайте цей рядок для виходу, якщо папка порожня
        else:
            for files in folder_name.iterdir():
                if files.is_dir():
                    check_folder(files, known_extension, unknown_extension, archives_folder)
                elif archive_extension := is_archive(files.name, dict_extension):
                    if unpack_archive(files, folder_name):
                        files.unlink()
                    else:
                        unknown_extension.add(archive_extension)



def is_archive(filename, dict_extension):
    extensions = dict_extension['archives']
    if filename.endswith(extensions):
        return filename.split('.')[-1]
    return None


def unpack_archive(archive_path, destination_folder):
    try:
        # Використовуємо shutil для розпакування архівів
        shutil.unpack_archive(archive_path, destination_folder)
        return True
    except shutil.ReadError:
        return False


def sort_files_by_extension(items, dict_extension, known_extension, unknown_extension):
    for item in items:
        if item.is_file() and not item.name.startswith('.DS_Store'):
            normalized_filename = normalize(item.name)
            file_extension = item.suffix[1:].upper()
            sorted = False
            for key, val in dict_extension.items():
                if file_extension in val:
                    known_extension.add(file_extension)
                    new_folder_path = my_object_folder / key
                    new_folder_path.mkdir(exist_ok=True)
                    new_file_path = new_folder_path / normalized_filename
                    try:
                        item.rename(new_file_path)
                        sorted = True
                        break
                    except Exception as e:
                        print(f"Failed to move {item}: {e}")
            if not sorted:
                unknown_extension.add(file_extension)
                unknown_folder_path = my_object_folder / 'unknown'
                if not unknown_folder_path.exists():
                    unknown_folder_path.mkdir(exist_ok=True)
                new_file_path = unknown_folder_path / normalized_filename
                try:
                    item.rename(new_file_path)
                except Exception as e:
                    print(f"Failed to move {item}: {e}")


def remove_empty_folders(folders):
    empty_folders = []
    for item in folders:
        if not item.parent.iterdir():
            empty_folders.append(item.parent)

    for folder in empty_folders:
        folder.rmdir()


def print_result(known_extension, unknown_extension):
    if not known_extension and not unknown_extension:
        print("Ваша папка вже має належний вигляд:)")
    else:
        print(f"Known Extensions: {known_extension}")
        print(f"Unknown Extensions: {unknown_extension}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Приклад запуску: script.py "/home/user/папка яку треба розібрати"')
    else:
        folder_path = sys.argv[1]
        my_object_folder = pathlib.Path(folder_path)

        if my_object_folder.exists():
            dict_extension = {
                "images": ('JPEG', 'PNG', 'JPG', 'SVG'),
                "video": ('AVI', 'MP4', 'MOV', 'MKV'),
                "documents": ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
                "audio": ('MP3', 'OGG', 'WAV', 'AMR'),
                "archives": ('ZIP', 'GZ', 'TAR')
            }

            known_extension = set()
            unknown_extension = set()

            excluded_folders = {"archives", "video", "audio", "documents", "images", 'unknown'}

            check_folder(my_object_folder, known_extension, unknown_extension, my_object_folder / 'archives')
            items_to_sort = collect_files_and_folders(my_object_folder, excluded_folders)
            sort_files_by_extension(items_to_sort, dict_extension, known_extension, unknown_extension)

            check_folder(my_object_folder, known_extension, unknown_extension, my_object_folder / 'archives')
            remove_empty_folders(items_to_sort)

            print_result(known_extension, unknown_extension)
        else:
            print(f'Шлях "{folder_path}" не існує.')