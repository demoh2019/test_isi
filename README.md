# Chat Application

## Установка

1. Клонируйте репозиторий:
    ```
    git clone git@github.com:demoh2019/test_isi.git
    ```

2. Перейдите в директорию проекта:
    ```
    cd test_isi
    ```

3. Установите виртуальное окружение:
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Установите зависимости:
    ```
    pip install -r requirements.txt
    ```

5. Выполните миграции:
    ```
    python manage.py migrate
    ```

6. Создайте суперпользователя:
    ```
    python manage.py createsuperuser
    ```

7. Запустите сервер разработки:
    ```
    python manage.py runserver
    ```

## Использование

- Для доступа к админке перейдите по адресу `/admin` и войдите под учетной записью суперпользователя.
- API доступно по адресу `/api/`.

## Тестовые данные

Для загрузки тестовых данных используйте команду:
    ```
    python manage.py loaddata <dump-file>.json
    ```

## Тестирование

Запустите тесты с помощью команды:
    ```
    python manage.py test
    ```

## Аутентификация

Используется Simple JWT. Для получения токена отправьте POST-запрос на `/api/token/` с вашими учетными данными.
