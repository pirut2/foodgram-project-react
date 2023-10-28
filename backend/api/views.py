from datetime import datetime
from django.http import HttpResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action

from recipe.models import (FollowRecipes, IngredientsBd,
                           IngredientsRecipe, Recipe,
                           ShoppingCart, Tag)
from .pagination import RecipePagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .filters import RecipeFilter, IngredientsBdFilter
from .serializers import (IngredientsBdSerializer, RecipeReadSerializer,
                          RecipeForFollowSerializer, RecipeWriteSerializer,
                          TagSerializer)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientsBdViewSet(ModelViewSet):
    queryset = IngredientsBd.objects.all()
    serializer_class = IngredientsBdSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientsBdFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Метод для добавления/удаления из избранного."""
        if request.method == 'POST':
            if FollowRecipes.objects.filter(user=request.user,
                                            recipes__id=pk).exists():
                return Response({'Рецепт уже добален в избранное.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not Recipe.objects.filter(id=pk).exists():
                return Response({'Такого рецепта не существует.'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = Recipe.objects.get(id=pk)
            FollowRecipes.objects.create(user=request.user, recipes=recipe)
            serializer = RecipeForFollowSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            obj = FollowRecipes.objects.filter(
                user=request.user, recipes__id=pk)
            if obj.exists():
                obj.delete()
                return Response({'Рецепт успешно удален из избранного.'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'Рецепта, который Вы хотите удалить'
                            'из избранного, не существует.'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Метод для добавления/удаления из списка покупок."""
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe__id=pk).exists():
                return Response({'Рецепт уже добален в список покупок.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not Recipe.objects.filter(id=pk).exists():
                return Response({'Такого рецепта не существует.'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = Recipe.objects.get(id=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeForFollowSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            obj = ShoppingCart.objects.filter(user=request.user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response({'Рецепт успешно удален из списка покупок.'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'Рецепта, '
                             'который Вы хотите удалить'
                             'из списка покупок, не существует.'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""
        user = request.user
        if not user.shopping_cart.exists():
            return Response('У Вас отсутствует Shopping_cart',
                            status=HTTP_400_BAD_REQUEST)
        date = datetime.today()
        ingredients = IngredientsRecipe.objects.filter(
            recipes__shopping_cart__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        download_list_1 = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {date:%Y-%m-%d}\n\n'
        )
        download_list_2 = '\n'.join([
            f'- {ingredient["ingredients__name"]} '
            f'({ingredient["ingredients__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        download_list = download_list_1 + download_list_2
        filename = f'{user.username}_shopping_list.pdf'

        response = HttpResponse(
            download_list, content_type='text.txt, charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
