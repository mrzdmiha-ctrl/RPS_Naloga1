#!/bin/sh
set -e

echo "Čakam na zagon PostgreSQL baze podatkov..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL baza podatkov je pripravljena!"

echo "Izvajam migracije podatkovne baze..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Zbiram statične datoteke..."
python manage.py collectstatic --noinput

echo "Polnim bazo z začetnimi podatki (predmeti, učitelji, učenci)..."
python manage.py seed_data

echo "Zaganjam Gunicorn aplikacijski strežnik..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

