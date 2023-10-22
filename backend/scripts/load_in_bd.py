"""
При разворачивании проекта из "коробки" не требуется выполнение пунктов 1 и 2.

1) pip install django-extensions;

2) Добавьте строку 'django_extensions'в список INSTALLED_APPS в settings.py;

3) python manage.py migrate - для создания таблиц в базе данных;

4) python manage.py check - найдите ошибки и, при необходимости, исправьте их;

5) python manage.py runscript load_in_bd - eсли все пойдет хорошо, вы увидите
импортированные строки, напечатанные в консоли;

6) python manage.py runserver

7) http://127.0.0.1:8000/api/ingredients/ - проверьте, как импортированные
произведения теперь отображаются на этой странице.

"""
import csv

from recipe.models import IngredientsBd


def run():
    with open('static/ingredients.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)

        IngredientsBd.objects.all().delete()

        for row in reader:
            print(row)

            category = IngredientsBd(name=row[0],
                                     measurement_unit=row[1],
                                     )
            category.save()
