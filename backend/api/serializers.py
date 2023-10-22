from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from recipe.models import Recipe, Tag, IngredientsBd, IngredientsRecipe
from users.models import User, FollowAuthor


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return UserAfterRegistration(instance, context=context).data


class UserAfterRegistration(UserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FollowAuthor.objects.filter(user=user, author=author).exists()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientsBdSerializer(ModelSerializer):
    class Meta:
        model = IngredientsBd
        fields = ('id', 'name', 'measurement_unit', )


class IngredientsRecipeSerializer(ModelSerializer):
    id = IntegerField(required=True)
    name = SerializerMethodField(read_only=True)
    measurement_unit = SerializerMethodField(read_only=True)
    amount = IntegerField(required=True)

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount', )

    def get_name(self, obj):
        ingredients_bd_name = IngredientsBd.objects.get(id=obj.id)
        return ingredients_bd_name.name

    def get_measurement_unit(self, obj):
        ingredients_bd_measurement_unit = IngredientsBd.objects.get(id=obj.id)
        return ingredients_bd_measurement_unit.measurement_unit


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follow_recipes.filter(recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
        required=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializer(many=True, required=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredients = []
        if len(value) == 0:
            raise ValidationError(
                detail='Отсутствуют значения в поле ingredients',
                code=status.HTTP_400_BAD_REQUEST
            )
        for item in value:
            if not IngredientsBd.objects.filter(id=item['id']).exists():
                raise ValidationError(
                    detail='Такого ингредиента не существует',
                    code=status.HTTP_400_BAD_REQUEST
                )
            ing = get_object_or_404(IngredientsBd, id=item['id'])
            if ing in ingredients:
                raise ValidationError({
                    'ingredients': 'Повтор ингридиента.'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество не может быть равно 0.'
                })
            ingredients.append(ing)
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег!'})
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги должны быть уникальными!'})
            tags_list.append(tag)
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError(
                detail=('Картинка для рецепта обязательна'),
                code=status.HTTP_400_BAD_REQUEST
            )
        return value

    def create_ingredients_amount(self, ingredients, recipe):
        for ingr in ingredients:
            ing, _ = IngredientsRecipe.objects.get_or_create(
                ingredients=IngredientsBd.objects.get(id=ingr['id']),
                amount=ingr['amount'],
            )
            recipe.ingredients.add(ing.id)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amount(recipe=recipe,
                                       ingredients=ingredients,
                                       )
        return recipe

    def update(self, instance, validated_data):
        if 'tags' not in validated_data:
            raise ValidationError(
                detail='Вы не заполнили поле tags или ingredients',
                code=status.HTTP_400_BAD_REQUEST
            )
        if 'ingredients' not in validated_data:
            raise ValidationError(
                detail='Вы не заполнили поле tags или ingredients',
                code=status.HTTP_400_BAD_REQUEST
            )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amount(recipe=instance,
                                       ingredients=ingredients,
                                       )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeForFollowSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowAuthorSerializer(CustomUserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if FollowAuthor.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='на самого себя подписаться не получится)',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeForFollowSerializer(
            recipes, many=True, read_only=True)
        return serializer.data
