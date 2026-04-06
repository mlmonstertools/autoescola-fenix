web: gunicorn autoescola.wsgi --log-file -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py setup_initial_data
