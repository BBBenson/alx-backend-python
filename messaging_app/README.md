# Messaging App API

A Django REST API for messaging functionality with JWT authentication, conversation management, and message filtering capabilities.

## Quick Start with Docker Compose

The fastest way to get the application running is with Docker Compose:

### Prerequisites

- Docker Engine installed ([Installation Guide](https://docs.docker.com/engine/install/))
- Docker Compose installed (usually included with Docker Desktop)

### Data Persistence

The application uses Docker volumes to ensure data persistence:

- **Database data**: Stored in `mysql_data` volume (persists across container restarts)
- **Static files**: Stored in `static_volume` volume
- **Media files**: Stored in `media_volume` volume

These volumes are preserved even when containers are stopped. To completely remove data, use `docker-compose down -v`.

### Setup Instructions

1. **Clone the repository and navigate to the project directory**:

    ```bash
    git clone <repository-url>
    cd messaging_app
    ```

2. **Set up environment variables**:

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file with your preferred database credentials and settings.

3. **Build and start the services**:

    ```bash
    docker-compose up --build
    ```

   This will:
   - Build the Django application image
   - Start a MySQL database container
   - Apply database migrations
   - Create a superuser (admin) account
   - Start the development server on `http://localhost:8000`

4. **Access the application**:
   - API: `http://localhost:8000/api/v1/`
   - Admin Panel: `http://localhost:8000/admin/`
   - Default admin credentials: `admin` / `admin123`

5. **Stop services when done**:

    ```bash
    docker-compose down
    ```

### Docker Commands

```bash
# Build only the web service
docker-compose build web

# Start services in detached mode
docker-compose up -d

# View logs
docker-compose logs web
docker-compose logs db

# Execute commands in running container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser

# Stop and remove containers, networks, and volumes
docker-compose down -v
```

## Manual Setup (Alternative)

If you prefer to set up the development environment manually:

### Prerequisites (Python)

- Python 3.12+
- PostgreSQL 17+
- pip (Python package installer)

### Installation Steps

1. **Create a virtual environment**:

    ```bash
    python -m venv .venv
    ```

2. **Activate the environment**:

    ```bash
    source .venv/scripts/activate  # Windows
    source .venv/bin/activate     # MacOS/Linux
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up PostgreSQL database** and create a database named `messaging_app_db`

5. **Environment Configuration**:

    ```bash
    cp .env.docker .env
    # Edit .env file with your database credentials
    ```

6. **Apply migrations**:

    ```bash
    python manage.py migrate
    ```

7. **Create test data**:

    ```bash
    python manage.py create_test_data
    ```

8. **Create admin user**:

    ```bash
    python manage.py createsuperuser
    ```

9. **Start development server**:

    ```bash
    python manage.py runserver
    ```

## MySQL Setup Instructions

### Prerequisites (MySQL)

- MySQL Server installed ([Installation Guide](https://dev.mysql.com/doc/refman/8.0/en/installing.html))
- MySQL Client installed ([Installation Guide](https://dev.mysql.com/doc/refman/8.0/en/installing.html))

### Setup Instructions (MySQL)

1. **Create a new MySQL database**:

    ```sql
    CREATE DATABASE messaging_app;
    ```

2. **Create a new MySQL user**:

    ```sql
    CREATE USER 'messaging_user'@'%' IDENTIFIED BY 'your-secure-password';
    ```

3. **Grant privileges to the new user**:

    ```sql
    GRANT ALL PRIVILEGES ON messaging_app.* TO 'messaging_user'@'%';
    ```

4. **Apply database migrations**:

    ```bash
    python manage.py migrate
    ```

5. **Create test data**:

    ```bash
    python manage.py create_test_data
    ```

6. **Create admin user**:

    ```bash
    python manage.py createsuperuser
    ```

7. **Start development server**:

    ```bash
    python manage.py runserver
    ```

## Environment Configuration

### Docker Environment (.env.docker)

For Docker setup, use the provided `.env.docker` template:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DB_NAME=messaging_app_db
DB_USER=messaging_user
DB_PASSWORD=messaging_pass
DB_HOST=db
DB_PORT=5432
```

### Local Development Environment

For manual setup, create `.env` file:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=your_local_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

## Dependencies

- Django 5.2.4+
- Django REST Framework 3.16.0+
- djangorestframework-simplejwt (JWT Authentication)
- django-environ (for environment variables)
- django-filter (for API filtering)
- psycopg (PostgreSQL adapter)
- python-dateutil (for date handling)
- mysqlclient (MySQL adapter)

## Project Structure

```text
messaging_app/
├── .venv/                 # Virtual environment
├── chats/                 # Messaging app
│   ├── migrations/        # Database migrations
│   ├── management/        # Custom management commands
│   ├── __init__.py
│   ├── admin.py           # Admin panel config
│   ├── apps.py
│   ├── models.py          # Data models
│   ├── permissions.py     # Custom permissions
│   ├── serializers.py     # API serializers
│   ├── urls.py            # API endpoints
│   └── views.py           # View logic
├── messaging_app/         # Project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py
├── .env.docker            # Docker environment template
├── .dockerignore          # Docker ignore file
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── entrypoint.sh          # Docker entrypoint script
├── .gitignore
├── manage.py
├── README.md              # Project documentation
└── requirements.txt       # Dependencies file
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Obtaining Tokens

1. **Get Access Token**:

    ```bash
    POST /api/v1/token/
    {
      "username": "your_username",
      "password": "your_password"
    }
    ```

2. **Using the Token**:
   Include the token in the Authorization header:

    ```bash
    Authorization: Bearer your_token_here
    ```

3. **Refresh Token**:

    ```bash
    POST /api/v1/token/refresh/
    {
      "refresh": "your_refresh_token_here"
    }
    ```

## Permissions

- **IsAuthenticated**: Required for all API endpoints
- **IsParticipantOfConversation**: Users must be participants to view/modify conversations
- **IsMessageOwnerOrReadOnly**: Only message owners can edit/delete their messages
- **IsAdminUser**: Required for admin interface access

## API Endpoints

### Token Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/token/` | POST | Obtain JWT token (access + refresh) |
| `/token/refresh/` | POST | Get new access token using refresh token |
| `/token/verify/` | POST | Verify a token |

### Users

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/users/` | POST | Register new user | AllowAny |
| `/users/me/` | GET | Get current user's profile | IsAuthenticated |
| `/users/{id}/` | GET | Get user details | IsOwner or IsStaff |
| `/users/{id}/` | PATCH | Update user details | IsOwner or IsStaff |

### Conversations

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/conversations/` | GET | List user's conversations | IsAuthenticated |
| `/conversations/` | POST | Create new conversation | IsAuthenticated |
| `/conversations/{id}/` | GET | Get conversation details | IsParticipant |
| `/conversations/{id}/messages/` | GET | List messages | IsParticipant |
| `/conversations/{id}/messages/` | POST | Send new message | IsParticipant |

### Messages

#### List Messages in a Conversation

```http
GET /api/v1/conversations/{conversation_id}/messages/
```

**Pagination**:

- Returns 20 messages per page by default
- Use `page` parameter to navigate through pages
- Customize page size with `page_size` parameter (max 100)

**Filtering**:

- `sender`: Filter by sender ID or username
- `start_date`: Filter messages sent after this date (YYYY-MM-DD HH:MM:SS)
- `end_date`: Filter messages sent before this date (YYYY-MM-DD HH:MM:SS)
- `search`: Search in message content (case-insensitive)

**Sorting**:

- Use `ordering` parameter with:
  - `sent_at` (ascending)
  - `-sent_at` (descending, default)
  - `sender__username` (alphabetical by sender)
  - `-sender__username` (reverse alphabetical by sender)

**Example Request**:

```bash
# Get first page of messages from conversation 1, ordered by most recent
GET /api/v1/conversations/{conversation_id}/messages/

# Get second page with 10 messages per page
GET /api/v1/conversations/{conversation_id}/messages/?page=2&page_size=10

# Filter messages from a specific sender
GET /api/v1/conversations/{conversation_id}/messages/?sender=kwame

# Search for messages containing "hello"
GET /api/v1/conversations/{conversation_id}/messages/?search=hello

# Get messages from a date range
GET /api/v1/conversations/{conversation_id}/messages/?start_date=2025-07-01&end_date=2025-07-23

# Combine filters
GET /api/v1/conversations/{conversation_id}/messages/?sender=kwame&start_date=2025-07-01&search=hello
```

## Testing the API

### Docker Environment

With Docker running, you can test the API:

```bash
# Get token for test user 'kwame'
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kwame", "password": "testpass123"}'

# Use the returned token to access protected endpoints
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/conversations/
```

### Test Data

Pre-created test users (available after running `create_test_data` command):

1. **Kwame Mensah**
   - Username: `kwame`
   - Password: `testpass123`

2. **Ama Agyei**
   - Username: `ama`
   - Password: `testpass123`

3. **Kofi Asante**
   - Username: `kofi`
   - Password: `testpass123`

**Note**: Kwame and Ama share a conversation with test messages in Twi.

## Testing Permissions

### 1. Unauthenticated Access (401)

```bash
curl -X GET http://localhost:8000/api/v1/conversations/
# Should return 401 Unauthorized
```

### 2. Non-Participant Access (403)

```bash
# Get Kofi's token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kofi", "password": "testpass123"}' | jq -r '.access')

# Try to access Kwame and Ama's conversation
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/conversations/1/
# Should return 403 Forbidden
```

## Admin Interface

Access the admin interface at `http://localhost:8000/admin/` using admin credentials.

### Default Admin Credentials (Docker)

- **Username**: `admin`
- **Password**: `admin123`

### Admin Features

- User management (create, edit, delete users)
- View all conversations
- Monitor messages
- User role management

## Development

### Creating Migrations

```bash
# In Docker environment
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# In manual setup
python manage.py makemigrations
python manage.py migrate
```

### Running Tests

```bash
# In Docker environment
docker-compose exec web python manage.py test

# In manual setup
python manage.py test
```

### Accessing Django Shell

```bash
# In Docker environment
docker-compose exec web python manage.py shell

# In manual setup
python manage.py shell
```

## Production Deployment

### Docker Production Setup

1. **Create production Docker Compose file** (`docker-compose.prod.yml`):
   - Use production-ready PostgreSQL configuration
   - Set proper environment variables
   - Configure nginx for static file serving
   - Use gunicorn instead of development server

2. **Security Considerations**:
   - Use secure `SECRET_KEY`
   - Set `DEBUG=False`
   - Configure proper `ALLOWED_HOSTS`
   - Use SSL/TLS certificates
   - Implement proper backup strategies

3. **Environment Variables**:
   - Use Docker secrets or external secret management
   - Never commit production credentials to version control

## Troubleshooting

### Common Docker Issues

1. **Port Already in Use**:

   ```bash
   # Change port in docker-compose.yml or stop conflicting service
   docker-compose down
   sudo lsof -i :8000  # Find what's using port 8000
   ```

2. **Database Connection Issues**:

   ```bash
   # Check if PostgreSQL container is running
   docker-compose logs db
   # Restart services
   docker-compose restart
   ```

3. **Permission Issues**:

   ```bash
   # Fix file permissions (Linux/macOS)
   sudo chown -R $USER:$USER .
   ```

4. **Container Build Issues**:

   ```bash
   # Clear Docker cache and rebuild
   docker-compose down -v
   docker system prune -a
   docker-compose up --build
   ```

### Common Development Issues

1. **Migration Issues**:

   ```bash
   # Reset migrations (development only)
   docker-compose exec web python manage.py migrate --fake-initial
   ```

2. **Static Files Not Loading**:

   ```bash
   # Collect static files
   docker-compose exec web python manage.py collectstatic
   ```

## Security Considerations

- Always use HTTPS in production
- Tokens expire after 1 hour (configurable in settings)
- Refresh tokens expire after 1 day
- Passwords are hashed before storage
- Admin interface is protected by `IsAdminUser`
- Rate limiting recommended for authentication endpoints
- Use proper secrets management in production
- Regular security audits and dependency updates

## Performance Optimization

- Database query optimization with `select_related`/`prefetch_related`
- Implement Redis caching for production
- Use CDN for static file delivery
- Database connection pooling
- Implement API rate limiting
- Monitor with APM tools (Sentry, New Relic)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the ALX ProDEV Curriculum.
