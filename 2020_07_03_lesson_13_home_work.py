# Import necessary modules

import argparse
import time
import os
import requests
from PIL import Image
from threading import Lock
from io import BytesIO
from multiprocessing.pool import ThreadPool

NAME = 'Picture preview'
DESCRIPTION = '''This is a program that are able to make thumbnail of pictures in Internet'''
EPILOG = '(c) Sergey Martynov 2020'
VERSION = '0.0.1'


# Функция чтения файла с адресами
def read_f(f_name):
    try:
        with open(f_name, 'r') as f:
            urls = f.readlines()
    except Exception:
        print('No file with such name')
    return urls


# Проверяем существование выходного каталога. Если есть, то переходим в него, если нет, то создаем и переходим
def dir_out(dir_name):
    if os.path.isdir('./' + dir_name):
        os.chdir('./' + dir_name)
    else:
        os.mkdir('./' + dir_name)
        os.chdir('./' + dir_name)
    return os.getcwd()


def main_code(url):
    global count_files
    global count_bites
    global count_err
    global urls
    global size1
    global size2
    lock.acquire()
    try:
        resp = requests.get(url[:-1])
        img = Image.open(BytesIO(resp.content))
        count_bites += len(resp.content)
        img = img.resize((128, 128), Image.ANTIALIAS)
        img.save(f'{urls.index(url):05}.jpeg')
        print(f'File {url[:-1]} is processed.')
        count_files += 1
    except Exception:
        count_err += 1
    lock.release()


if __name__ == '__main__':
    # Считываем значения аргументов
    p = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION, epilog=EPILOG, add_help=False)
    p.add_argument('file', type=str, help='Name of file with list of urls')
    p.add_argument('--directory', default='thumbnails', type=str, help='Name of directory to storage pictures')
    p.add_argument('--threads', default=4, type=int, help='Number of threads')
    p.add_argument('--size', default='128x128', type=str, help='Size of thumbnail')
    p.add_argument('--help', '-h', action='help', help='Help message')
    p.add_argument('--version', '-v', action='version', help='Version', version='%(prog)s {}'.format(VERSION))
    args = p.parse_args()

    # Определяем размеры thumbnail
    size1 = int(args.size.split(sep='x')[0])
    size2 = int(args.size.split(sep='x')[1])

    # Читаем файл со списком адресов
    urls = read_f(args.file)

    # Запоминаем директорию от куда начали
    start_directory = os.getcwd()

    # Создаем каталог и переходим в него
    target_dir = dir_out(args.directory)

    # Основная обработка.
    # Создаем пул потоков
    pool = ThreadPool(args.threads)
    # Создаем счетчики
    count_files = 0
    count_bites = 0
    count_err = 0
    # Создаем замок
    lock = Lock()
    # Обработка файлов
    start = time.perf_counter()
    pool.map(main_code, urls)
    pool.close()
    pool.join()
    # Переходим в директорию, от куда начали работать.
    os.chdir(start_directory)
    # Печатаем статистику работы
    print(f'Processed {count_files} files.')
    print(f'Downloaded {count_bites} bites.')
    print(f'Got {count_err} errors.')
    print(f'Full time of execution is {time.perf_counter() - start}. sec')
