import logging
import re
import requests_cache

from collections import Counter, defaultdict
from outputs import control_output
from urllib.parse import urljoin
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, WHATS_NEW, DOWNLOAD
from utils import get_response, find_tag, get_soup


def whats_new(session):
    """Парсер выдает информацию об обновлениях питона."""
    whats_new_url = urljoin(MAIN_DOC_URL, WHATS_NEW)
    soup = get_soup(session, whats_new_url)
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
        soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    """Парсер выдает информацию о версиях и их статусе."""
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ValueError('Не найден список c версиями Python')

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
    """Парсер скачивает архив питона в zip формате."""
    downloads_url = urljoin(MAIN_DOC_URL, DOWNLOAD)
    soup = get_soup(session, downloads_url)
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
    """Парсер проверяем все статусы PEP и составляет таблицу с результатами."""
    soup = get_soup(session, PEP_URL)
    table = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(table, 'tbody')
    tr_tag_list = tbody_tag.find_all('tr')
    statuses_dict = defaultdict(int)
    for tr_tag in tr_tag_list:
        abbr_tag = find_tag(tr_tag, 'abbr')
        status_in_table = abbr_tag['title'].split()[-1]
        url_pep_short = find_tag(
            tr_tag,
            'a',
            attrs={'class': 'pep reference internal'}
        )
        url_pep = urljoin(PEP_URL, url_pep_short['href'])
        soup = get_soup(session, url_pep)
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
        statuses_dict[status_page] += 1
    results = [('Cтатус', 'Количество')]
    total_statuses = sum(statuses_dict.values())
    for status, count in statuses_dict.items():
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
    """Основная функция парсера."""
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
    except Exception as e:
        logging.error(f'При вызове функции {parser_mode}, возникла ошибка {e}')
        return
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
