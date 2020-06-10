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
