# Full Stack Ecommerce using Django

Full-Stack Django ecommerce project.

## Features

- Faker generate fakeproducts
- API support with Swagger and Redoc documentation
- Celery with Redis, Celery beat and Flower
- Docker-compose for Nginx, Gunicorn, PostgreSQL, Celery, Redis and etc.

## Steps to run it in local Env

### Pre

- [GTK-for-Windows-Runtime-Environment-Installer Public](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
- Database Pg
- redis server - windows [Install Redis on Windows](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/) - `redis-cli ping` for verification

---

1. Clone this repo.
2. Create you virtual env
3. Install Project Dependencies - `cd core` -->> `pip install -r requirements.txt`
4. Configure PostgreSQL Database

   - In the pg shell

   ```sql
   CREATE USER myuser WITH PASSWORD 'mypassword';
   CREATE DATABASE mydb OWNER myuser;
   GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
   ```

5. Create `.env` file in the root dir

6. Start your Database and redis server.

7. `python manage.py migrate`
8. `python manage.py fakeproducts`
9. `python manage.py collectstatic --noinput`
10. `python manage.py runserver`

## Steps to run it in container env (Docker)
