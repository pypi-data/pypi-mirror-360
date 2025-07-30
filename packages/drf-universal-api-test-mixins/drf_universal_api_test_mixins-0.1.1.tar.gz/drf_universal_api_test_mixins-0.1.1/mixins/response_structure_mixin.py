class ResponseStructureMixin:
    """
    Миксин для проверки структуры и содержимого ответов API (list/retrieve).
    Подходит для GET, POST, PUT, PATCH - запросов. Проверяет структуру JSON-ответа

    Использование:
    - Для проверки списка определите `expected_item_fields` и (опционально) `expected_list_order`
      (для проверки порядка возвращаемых объектов).
    - Для проверки retrieve-ответа определите `expected_retrieve_fields` и (опционально) `expected_retrieve_values`.
    - Для универсальности укажите `list_key` (например, "offices", "results" и т.д.), если ваш API возвращает не список, а словарь с ключом-списком.
    - Для проверки дополнительных полей в корне ответа (например, `default_office_id`) используйте `expected_extra_fields`.

    Особенности:
    - Метод `check_retrieve_response_structure` подходит не только для GET-запросов retrieve,
      но и для любых других HTTP-методов (POST, PUT, PATCH), которые возвращают один объект в ответе.
    - Это позволяет использовать миксин для проверки структуры ответов на создание, обновление и получение объекта.

    Атрибуты:
        expected_item_fields (set or list): Ожидаемые поля в каждом объекте списка.
        expected_list_order (dict): Определяет поле и ожидаемый порядок значений для проверки порядка элементов.
        list_key (str): Ключ словаря, в котором лежит список объектов (если ответ — словарь).
        expected_extra_fields (list): Дополнительные поля в корне ответа.
        expected_retrieve_fields (set or list): Ожидаемые поля в объекте retrieve/создания/обновления.
        expected_retrieve_values (dict): Ожидаемые значения некоторых полей объекта.
    """
    # Для list-эндпоинтов
    expected_item_fields = None
    expected_list_order = None
    list_key = None  # имя ключа, в котором лежит список объектов (например, "offices")
    expected_extra_fields = None  # список дополнительных полей в корне ответа
                                  # (например, "default_office_id")

    # Для retrieve-эндпоинтов
    expected_retrieve_fields = None
    expected_retrieve_values = None

    def extract_list_from_response(self, data):
        """
        Универсально извлекает список объектов из ответа.
        """
        # Если явно задан ключ (например, 'results'), в котором лежит список объектов
        if self.list_key:
            # Проверяем, что этот ключ есть в словаре data
            self.assertIn(self.list_key, data, f"В ответе нет ключа '{self.list_key}'")
            # Берём список объектов по этому ключу
            items = data[self.list_key]
        # Если ответ — это уже список (например, просто [...])
        elif isinstance(data, list):
            # Тогда считаем, что items — это сам data
            items = data
        # Если ответ — словарь, но ключ для списка не задан
        elif isinstance(data, dict):
            # Ищем все значения в словаре, которые являются списками
            lists = [v for v in data.values() if isinstance(v, list)]
            # Если среди значений ровно один список
            if len(lists) == 1:
                # Берём этот единственный список как items
                items = lists[0]
            else:
                # Если списков нет или их несколько — не можем однозначно определить, где список объектов
                raise AssertionError(
                    f"Не удалось однозначно определить список объектов в ответе: {data}"
                )
        else:
            # Если data — не список и не словарь — формат ответа неизвестен, ошибка
            raise AssertionError(
                f"Неизвестный формат ответа: {type(data)} — {data}"
            )
        # Проверяем, что items действительно список
        self.assertIsInstance(items, list, "Ожидался список объектов")
        return items

    def check_list_response_structure(self, response):
        """
        Проверяет структуру и порядок объектов в list-ответе.
        """
        data = response.json()

        # Если определены дополнительные поля, которые должны быть в корне ответа,
        # и ответ — словарь
        if self.expected_extra_fields and isinstance(data, dict):
            # Для каждого такого дополнительного поля проверяем, что оно есть в ответе
            for field in self.expected_extra_fields:
                self.assertIn(field, data, f"В ответе нет обязательного поля '{field}'")

        # Извлекаем список объектов из ответа
        items = self.extract_list_from_response(data)

        # Если определены ожидаемые поля у каждого объекта списка
        if self.expected_item_fields:
            # Для каждого объекта проверяем, что набор ключей совпадает с ожидаемым
            for item in items:
                self.assertEqual(
                    set(item.keys()), set(self.expected_item_fields),
                    f"Поля объекта: {item}"
                )

        # Если определён порядок элементов, который нужно проверить
        if self.expected_list_order:
            # Формируем список значений поля, по которому проверяем порядок
            order = [item[self.expected_list_order["field"]] for item in items]
            # Сравниваем полученный порядок с ожидаемым
            self.assertEqual(
                order, self.expected_list_order["values"],
                "Порядок элементов не совпадает"
            )

    def check_retrieve_response_structure(self, response):
        """
        Проверяет, что ответ на запрос retrieve (или аналогичный) соответствует ожидаемой структуре
        и содержит правильные данные.
        """
        data = response.json()
        self.assertIsInstance(data, dict, "Ответ должен быть объектом (dict)")
        # Если заданы ожидаемые поля объекта
        if self.expected_retrieve_fields:
            # Проверяем, что набор ключей в ответе совпадает с ожидаемым набором
            self.assertEqual(
                set(data.keys()),
                set(self.expected_retrieve_fields),
                f"Поля объекта: {data}"
            )
        # Если заданы ожидаемые значения для некоторых полей объекта
        if self.expected_retrieve_values:
            # Для каждого поля и ожидаемого значения проверяем, что в ответе совпадает значение
            for key, value in self.expected_retrieve_values.items():
                self.assertEqual(
                    data.get(key),
                    value,
                    f"Значение поля '{key}' не совпадает: {data.get(key)} != {value}"
                )