import django.db.models.deletion
import solski_sistem.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Predmet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naziv', models.CharField(max_length=120, verbose_name='Naziv predmeta')),
                ('koda', models.CharField(max_length=20, unique=True, verbose_name='Kratica / Koda')),
                ('opis', models.TextField(blank=True, verbose_name='Opis predmeta')),
                ('letnik', models.PositiveSmallIntegerField(default=1, verbose_name='Letnik')),
                ('ustvarjeno_ob', models.DateTimeField(auto_now_add=True, verbose_name='Datum nastanka')),
                ('ucenci', models.ManyToManyField(blank=True, related_name='obiskuje_predmete', to=settings.AUTH_USER_MODEL, verbose_name='Vpisani učenci')),
                ('ucitelji', models.ManyToManyField(blank=True, related_name='poucuje_predmete', to=settings.AUTH_USER_MODEL, verbose_name='Učitelji, ki poučujejo ta predmet')),
            ],
            options={
                'verbose_name': 'Predmet',
                'verbose_name_plural': 'Predmeti',
                'ordering': ['letnik', 'naziv'],
            },
        ),
        migrations.CreateModel(
            name='Naloga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naslov', models.CharField(max_length=150, verbose_name='Naslov naloge')),
                ('navodila', models.TextField(verbose_name='Navodila za oddajo')),
                ('rok_oddaje', models.DateTimeField(blank=True, null=True, verbose_name='Rok za oddajo')),
                ('ustvarjeno_ob', models.DateTimeField(auto_now_add=True, verbose_name='Ustvarjeno')),
                ('avtor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ustvarjene_naloge', to=settings.AUTH_USER_MODEL, verbose_name='Učitelj')),
                ('predmet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='naloge', to='solski_sistem.predmet', verbose_name='Predmet')),
            ],
            options={
                'verbose_name': 'Naloga',
                'verbose_name_plural': 'Naloge',
                'ordering': ['-ustvarjeno_ob'],
            },
        ),
        migrations.CreateModel(
            name='Gradivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naslov', models.CharField(max_length=150, verbose_name='Naslov gradiva')),
                ('opis', models.TextField(blank=True, verbose_name='Opis gradiva')),
                ('datoteka', models.FileField(upload_to='gradiva/', verbose_name='Datoteka gradiva')),
                ('nalozeno_ob', models.DateTimeField(auto_now_add=True, verbose_name='Naloženo dne')),
                ('avtor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nalozena_gradiva', to=settings.AUTH_USER_MODEL, verbose_name='Učitelj (avtor)')),
                ('predmet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gradiva', to='solski_sistem.predmet', verbose_name='Predmet')),
            ],
            options={
                'verbose_name': 'Gradivo',
                'verbose_name_plural': 'Gradiva',
                'ordering': ['-nalozeno_ob'],
            },
        ),
        migrations.CreateModel(
            name='OddajaNaloge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datoteka', models.FileField(storage=solski_sistem.models.TocnoImeOverwriteStorage(), upload_to=solski_sistem.models.pot_za_oddajo_naloge, verbose_name='Oddana datoteka')),
                ('opomba', models.TextField(blank=True, verbose_name='Opomba učenca ob oddaji')),
                ('oddano_ob', models.DateTimeField(auto_now=True, verbose_name='Čas oddaje')),
                ('naloga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oddaje', to='solski_sistem.naloga', verbose_name='Naloga')),
                ('ucenec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oddane_naloge', to=settings.AUTH_USER_MODEL, verbose_name='Učenec')),
            ],
            options={
                'verbose_name': 'Oddaja naloge',
                'verbose_name_plural': 'Oddaje nalog',
                'ordering': ['-oddano_ob'],
                'unique_together': {('naloga', 'ucenec')},
            },
        ),
    ]
