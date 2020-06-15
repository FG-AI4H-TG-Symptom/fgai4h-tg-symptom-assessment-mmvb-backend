[back](../README.md)

## General Tips

### Migrations
It is always useful to run `make apply_migrations` after you checked out code from someone, as the data models/schema might
have changed and you need to persist them. **Make sure mysql is running before trying to apply migrations**

If/when you implement a new data model, you need to run:
```
$ python manage.py makemigrations
$ python manage.py migrate
```

to generate the schema changes and apply them to the database.

### Celery
If you need to implement new celery tasks for any of your Django installed apps (the ones listed under `INSTALLED_APPS` in the project `settings.py` module) you only need to:

  - Create (if not already created) a `tasks.py` module under the desired Django app directory (`cases` for example)
  - Follow the template shown below on your `tasks.py`:
  ```
  from celery import shared_task

  @shared_task
  def add(x, y):
      return x + y
  ```

Then you could simply import the `add` task somewhere in your code and run it and, if the celery worker server is up and running, your task would be executed.

For more details check the [celery docs](https://docs.celeryproject.org/en/4.4.2/django/first-steps-with-django.html).

### Fixtures
During the development of the project it is important to be able to have a common source of data to be used for testing/debugging and to easily load it into the database.

Having this in mind, there are some fixtures data within the `cases/fixtures` and `benchmarking_sessions/fixtures` directories with `CaseSet`, `Case`, and `BenchmarkingSession` objects' data. For loading it into your running database simply execute the following in the root folder of the project:
```
$ make load_fixtures
```
This command uses Django `loaddata` management command, bear in mind that every time that you run it (or when you run `make start_app`) the loaded data will be overwritten for those objects in the database, so any changes you have applied to them will be lost. For more information visit the Django project [documentation](https://docs.djangoproject.com/en/3.0/ref/django-admin/#loaddata).
