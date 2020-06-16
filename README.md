# Social Network Demo

Simple Blog engine. Was made as a test task. [Technical specification](TASK.md)

## Requirements
Demo website uses default Django SQLite connector. 
Redis required.  

## Install
```commandline
git clone https://github.com/ravique/social-network-demo.git
cd sn_test_task
pip install -r requirements.txt
```

then add `.env` to the `social_network` folder.

example:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
JWT_SIGNING_KEY=abc
DEBUG=True
```

To perform migrations:
```commandline
python manage.py migrate
```

## API Reference

## Registration and login

### Registration: `/api/register/` – POST
Required fields: `username, password`
Returns: User account data

**Example**
```json
{
"username": "sammy",
"password": 12345678,
}
```

### Login `/api/login/` – POST

Required fields: `username, password`
Returns: JWT and Refresh tokens.

_ACCESS_TOKEN_LIFETIME is set to 30 minutes and REFRESH_TOKEN_LIFETIME to 30 days for demonstration reasons._ 

**Example**
```json
{
"username": "sammy",
"password": 12345678
}
```

## Entities (all resources are available for authenticated users only)

### Post creation `/api/post/` – POST
Returns list of courses.

### Post detail `/api/post/<id>/` – GET
Returns detailed information about post.

### Post list `/api/post/<id>/` – GET
Returns paginated list of posts.

### Post list `/api/post/<id>/like` – POST
Endpoint to like post

### Post list `/api/post/<id>/dislike` – POST
Endpoint to dislike post

### User statistics `/api/user/<id>/` - GET
Returns user statistics: `id, username, last_login, last_request_moment`

### Like analytics `/api/like/analytics/` - GET
Returns likes analytics, grouped by day. Supports `date_from` and `date_to` GET parameters (work as `gte` and `lte`, format `YYYY-MM-DD`)

## Authors

* **Andrei Etmanov**

## License

This project is licensed under the MIT License – see the [LICENSE.md](LICENSE.md) file for details