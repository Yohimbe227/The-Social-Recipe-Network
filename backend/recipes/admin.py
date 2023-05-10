from django.contrib import admin

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag, User, \
    TagRecipe


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 2


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

    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    model = Tag
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('slug',)


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    inlines = [
        IngredientRecipeInline,
        TagRecipeInline,
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



