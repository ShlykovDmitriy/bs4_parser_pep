import argparse
import logging

from logging.handlers import RotatingFileHandler

from constants import (BASE_DIR,
                       LOG_FORMAT,
                       DT_FORMAT,
                       LOG_DIR_NAME,
                       MAXBYTES_LOG_FILE,
                       BACKUPCOUNT_LOG_FILE,
                       LOG_FILE_NAME,
                       ARGUMENT_FILE,
                       ARGUMENT_PRETTY)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(ARGUMENT_PRETTY, ARGUMENT_FILE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    log_dir = BASE_DIR / LOG_DIR_NAME
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / LOG_FILE_NAME
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=MAXBYTES_LOG_FILE, backupCount=BACKUPCOUNT_LOG_FILE
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
