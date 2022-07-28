from django.db import models  # noqa F401


class Pokemon(models.Model):
    title = models.CharField('название', max_length=200)
    title_en = models.CharField('английское название', max_length=200, blank=True)
    title_jp = models.CharField('японское название', max_length=200, blank=True)

    image = models.ImageField('изображение', upload_to='pokemons/', blank=True)
    description = models.TextField('описание', blank=True)
    previous_evolution = models.ForeignKey('self',
                                           on_delete=models.CASCADE,
                                           null=True,
                                           blank=True,
                                           related_name='next_evolution',
                                           verbose_name='предыдущая эволюция')

    def __str__(self):
        return f'{self.title}'


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, verbose_name='покемон')
    lat = models.FloatField('широта')
    lon = models.FloatField('долгота')
    appeared_at = models.DateTimeField('появится', null=True)
    disappeared_at = models.DateTimeField('исчезнет', null=True)
    level = models.IntegerField('уровень', default=0)
    health = models.IntegerField('здоровье', default=0)
    strength = models.IntegerField('сила', default=0)
    defence = models.IntegerField('защита', default=0)
    stamina = models.IntegerField('выносливость', default=0)

    def __str__(self):
        return f'{self.pokemon.title} {self.level}'
