import io
import os
import re
import shutil
import zipfile
import argparse
import configparser


parser = argparse.ArgumentParser(
    description='Распаковщик установочных файлов, собранных Actual Installer',
    epilog='Автор: Мейсак Илья Николаевич, 2025.11.09')

parser.add_argument('installer', help='путь к файлу инсталлятора')
parser.add_argument('-ziponly', action='store_true',
                    help='сохранить только не распакованные ZIP-архивы')
args = parser.parse_args()

exe_name = args.installer
dir_name = os.path.splitext(exe_name)[0]
shutil.rmtree(dir_name, ignore_errors=True)
os.makedirs(dir_name, exist_ok=True)

with open(exe_name, 'rb') as f:
    file = f.read()

# поиск ZIP-архивов и их распаковка
file_pointer = 0
n = 0
while True:
    start_zip = file.find(b'\x50\x4B\x03\x04', file_pointer)
    if start_zip == -1:
        break
    end_zip = file.find(b'\x50\x4B\x05\x06', start_zip)
    if end_zip == -1:
        break
    end_zip += 22 + int.from_bytes(file[end_zip + 20:end_zip + 22], 'little')
    zip_bytes = file[start_zip:end_zip]
    file_pointer = end_zip

    if not args.ziponly:
        # распаковать архивы из памяти не сохраняя на диск
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(dir_name)
    else:
        # сохранить нераспакованные архивы на диск
        n += 1
        zip_name = f'{dir_name}/{n}.zip'
        with open(zip_name, 'wb') as f:
            f.write(zip_bytes)


if not args.ziponly:
    # открыть файл конфигурации сборки
    config = configparser.ConfigParser()
    with open(f'{dir_name}/aisetup.ini', encoding='utf-8-sig') as f:
        config.read_file(f)

    # переименовать распакованные файлы
    for key, val in zip(config['Files'].keys(), config['Files'].values()):
        old = os.path.join(dir_name, key)
        new = os.path.join(dir_name, re.findall(
            r'^<InstallDir>\\(.*)\?11$', val)[0].replace('\\', '/'))
        os.renames(old, new)
