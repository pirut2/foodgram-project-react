from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (ADMIN, USER,
                        USERNAME_MAX_LEN,
                        EMAIL_MAX_LEN,
                        FIRST_NAME_MAX_LEN,
                        LAST_NAME_MAX_LEN,
                        ROLE_MAX_LEN)
from .validators import (username_not_me_validator,
                         username_validator)


class User(AbstractUser):
    """Модель Пользователя."""

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USERNAME_MAX_LEN,
        blank=False,
        unique=True,
        help_text='Введите имя пользователя',
        validators=[username_not_me_validator, username_validator],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует',
        },
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_MAX_LEN,
        blank=False,
        unique=True,
        help_text='Введите адрес электронной почты',
        error_messages={
            'unique': 'Пользователь с таким email уже существует',
        },
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=FIRST_NAME_MAX_LEN,
        blank=True,
        help_text='Укажите имя',
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_MAX_LEN,
        blank=True,
        help_text='Укажите фамилию',
    )

    role = models.CharField(
        verbose_name='Роль пользователя',
        choices=ROLE_CHOICES,
        max_length=ROLE_MAX_LEN,
        default='user',
        help_text='Выберите роль пользователя',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class FollowAuthor(models.Model):
    """Подписка на атора"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            )
        ]
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписка на автора'
