from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from colorfield.fields import ColorField
from django.db import models

from .consts import LEN_CONST_NORM, LEN_CONST_SMALL

User = get_user_model()


class Tag(models.Model):
    """Тэг"""
    name = models.CharField(max_length=LEN_CONST_NORM, unique=True)
    color = ColorField(default='#FF0000', unique=True,
                       verbose_name='Цвет в формате HEX')
    slug = models.SlugField(max_length=LEN_CONST_NORM, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class IngredientsBd (models.Model):
    """Таблица ингридиентов"""
    name = models.CharField(max_length=LEN_CONST_NORM)
    measurement_unit = models.CharField(
        max_length=LEN_CONST_SMALL, verbose_name='единица измерения')

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ('name', )
        verbose_name = 'База данный ингридиентов'
        verbose_name_plural = 'База данный ингридиентов'


class IngredientsRecipe(models.Model):
    """Ингридиенты колличество. Для модели рецепта"""
    ingredients = models.ForeignKey(
        IngredientsBd,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe')
    amount = models.PositiveIntegerField(
        default=1, verbose_name='количество ингридиента')

    def __str__(self) -> str:
        return f'{self.ingredients}, {self.amount}'

    class Meta:
        verbose_name = 'Ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'


class Recipe(models.Model):
    """Рецепт"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=LEN_CONST_NORM)
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(IngredientsRecipe,
                                         related_name='recipes')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления', validators=[
            MaxValueValidator(10000),
            MinValueValidator(1)
        ])
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  verbose_name='Тег')

    def __str__(self) -> str:
        return f'{self.name} - {self.author}'

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class FollowRecipes(models.Model):
    """Подписка на рецепты"""
    recipes = models.ForeignKey(Recipe,
                                on_delete=models.CASCADE,
                                related_name='follow_recipes',
                                verbose_name='рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follow_recipes',
                             verbose_name='пользователь')

    class Meta:
        ordering = ('user', )
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipes'),
                name='unique_follow_recipes'
            )
        ]
        verbose_name = 'Рецепт подписка'
        verbose_name_plural = 'Подписки на рецепты'


class ShoppingCart(models.Model):
    """Модель корзины"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='рецепт',
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='пользователь',
    )

    def __str__(self):
        return f'{self.recipe} добавлен в корзину покупок'

    class Meta:
        verbose_name = 'Рецепты на закупку'
        verbose_name_plural = 'Рецепты на закупку'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]
