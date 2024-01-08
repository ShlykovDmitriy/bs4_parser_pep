import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR,
                       DATETIME_FORMAT,
                       ARGUMENT_PRETTY,
                       ARGUMENT_FILE,
                       OUTPUT_DIR)


def control_output(results, cli_args):
    """Обработка аргумента для вывода результата."""
    output_functions = {
        ARGUMENT_PRETTY: pretty_output,
        ARGUMENT_FILE: file_output,
    }
    output_function = output_functions.get(cli_args.output, default_output)
    output_function(results, cli_args)


def default_output(results, cli_args):
    """Вывод в терминал."""
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    """Вывод в таблицу."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Вывод файлом."""
    results_dir = BASE_DIR / OUTPUT_DIR
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
