import logging
import re
import requests_cache

from bs4 import BeautifulSoup
from collections import Counter
from outputs import control_output
from urllib.parse import urljoin
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL
from utils import get_response, find_tag


def whats_new(session):
    '''Парсер выдает информацию об обновлениях питона.'''
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            return
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    '''Парсер выдает информацию о версиях и их статусе.'''
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Не найден список c версиями Python')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    '''Парсер скачивает архив питона в zip формате.'''
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)
    if response is None:
        return

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    '''Парсер проверяем все статусы PEP и составляет таблицу с результатами.'''
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    table = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(table, 'tbody')
    tr_tag_list = tbody_tag.find_all('tr')
    statuses_list = []
    for tr_tag in tr_tag_list:
        abbr_tag = find_tag(tr_tag, 'abbr')
        status_in_table = abbr_tag['title'].split()[-1]
        url_pep_short = find_tag(
            tr_tag,
            'a',
            attrs={'class': 'pep reference internal'}
        )
        url_pep = urljoin(PEP_URL, url_pep_short['href'])
        response = get_response(session, url_pep)
        soup = BeautifulSoup(response.text, features='lxml')
        dl_tag = find_tag(
            soup,
            'dl',
            attrs={'class': 'rfc2822 field-list simple'}
        )
        status_string = dl_tag.find(string='Status')
        status_string_parent = status_string.find_parent()
        status_page = status_string_parent.next_sibling.next_sibling.string
        if status_in_table != status_page:
            logging.info(
                    f'Несовпадающие статусы: {url_pep}   '
                    f'Статус в карточке: {status_page}   '
                    f'Статус в таблице: {status_in_table}'
                )
        statuses_list.append(status_page)

    results = [('Cтатус', 'Количество')]
    status_count = Counter(statuses_list)
    total_statuses = sum(status_count.values())
    for status, count in status_count.items():
        results.append((status, count))
    results.append(('Итого:', total_statuses))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    '''Основная функция парсера.'''
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
