import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, CHOICE_FOR_OUTPUT_FILE,
                       CHOICE_FOR_OUTPUT_PRETTY, DATETIME_FORMAT, OUTPUT_DIR)


def default_output(results, *args):
    """Вывод в терминал."""
    for row in results:
        print(*row)


def pretty_output(results, *args):
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


OUTPUT_FUNCTIONS = {
    CHOICE_FOR_OUTPUT_PRETTY: pretty_output,
    CHOICE_FOR_OUTPUT_FILE: file_output,
    None: default_output,
}


def control_output(results, cli_args):
    """Обработка аргумента для вывода результата."""
    output_function = OUTPUT_FUNCTIONS.get(cli_args.output)
    output_function(results, cli_args)
