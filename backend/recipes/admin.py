from django.contrib import admin

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag, User


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class UserAdmin(BaseAdmin):
    model = User
    list_display = (
        'pk',
        'username',
        'email',
    )
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    model = Ingredient
    inlines = [
        IngredientRecipeInline,
    ]
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    inlines = [
        IngredientRecipeInline,
    ]
    list_display = (
        'pk',
        'name',
        'author',
    )
    search_fields = (
        'name',
        'author',
    )
    list_filter = (
        'author', 'name', 'tags',
    )


@admin.register(Tag)
class CategoryAdmin(BaseAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('slug',)
