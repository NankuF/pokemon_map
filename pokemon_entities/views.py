import folium
from django.http import HttpResponseNotFound
from django.shortcuts import render
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

    pokemons = Pokemon.objects.all()
    pokemons_on_page = []
    for pokemon in pokemons:
        pokemon_image_url = request.build_absolute_uri(pokemon.image.url) if pokemon.image else ''
        pokemons_on_page.append({'pokemon_id': pokemon.id, 'img_url': pokemon_image_url, 'title_ru': pokemon.title})

        pokemon_entities = PokemonEntity.objects.filter(pokemon=pokemon,
                                                        disappeared_at__gt=localtime(),
                                                        appeared_at__lte=localtime()
                                                        )
        for pokemon_entity in pokemon_entities:
            add_pokemon(
                folium_map, pokemon_entity.lat,
                pokemon_entity.lon,
                request.build_absolute_uri(pokemon_entity.pokemon.image.url)
            )

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemons = Pokemon.objects.all()

    for pokemon in pokemons:
        if pokemon.id == int(pokemon_id):
            requested_pokemon = pokemon
            break
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon.pokemon_entities.all():
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(requested_pokemon.image.url)
        )

    previous_evolution = requested_pokemon.previous_evolution if requested_pokemon.previous_evolution else ''
    prev_evol = {}
    if previous_evolution:
        prev_evol.update({'pokemon_id': previous_evolution.id, 'title_ru': previous_evolution.title})
        if previous_evolution.image:
            prev_evol['img_url'] = previous_evolution.image.url

    next_evolution =requested_pokemon.next_evolutions.all().first() if requested_pokemon.next_evolutions.all() else ''
    next_evol = {}
    if next_evolution:
        next_evol.update({'pokemon_id': next_evolution.id, 'title_ru': next_evolution.title})
        if next_evolution.image:
            next_evol['img_url'] = next_evolution.image.url

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': {
            'img_url': requested_pokemon.image.url,
            'title_ru': requested_pokemon.title,
            'title_en': requested_pokemon.title_en,
            'title_jp': requested_pokemon.title_jp,
            'description': requested_pokemon.description,
            'next_evolution': next_evol,
            'previous_evolution': prev_evol,
        }
    })
