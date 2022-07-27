from django.contrib import admin
from .models import Pokemon, PokemonEntity


@admin.register(Pokemon)
class AdminPokemon(admin.ModelAdmin):
    pass


@admin.register(PokemonEntity)
class AdminPokemonEntity(admin.ModelAdmin):
    pass
