import os
import shutil
import argparse


parser = argparse.ArgumentParser(
    description='Нарезает exe-шники на 7zip-архивы',
    epilog='Автор: Мейсак Илья Николаевич, 2026.03.05')

parser.add_argument('installer', help='путь к файлу инсталлятора')
args = parser.parse_args()

exe_name = args.installer
dir_name = os.path.splitext(exe_name)[0]
shutil.rmtree(dir_name, ignore_errors=True)
os.makedirs(dir_name, exist_ok=True)

with open(exe_name, 'rb') as f:
    file = f.read()

# поиск архивов и их сохранение
file_pointer = 0
n = 0
while True:
    # 37 7A BC AF 27 1C - сигнатура; 00 04 - версия
    start_arch = file.find(b'\x37\x7A\xBC\xAF\x27\x1C\x00\x04', file_pointer)
    if start_arch == -1:
        break
    end_arch = (
        start_arch + 32 +
        int.from_bytes(file[start_arch + 12:start_arch + 20], 'little') +
        int.from_bytes(file[start_arch + 20:start_arch + 28], 'little')
    )
    arch_bytes = file[start_arch:end_arch]
    file_pointer = end_arch

    # сохранить архив на диск
    n += 1
    arch_name = f'{dir_name}/{n}.7z'
    with open(arch_name, 'wb') as f:
        f.write(arch_bytes)
