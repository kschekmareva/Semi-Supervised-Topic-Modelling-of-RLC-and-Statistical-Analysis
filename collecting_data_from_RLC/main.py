
import pandas as pd
from pyaspeller import YandexSpeller
import time

speller = YandexSpeller()

file_path = 'updated_rlc_search_results_182.xlsx'
data = pd.read_excel(file_path)

def correct_text(text):
    try:
        corrections = speller.spell(text)
        for correction in corrections:
            text = text.replace(correction['word'], correction['s'][0])
        return text
    except Exception as e:
        print(f"Ошибка при обработке текста: {text}. Ошибка: {e}")
        return text


def process_in_batches(data, batch_size=20, output_file='corrected_texts.xlsx'):
    total_rows = len(data)
    start_row = 0

    with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
        for i in range(0, total_rows, batch_size):
            batch = data.iloc[i:i + batch_size].copy()
            batch['Исправленный текст'] = batch['Текст'].apply(correct_text)
            batch.to_excel(writer, index=False, header=i == 0, startrow=start_row)

            start_row += len(batch) + (
                1 if i == 0 else 0)

            print(f"Обработано строк: {i + len(batch)} из {total_rows}")
            time.sleep(2)

    print(f"Все данные сохранены в {output_file}")


process_in_batches(data)


