# Full Stack Ecommerce using Django

Full-Stack Django ecommerce project.

## Features

- Faker generate fakeproducts
- API support with Swagger and Redoc documentation
- Celery with Redis, Celery beat and Flower
- Docker-compose for Nginx, Gunicorn, PostgreSQL, Celery, Redis and etc.

## Steps to run it in local Env

### Prerequisite

- Install [GTK-for-Windows-Runtime-Environment-Installer Public](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
- Install PostgreSQL Database (PgAdmin 14)
- To install Redis on Windows, you'll first need to enable [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
- Now, [Install Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/) Server on **WSL2**.

---

### 1. Clone this repo.

```sh
git clone https://github.com/faizan35/fullstack-ecommerce.git
```

### 2. Create you virtual env

- This is for windows, Execute there incide cmd.

```sh
cd fullstack-ecommerce

pip install virtualenv

python -m venv myenv
myenv\Scripts\activate
```

### 3. Install Project Dependencies

- Same, in cmd terminal

```sh
cd core

pip install -r requirements.txt
```

### 4. Configure PostgreSQL Database

- Inside SQL Shell **(psql)**

```sql
CREATE USER myuser WITH PASSWORD 'mypassword';
CREATE DATABASE mydb OWNER myuser;
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
```

### 5. Create `.env` file in the root dir

```txt
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_HOST=localhost

EMAIL_HOST_SENDER=my_fake_email@email.com
EMAIL_HOST_APP_PASSWORD=fake_pass

STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_API_VERSION=
STRIPE_WEBHOOK_SECRET=

YOOKASSA_SECRET_KEY=actualyourdata
YOOKASSA_SHOP_ID=actualyourdata

CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

> Copy all this inside the env file, Only env values you need is of Stripe's.
> We are NOT using YOOKASSA in this project.

#### How to find Strip's env values

- `STRIPE_PUBLISHABLE_KEY`: Can find in the Stripe Dashboard.

- `STRIPE_SECRET_KEY`: Can find in the Stripe Dashboard.

- `STRIPE_API_VERSION`: Can find in the Stripe Dashboard.

- `STRIPE_WEBHOOK_SECRET`: [Find Webhook](./Stripe-Setup/webhook.md)

### 6. Start your Database and Redis Server.

#### Database

- Open your UI of Database

#### Redis Server

```sh
sudo service redis-server start
```

or

```sh
sudo systemctl start redis-server
```

- `redis-cli ping` for verification, You will get `PONG` if it working.

### 7. Start your Stripe CLI WebHook

- Navigate to the dir where you have installed stripe cli.
- Open cmd in that path and execute

```sh
stripe listen --forward-to localhost:8000/payment/stripe-webhook/
```

### 8. Execute these commands one by one

```sh
python manage.py migrate

python manage.py fakeproducts

python manage.py runserver
```

### 8. You E-comm Web App would be running on:

- [http://127.0.0.1:8000/shop/](http://127.0.0.1:8000/shop/)

---

## Steps to run it in container env (Docker)
