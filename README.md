Installation
====================

```
$ pipenv install --dev
```

Setup backend
====================

```
$ cd backend_site
$ pipenv run python manage.py migrate
$ pipenv run python manage.py loaddata app.json
```

Setup frontend
====================

```
$ cd frontend_site
$ pipenv run python manage.py migrate
$ pipenv run python manage.py loaddata app.json
```

Start demo
====================

Run the backend server:

```
$ pipenv run ./backend_site/runserver.sh
```

and run the frontend servers (for both public and preview sites):

```
$ pipenv run ./frontend_site/runservers.sh
```

Visit the public site at http://localhost:8000/blog/ and the preview
site at http://localhost:8001/blog/ .

You can edit pages through the backend's wagtail admin interface at
http://localhost:18000/admin/ .
Log into the admin with the credentials `admin` / `changeme`.

Visit the admin site for frontend servers at
http://localhost:8000/admin/ to manage your templates.
The credentials are `admin` / `changeme` as well.

