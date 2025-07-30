import requests
from bs4 import BeautifulSoup


def get_imdb_fullcredits(imdb_id, include_sections=None):
    """
    Извлекает данные с IMDb страницы полного списка актёров и съёмочной группы.

    :param imdb_id: ID фильма на IMDb (например, 'tt1375666').
    :param include_sections: Список секций для извлечения. Если None, извлекаются все секции.
    :return: Словарь с данными по выбранным секциям.
    """
    url = f'https://www.imdb.com/title/{imdb_id}/fullcredits/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f'Ошибка при загрузке страницы: {response.status_code}')

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}


    sections = soup.find_all('section', class_='ipc-page-section ipc-page-section--base')
    for section in sections:

        header = section.find('span', id=True)
        if not header:
            continue
        section_title = header.get_text(strip=True)


        if include_sections and section_title.lower() not in include_sections:
            continue

        section_list = []


        list_items = section.find_all('li', class_='ipc-metadata-list-summary-item')
        for li in list_items:

            name_tag = li.find('a', class_='ipc-link ipc-link--base name-credits--title-text name-credits--title-text-big')
            if name_tag:
                name = name_tag.get_text(strip=True)
                section_list.append(name)

        if section_list:
            data[section_title] = section_list

    return data
