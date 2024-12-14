import os
import fnmatch
import csv


class IncorrectHeaders(Exception):
    def __init__(self, message):
        self.message = message


class PriceMachine:
    def __init__(self):
        self.file_mask = ''  # Маска поиска файла
        self.dir_path = ''  # Путь к корню каталога
        self.__files = []  # Список найденных файлов
        self.__data = []  # Собранные данные

        self.col_product = []
        self.col_price = []
        self.col_weight = []

    def __search_file(self) -> str:
        """
        Поиск файлов по маске в директории
        :return: список найденных файлов
        """

        self.__files.clear()
        for root, dirs, files in os.walk(self.dir_path):
            for name in files:
                if fnmatch.fnmatch(name, self.file_mask):
                    self.__files.append(os.path.join(root, name))
        return f'Найдено {len(self.__files)} файлов.'

    def load_prices(self):
        """
        Загрузка данных из файлов
        """

        print(self.__search_file())  # Поиск файлов и вывод результатов

        # Проверка найденных файлов
        if len(self.__files) == 0:
            raise f'ERROR: Найдено 0 файлов по маске "{self.file_mask}"!'

        self.__data.clear()
        for file_path in self.__files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file, delimiter=',')
                    headers = reader.fieldnames  # Получаем заголовки

                    # Проверка на валидность колонок и получение номеров столбцов
                    try:
                        product_id, price_id, weight_id = self.__search_product_price_weight(headers)
                    except IncorrectHeaders as e:
                        print(e, file_path)
                        continue

                    # print(headers[product_id], headers[price_id], type(weight_id))
                    # print("{:<5} {:<50} {:<10} {:<10} {:<20} {:<15}".format(
                    #     "Номер", "Наименование", "Цена", "Вес", "Файл", "Цена за кг."))

                    # Получение данных
                    for idx, item in enumerate(reader, start=1):
                        product = item[headers[product_id]]
                        price = float(item[headers[price_id]])
                        weight = float(item[headers[weight_id]])

                        # if idx == 1:
                        #     print("{:<5} {:<50} {:<10} {:<10} {:<20} {:<15.2f}".format(
                        #         idx,
                        #         product,
                        #         price,
                        #         weight,
                        #         os.path.basename(file_path),
                        #         (price / weight),
                        #     ))

                        self.__data.append({
                            'Наименование': product,
                            'Цена': price,
                            'Вес': weight,
                            'Файл': os.path.basename(file_path),
                            'Цена за кг.': (price / weight),
                        })

            except FileNotFoundError:
                print(f'ERROR FileNotFoundError: Файл {file_path} не найден!')
            except ValueError as e:
                print(f"ERROR ValueError: {e}")
            except Exception as e:
                print(f'ERROR Exception: {file_path}: {e}!')

        self.__data.sort(key=lambda x: x['Цена за кг.'])

        # for idx, item in enumerate(self.data[:50], start=1):
        #     print("{:<5} {:<50} {:<10} {:<10} {:<20} {:<15.2f}".format(
        #         idx,
        #         item['Наименование'],
        #         item['Цена'],
        #         item['Вес'],
        #         item['Файл'],
        #         item['Цена за кг.'],
        #     ))

    def __search_product_price_weight(self, headers) -> tuple[int, int, int]:
        """
            Проверка на корректное кол-во колонок и получение номеров столбцов
            :param headers: заголовки таблиц
            :return: номера столбцов
        """
        if not set(self.col_product).intersection(headers):
            raise IncorrectHeaders(f'ERROR IncorrectHeaders: Не найдены колонки для поиска:'
                                   f'{self.col_product}')
        if not set(self.col_price).intersection(headers):
            raise IncorrectHeaders(f'ERROR IncorrectHeaders: Не найдены колонки для поиска:'
                                   f'{self.col_price}')
        if not set(self.col_weight).intersection(headers):
            raise IncorrectHeaders(f'ERROR IncorrectHeaders: Не найдены колонки для поиска:'
                                   f'{self.col_weight}')

        product_id = next(headers.index(col) for col in self.col_product if col in headers)
        price_id = next(headers.index(col) for col in self.col_price if col in headers)
        weight_id = next(headers.index(col) for col in self.col_weight if col in headers)
        return product_id, price_id, weight_id

    def find_text(self, find_product: str):
        """
        Поиск по наименованию
        :param find_product: текст поиска
        """

        found_items = []
        for item in self.__data:
            if find_product.lower() in item['Наименование'].lower():
                found_items.append(item)

        if not found_items:
            print('Поиск не дал результатов.')
        else:
            print("{:<5} {:<50} {:<10} {:<10} {:<20} {:<15}".format(
                "Номер", "Наименование", "Цена", "Вес", "Файл", "Цена за кг."))
            for idx, item in enumerate(found_items, start=1):
                print("{:<5} {:<50} {:<10} {:<10} {:<20} {:<15.2f}".format(
                    idx,
                    item['Наименование'],
                    item['Цена'],
                    item['Вес'],
                    item['Файл'],
                    item['Цена за кг.'],
                ))

    def export_to_html(self, name='output.html'):
        """
        Экспорт данных в html файл
        :param name: имя файла
        :return: имя файла
        """

        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for idx, item in enumerate(self.__data, start=1):
            result += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{item['Наименование']}</td>
                    <td>{item['Цена']}</td>
                    <td>{item['Вес']}</td>
                    <td>{item['Файл']}</td>
                    <td>{item['Цена за кг.']:.2f}</td>
                </tr>
            '''
        result += '''</table></body></html>'''
        with open(name, 'w', encoding='utf-8') as file:
            file.write(result)
        return name


pm = PriceMachine()

pm.dir_path = os.path.dirname(os.path.realpath(__file__))  # Путь к корню каталога поиска файлов
pm.file_mask = "price*.csv"  # Маска для поиска файлов

pm.col_product = ['название', 'продукт', 'товар', 'наименование', ]
pm.col_price = ['цена', 'розница', ]
pm.col_weight = ['фасовка', 'масса', 'вес']

pm.load_prices()  # Загрузка данных

help_cmd = f'\n(q, exit) Выход\n'  # Справка по командам

while True:
    text = input(f'{help_cmd}Введите текст для поиска:').lower().strip()
    if not text:
        print('Ошибка! Введите текст для поиска.')
    elif text in ('q', 'exit',):
        break
    pm.find_text(text)

print('Экспорт в файл: ', pm.export_to_html())
print('Программа завершена.')
