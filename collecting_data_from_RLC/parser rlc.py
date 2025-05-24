import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
from spellchecker import SpellChecker
base_url = "http://web-corpora.net/RLC/search/?exact_word=&wordform%5B%5D=&lex%5B%5D=&grammar%5B%5D=&errors%5B%5D=%28Graph%7CHyphen%7CSpace%7COrtho%7CTranslit%7CMisspell%29&from%5B%5D=1&to%5B%5D=1&wordform%5B%5D=&lex%5B%5D=&grammar%5B%5D=&errors%5B%5D=&lex_search=Поиск&date1=&date2=&gender=any&mode=any&background=any&format=полный&per_page=100&expand=%2B-1&page=1"
page_num = 1

file_path = 'rlc_search_results_(6).xlsx'
df = pd.read_excel(file_path)
original_sentences = df['Оригинальное предложение'].tolist()
cleaned_sentences = [sentence.replace('*', '').replace('{{', '').replace('}}', '') for sentence in original_sentences]
spell = SpellChecker(language='ru')

def get_page_content(page_num):
    url = base_url[:-1] + str(page_num)
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        page_html = response.content
        soup = BeautifulSoup(page_html, 'html.parser')
        return soup
    else:
        print(f"Ошибка {response.status_code}: {response.text}")



def clean_modal_text(modal_text):
    """
    Очищает текст модального окна, удаляя аннотации на английском языке в начале текста,
    текст в скобках и квадратных скобках, специальные символы и лишние пробелы.

    Параметры:
    modal_text (str): Исходный текст модального окна.

    Возвращает:
    str: Очищенный текст.
    """
    modal_text = re.sub(r'×', ' ', modal_text)

    modal_text = re.sub(r'^[^,]+,\s*[^)]+\)\s*', ' ', modal_text)

    modal_text = re.sub(r'<.*$', '', modal_text)
    modal_text = re.sub(r'\[.*?\]', ' ', modal_text)
    modal_text = re.sub(r'\(.*?\)', ' ', modal_text)
    modal_text = re.sub(r',\s*[A-Za-zА-Яа-яёЁ]+\s*', ' ', modal_text)
    modal_text = re.sub(r'\s+', ' ', modal_text).strip()
    return modal_text


def parse_page(soup, cleaned_sentences):
    if soup:
        buttons = soup.find_all('button', class_='btn btn-xs')

        for button in buttons:
            button_text = button.get_text(strip=True)

            data_target = button.get('data-target')

            if data_target:
                modal = soup.find('div', id=data_target[1:])

                if modal:
                    modal_text = modal.get_text(strip=False)
                    cleaned_modal_text = clean_modal_text(modal_text)
                    for i, sentence in enumerate(cleaned_sentences):
                        if sentence in modal_text:
                            print(f"Найдено предложение: {sentence}")
                            df.at[i, 'Текст'] = cleaned_modal_text
                else:
                    print(f"Кнопка: {button_text}")
                    print("Модальное окно не найдено.")
            else:
                print(f"Кнопка: {button_text}, но data-target не найдено.")
    else:
        print("Soup пустой, пропускаем страницу.")


def parse_all_pages(max_pages, original_sentences):
    for page_num in range(1, max_pages + 1):
        print(f"Парсинг страницы {page_num}")
        soup = get_page_content(page_num)

        if soup:
            parse_page(soup, original_sentences)
        else:
            print(f"Пропуск страницы {page_num} из-за ошибки.")

        time.sleep(2)


parse_all_pages(182, cleaned_sentences)
df.to_excel('updated_rlc_search_results_182.xlsx', index=False)
time.sleep(5)

file_path_updated = 'updated_rlc_search_results_182.xlsx'
df_new = pd.read_excel(file_path_updated)
