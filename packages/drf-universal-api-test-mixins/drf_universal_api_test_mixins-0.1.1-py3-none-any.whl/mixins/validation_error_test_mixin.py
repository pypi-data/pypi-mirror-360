class ValidationErrorTestMixin:
    """
    Миксин предназначен для проверки ответов с ошибками валидации на запросы с телом (POST, PUT, PATCH).
    Возможно явно указать по каким полям ожидаются ошибки.
    """

    def check_validation_error_response(self, response, expected_error_fields=None):
        """
        Проверяет структуру ответа при ошибках валидации.

        Args:
            response: объект Response от DRF.
            expected_error_fields (list or set, optional): список ожидаемых полей с ошибками.
        """
        self.assertEqual(response.status_code, 400, "Ожидается статус 400 Bad Request")
        data = response.json()
        self.assertIsInstance(data, dict, "Ответ должен быть словарём с ошибками")

        if expected_error_fields:
            # Проверяем, что в ответе есть ошибки по ожидаемым полям
            for field in expected_error_fields:
                self.assertIn(field, data, f"Ожидается ошибка по полю '{field}'")

        # Проверяем, что для каждого поля ошибки — непустой список строк
        for errors in data.values():
            self.assertIsInstance(errors, list, "Ошибки должны быть списком")
            self.assertTrue(all(isinstance(e, str) and e for e in errors), "Все ошибки должны быть непустыми строками")
