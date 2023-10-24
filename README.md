# praktikum_new_diplom
Для доступа к админке 
password: qwerty123
email: qwerty@yandex.ru

# Со второй частью диплома README дополнится и сильно изменится.

# foodgram | REST API Service 

### Описание:
Проект Foodgram собирает рецепты пользователей

Авторизованные пользователи могут создавать удалять и редактировать собственные рецепты,

работать с подписками, избранными рецептами. Скачивать список ингредиентов для покупки.

Список тегов и ингредиентов устанавливается администратором и может быть расширен в будущем.

### Используемые технологии и библиотеки:
- Python
- Django
- Django REST framework
- Djoser
- python-dotenv
- JavaScript
- ...

### Как запустить проект:

Клонируйте репозиторий:
```
git clone git@github.com:pirut2/foodgram-project-react.git
```

Измените свою текущую рабочую дерикторию:
```
cd /foodgram-project-react/
```

Создайте и активируйте виртуальное окружение

```
python -m venv venv
```

```
source venv/scripts/activate
```

Обновите pip:
```
python3 -m pip install --upgrade pip
```

Установите зависимости из requirements.txt:

```
pip install -r requirements.txt
```
Измените рабочую дерикторию:

```
cd /backend/
```

Создайте миграции:

```
python manage.py migrate
```

Запустите скрипт добавления ингредиентов в базу данных:

```
python manage.py runscript load_in_bd
```

Запустите сервер:

```
python manage.py runserver
```
Полная документация прокта (redoc) доступна по адресу http://127.0.0.1:8000/redoc/

### Документация, эндпоинты и примеры запросов.

1. После клонирования репозитория с github запустите и авторизуйтесь в приложении docker.
2. В репозитории проекта перейдите в папку infra.
3. Выполните команду docker-compose up.

Теперь ознакомиться с документацией и эндпоинтами можно по адресу http://localhost/api/docs/

Пример запроса:

POST http://localhost/api/recipes/

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}

Пример ответа:
- код ответа сервера: 201

{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}

### Автор:
- Дмитрий Пирут - разработчик
