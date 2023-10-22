from django.contrib import admin

from .models import (Tag, IngredientsBd,
                     IngredientsRecipe,
                     Recipe, FollowRecipes, ShoppingCart)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', )


@admin.register(IngredientsBd)
class IngredientsBdAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    list_filter = ('name', )


@admin.register(IngredientsRecipe)
class IngredientsRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredients', 'amount', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_recipe')
    readonly_fields = ('favorites_recipe',)
    list_filter = ('name', 'author',)
    empty_value_display = '-пусто-'

    def favorites_recipe(self, obj):
        return obj.follow_recipes.count()


@admin.register(FollowRecipes)
class FollowRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipes', 'user', )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', )
