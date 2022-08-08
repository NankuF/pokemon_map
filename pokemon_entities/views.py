import folium
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import localtime
from pokemon_entities.models import Pokemon, PokemonEntity

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    pokemon_entities = PokemonEntity.objects.select_related('pokemon').filter(appeared_at__lte=localtime(),
                                                                              disappeared_at__gt=localtime()
                                                                              )
    pokemons_on_page = []
    for p_entity in pokemon_entities:
        pokemon_image_url = request.build_absolute_uri(p_entity.pokemon.image.url) if p_entity.pokemon.image else None
        pokemons_on_page.append({'pokemon_id': p_entity.pokemon.id,
                                 'img_url': pokemon_image_url,
                                 'title_ru': p_entity.pokemon.title})

        add_pokemon(
            folium_map, p_entity.lat,
            p_entity.lon,
            request.build_absolute_uri(p_entity.pokemon.image.url)
        )

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemons = Pokemon.objects.select_related('previous_evolution')
    pokemon = get_object_or_404(pokemons, id=pokemon_id)

    if pokemon.id == int(pokemon_id):
        requested_pokemon = pokemon
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon.pokemon_entities.all():
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(requested_pokemon.image.url)
        )

    previous_evolution = requested_pokemon.previous_evolution if requested_pokemon.previous_evolution else None
    next_evolution = requested_pokemon.next_evolutions.first()
    previous_evolution_pokemon = next_evolution_pokemon = None
    if previous_evolution:
        previous_evolution_pokemon = {
            'pokemon_id': previous_evolution.id,
            'title_ru': previous_evolution.title,
            'img_url': previous_evolution.image.url if previous_evolution.image else None
        }
    if next_evolution:
        next_evolution_pokemon = {
            'pokemon_id': next_evolution.id,
            'title_ru': next_evolution.title,
            'img_url': next_evolution.image.url if next_evolution.image else None
        }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': {
            'img_url': requested_pokemon.image.url,
            'title_ru': requested_pokemon.title,
            'title_en': requested_pokemon.title_en,
            'title_jp': requested_pokemon.title_jp,
            'description': requested_pokemon.description,
            'next_evolution': next_evolution_pokemon,
            'previous_evolution': previous_evolution_pokemon,
        }
    })
