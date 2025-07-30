QakeAPI CLI
===========

QakeAPI CLI - это инструмент командной строки для быстрого создания новых проектов QakeAPI с предустановленной структурой и общими паттернами.

Установка
--------

CLI инструмент включен в основной пакет QakeAPI. Для использования просто запустите:

.. code-block:: bash

    python3 qakeapi_cli.py --help

Основные команды
---------------

Создание проекта
~~~~~~~~~~~~~~~

Создать новый проект:

.. code-block:: bash

    # Интерактивный режим
    python3 qakeapi_cli.py create my-app

    # С указанием шаблона
    python3 qakeapi_cli.py create my-api --template=api

    # С выбором функций
    python3 qakeapi_cli.py create my-web --template=web --features=auth,templates,testing

    # Без интерактивных вопросов
    python3 qakeapi_cli.py create my-app --no-interactive --template=basic

Просмотр доступных шаблонов и функций
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python3 qakeapi_cli.py list

Доступные шаблоны
----------------

Basic API
~~~~~~~~~

Простой API с базовыми CRUD операциями.

**Функции:**
- HTTP routing с path параметрами
- Валидация запросов/ответов с Pydantic
- OpenAPI/Swagger документация

**Использование:**
.. code-block:: bash

    python3 qakeapi_cli.py create my-basic-api --template=basic

Full API
~~~~~~~~

Полноценный API с аутентификацией, базой данных и продвинутыми функциями.

**Функции:**
- HTTP routing с path параметрами
- Валидация запросов/ответов с Pydantic
- OpenAPI/Swagger документация
- JWT аутентификация
- Интеграция с базой данных (SQLAlchemy)
- Redis кэширование
- Ограничение скорости запросов

**Использование:**
.. code-block:: bash

    python3 qakeapi_cli.py create my-full-api --template=api

Web Application
~~~~~~~~~~~~~~~

Веб-приложение с шаблонами и фронтендом.

**Функции:**
- HTTP routing с path параметрами
- Валидация запросов/ответов с Pydantic
- Jinja2 движок шаблонов
- Обслуживание статических файлов
- JWT аутентификация
- CSRF защита

**Использование:**
.. code-block:: bash

    python3 qakeapi_cli.py create my-web-app --template=web

Microservice
~~~~~~~~~~~~

Легковесный микросервис с минимальными зависимостями.

**Функции:**
- HTTP routing с path параметрами
- Валидация запросов/ответов с Pydantic
- Health check эндпоинты
- Метрики приложения

**Использование:**
.. code-block:: bash

    python3 qakeapi_cli.py create my-microservice --template=microservice

Доступные функции
----------------

Основные функции
~~~~~~~~~~~~~~~

- **routing** - HTTP routing с path параметрами
- **validation** - Валидация запросов/ответов с Pydantic
- **docs** - OpenAPI/Swagger документация
- **auth** - JWT аутентификация
- **database** - Интеграция с базой данных (SQLAlchemy)
- **cache** - Redis кэширование
- **rate_limit** - Ограничение скорости запросов

Веб-функции
~~~~~~~~~~~

- **templates** - Jinja2 движок шаблонов
- **static** - Обслуживание статических файлов
- **csrf** - CSRF защита
- **websockets** - Поддержка WebSocket
- **live_reload** - Live reload для разработки

Дополнительные функции
~~~~~~~~~~~~~~~~~~~~~

- **background** - Обработка фоновых задач
- **file_upload** - Обработка загрузки файлов
- **health** - Health check эндпоинты
- **metrics** - Метрики приложения
- **logging** - Структурированное логирование
- **testing** - Тестовый набор с pytest
- **docker** - Docker конфигурация

Структура создаваемого проекта
-----------------------------

Базовая структура
~~~~~~~~~~~~~~~~

.. code-block:: text

    my-app/
    ├── app/
    │   ├── main.py          # Основной файл приложения
    │   ├── config.py        # Конфигурация
    │   ├── auth.py          # Аутентификация (если включена)
    │   ├── models.py        # Модели БД (если включена)
    │   ├── api/             # API эндпоинты
    │   ├── core/            # Основная логика
    │   ├── schemas/         # Pydantic схемы
    │   ├── services/        # Бизнес-логика
    │   └── utils/           # Утилиты
    ├── tests/               # Тесты
    ├── docs/                # Документация
    ├── templates/           # Шаблоны (если включены)
    ├── static/              # Статические файлы (если включены)
    ├── requirements.txt     # Зависимости
    ├── README.md           # Документация проекта
    └── pytest.ini         # Конфигурация pytest (если включены тесты)

Дополнительные файлы
~~~~~~~~~~~~~~~~~~~

В зависимости от выбранных функций могут быть созданы:

- **Dockerfile** - Docker конфигурация
- **docker-compose.yml** - Docker Compose конфигурация
- **migrations/** - Миграции БД
- **alembic/** - Конфигурация Alembic

Интерактивный режим
------------------

При запуске без флага ``--no-interactive`` CLI задаст вам вопросы:

1. **Название проекта** - имя директории проекта
2. **Описание проекта** - краткое описание
3. **Версия** - версия проекта
4. **Автор** - имя автора
5. **Email** - email автора
6. **Шаблон** - выбор из доступных шаблонов
7. **Функции** - выбор дополнительных функций
8. **Подтверждение** - подтверждение создания проекта

Пример интерактивного создания:

.. code-block:: bash

    $ python3 qakeapi_cli.py create my-app

    ============================================================
      🚀 QakeAPI Project Generator
    ============================================================

    ℹ️  Let's create your QakeAPI project!
    Project name [my-app]: 
    Project description [A QakeAPI application]: My Awesome API
    Version [1.0.0]: 
    Author [Your Name]: John Doe
    Email [your.email@example.com]: john@example.com

    Select project template:
      → 1. Basic API
        2. Full API
        3. Web Application
        4. Microservice

    Select option [1-4] (default: 1): 2

    ℹ️  Selected template: Full API
    ℹ️  Description: Complete API with authentication, database, and advanced features

    Available features:
    Select features to include:
      1. routing - HTTP routing with path parameters
      2. validation - Request/response validation with Pydantic
      ...
      19. live_reload - Development live reload

    Enter numbers separated by commas (e.g., 1,3,5) or 'all' for all features:
    Your choice: 1,2,3,4,5,6,7,17

    ✅ Selected 8 features

    ============================================================
      📋 Project Summary
    ============================================================

    Project Name: my-app
    Description: My Awesome API
    Template: Full API
    Features: auth, cache, database, docs, rate_limit, routing, testing, validation

    Generate project? [Y/n]: Y

    ✅ Project 'my-app' generated successfully!

Следующие шаги
-------------

После создания проекта:

1. **Перейдите в директорию проекта:**
   .. code-block:: bash

       cd my-app

2. **Создайте виртуальное окружение:**
   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # На Windows: venv\Scripts\activate

3. **Установите зависимости:**
   .. code-block:: bash

       pip install -r requirements.txt

4. **Запустите приложение:**
   .. code-block:: bash

       python app/main.py

5. **Откройте в браузере:**
   - http://localhost:8000 - основная страница
   - http://localhost:8000/docs - API документация

Если включен Docker:
.. code-block:: bash

    docker-compose up --build

Примеры использования
--------------------

Создание простого API
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python3 qakeapi_cli.py create simple-api --template=basic

Создание веб-приложения с аутентификацией
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python3 qakeapi_cli.py create web-app --template=web --features=auth,templates,testing

Создание микросервиса
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python3 qakeapi_cli.py create microservice --template=microservice --features=health,metrics,logging

Создание полноценного API с Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python3 qakeapi_cli.py create full-api --template=api --features=docker,testing

Настройка и кастомизация
-----------------------

После создания проекта вы можете:

1. **Настроить конфигурацию** в ``app/config.py``
2. **Добавить новые эндпоинты** в ``app/main.py``
3. **Создать модели БД** в ``app/models.py``
4. **Добавить схемы валидации** в ``app/schemas/``
5. **Настроить аутентификацию** в ``app/auth.py``
6. **Добавить тесты** в ``tests/``
7. **Настроить Docker** в ``Dockerfile`` и ``docker-compose.yml``

CLI инструмент создает базовую структуру, которую вы можете расширять под свои нужды. 