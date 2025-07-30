from django.urls import resolve, reverse


class CRUDAPITestMixin:
    """
    Универсальный миксин для тестирования REST API эндпоинтов справочников и CRUD-ресурсов.

    Миксин автоматизирует тестирование следующих аспектов API:
      - Проверка корректного разрешения URL на ожидаемый view-класс (resolve) для всех типов эндпоинтов (list, retrieve, create, update).
      - Проверка разрешённых и запрещённых HTTP-методов (GET, POST, PUT, PATCH, DELETE) для каждого эндпоинта.
      - Проверка обработки аутентификации (например, возврат 401 для анонимных пользователей).
      - Тестирование поведения при пустом наборе данных (например, пустой список объектов).

    Для корректной работы миксина необходимо в методе setUp дочернего тестового класса инициализировать поля `user` (для аутентификации) и, при необходимости, `obj` (для тестирования detail/update эндпоинтов).

    Attributes:
        list_url_name (str): Имя URL для эндпоинта списка объектов.
        retrieve_url_name (str): Имя URL для эндпоинта получения объекта по ID.
        create_url_name (str): Имя URL для эндпоинта создания объекта.
        update_url_name (str): Имя URL для эндпоинта обновления объекта.
        list_view_class (type): Класс view для списка.
        retrieve_view_class (type): Класс view для получения объекта.
        create_view_class (type): Класс view для создания объекта.
        update_view_class (type): Класс view для обновления объекта.
        allowed_list_methods (list[str]): Разрешённые методы для списка.
        allowed_retrieve_methods (list[str]): Разрешённые методы для получения объекта.
        allowed_create_methods (list[str]): Разрешённые методы для создания объекта.
        allowed_update_methods (list[str]): Разрешённые методы для обновления объекта.
        model (type): Модель, с которой работает справочник.
        user (User): Пользователь для аутентификации в тестах. Должен быть инициализирован в setUp.
        obj (Model): Объект для тестирования retrieve/update эндпоинтов. Должен быть инициализирован в setUp, если используется.
        lookup_url_kwarg (str): Имя параметра для detail-эндпоинтов (по умолчанию 'pk').

    Example:
        Пример использования:
        ```
        class OfficesAPITest(CRUDAPITestMixin, APITestCase):
            list_url_name = "offices-list"
            retrieve_url_name = "offices-retrieve"
            list_view_class = OfficeListView
            retrieve_view_class = OfficeRetrieveView
            allowed_list_methods = ["get"]
            allowed_retrieve_methods = ["get"]
            model = Office
            lookup_url_kwarg = "office_id"

            def setUp(self):
                self.user = User.objects.create_user(email="test@test.com", password="123")
                self.client.force_authenticate(user=self.user)
                self.obj = Office.objects.create(
                    name="Test", address="Addr", city="City", country="Country"
                )
        ```
    """

    # URL names (указать в дочерних классах)
    list_url_name = None
    retrieve_url_name = None
    create_url_name = None
    update_url_name = None

    # View-классы для проверки resolve (опционально)
    list_view_class = None
    retrieve_view_class = None
    create_view_class = None
    update_view_class = None

    # Разрешённые методы для каждого типа эндпоинта
    allowed_list_methods = ["get"]
    allowed_retrieve_methods = ["get"]
    allowed_create_methods = ["post"]
    allowed_update_methods = ["put", "patch"]

    anonymous_list_status_code = 401  # по умолчанию

    # Модель для теста пустого списка и других проверок
    model = None

    # Пользователь для аутентификации (заполнить в setUp)
    user = None

    # Объект для detail/update (заполнить в setUp, если нужно)
    obj = None

    # Имя параметра для detail-эндпоинтов (можно переопределять в дочерних классах)
    lookup_url_kwarg = "pk"

    def _get_lookup_kwargs(self):
        """
        Возвращает словарь для передачи в reverse(kwargs=...) для detail-эндпоинтов.
        """
        return {self.lookup_url_kwarg: getattr(self.obj, "id")}

    def _check_allowed_methods(self, url, allowed_methods):
        """
        Проверяет, что все разрешённые методы НЕ возвращают 405.
        """
        for method in allowed_methods:
            response = getattr(self.client, method)(url)
            self.assertNotEqual(
                response.status_code,
                405,
                msg=f"Method {method.upper()} should be allowed for {url}",
            )

    def _check_not_allowed_methods(self, url, allowed_methods):
        """
        Проверяет, что все НЕразрешённые методы возвращают 405.
        """
        all_methods = {"get", "post", "put", "patch", "delete"}
        not_allowed = all_methods - set(allowed_methods)
        for method in not_allowed:
            response = getattr(self.client, method)(url)
            self.assertEqual(
                response.status_code,
                405,
                msg=f"Method {method.upper()} should NOT be allowed for {url}",
            )

    # --- Тесты для списка ---
    def test_list_url_resolves_to_view(self):
        if self.list_url_name and self.list_view_class:
            found = resolve(reverse(self.list_url_name))
            assert found.func.view_class == self.list_view_class

    def test_list_methods_allowed(self):
        if not self.list_url_name:
            return
        url = reverse(self.list_url_name)
        self._check_allowed_methods(url, self.allowed_list_methods)

    def test_list_methods_not_allowed(self):
        if not self.list_url_name:
            return
        url = reverse(self.list_url_name)
        self._check_not_allowed_methods(url, self.allowed_list_methods)

    def test_list_anonymous_access(self):
        if not self.list_url_name:
            return
        url = reverse(self.list_url_name)
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, self.anonymous_list_status_code)

    def test_list_empty(self):
        if not self.list_url_name or not self.model:
            return
        self.model.objects.all().delete()
        url = reverse(self.list_url_name)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if isinstance(data, list):
            self.assertEqual(len(data), 0)
        elif isinstance(data, dict):
            lists = [v for v in data.values() if isinstance(v, list)]
            self.assertTrue(lists, "В ответе нет списка!")
            self.assertEqual(len(lists[0]), 0)
        else:
            self.fail("Неизвестный формат ответа: %s" % type(data))

    # --- Тесты для retrieve ---
    def test_retrieve_url_resolves_to_view(self):
        if self.retrieve_url_name and self.retrieve_view_class and self.obj:
            url = reverse(self.retrieve_url_name, kwargs=self._get_lookup_kwargs())
            found = resolve(url)
            assert found.func.view_class == self.retrieve_view_class

    def test_retrieve_methods_allowed(self):
        if not self.retrieve_url_name or not self.obj:
            return
        url = reverse(self.retrieve_url_name, kwargs=self._get_lookup_kwargs())
        self._check_allowed_methods(url, self.allowed_retrieve_methods)

    def test_retrieve_methods_not_allowed(self):
        if not self.retrieve_url_name or not self.obj:
            return
        url = reverse(self.retrieve_url_name, kwargs=self._get_lookup_kwargs())
        self._check_not_allowed_methods(url, self.allowed_retrieve_methods)

    # --- Тесты для create ---
    def test_create_url_resolves_to_view(self):
        if self.create_url_name and self.create_view_class:
            url = reverse(self.create_url_name)
            found = resolve(url)
            assert found.func.view_class == self.create_view_class

    def test_create_methods_allowed(self):
        if not self.create_url_name:
            return
        url = reverse(self.create_url_name)
        self._check_allowed_methods(url, self.allowed_create_methods)

    def test_create_methods_not_allowed(self):
        if not self.create_url_name:
            return
        url = reverse(self.create_url_name)
        self._check_not_allowed_methods(url, self.allowed_create_methods)

    # --- Тесты для update ---
    def test_update_url_resolves_to_view(self):
        if self.update_url_name and self.update_view_class and self.obj:
            url = reverse(self.update_url_name, kwargs=self._get_lookup_kwargs())
            found = resolve(url)
            assert found.func.view_class == self.update_view_class

    def test_update_methods_allowed(self):
        if not self.update_url_name or not self.obj:
            return
        url = reverse(self.update_url_name, kwargs=self._get_lookup_kwargs())
        self._check_allowed_methods(url, self.allowed_update_methods)

    def test_update_methods_not_allowed(self):
        if not self.update_url_name or not self.obj:
            return
        url = reverse(self.update_url_name, kwargs=self._get_lookup_kwargs())
        self._check_not_allowed_methods(url, self.allowed_update_methods)
