# social-medial-api


## How tu run:
- Copy .evn.sample -> .env and populate with all required data
- `docker compose up --build`
- `docker compose exec web python manage.py loaddata demo_full.json`
- Admin user: admin@admin.com
- `docker compose exec web python manage.py changepassword admin`

## Features

- User registration and authentication
- User profile management
- Follow / unfollow users
- Create, update and delete posts
- Like and unlike posts
- Scheduled post publishing with Celery

## Documentation
Swagger:
http://localhost:8000/api/doc/swagger/