# Django Swifty

Django Swifty is a powerful Django package that simplifies and enhances your Django development experience. It integrates various functionalities, including database management, caching, authentication, logging, and more, to streamline the development process.

## Installing the Package in Another Django Project

To install the Django Swifty package in another Django project, follow these steps:

1. **Install the package**:

   ```bash
   pip install django_swifty
   ```

2. **Add to INSTALLED_APPS**: After installation, add "django_swifty" to your `INSTALLED_APPS` setting in your Django project's `settings.py` file:

   ```python
   INSTALLED_APPS = [
       ...
       "swifty",
   ]
   ```

3. **Run migrations**: If the package includes any database models, run the following command to apply migrations:

   ```bash
   python manage.py migrate
   ```

## Features

- **Seamless Django Integration**: Works out of the box with your Django projects.
- **Easy Configuration**: Minimal setup required.
- **Performance Optimized**: Built with performance in mind.
- **Customizable**: Flexible settings to match your needs.

### Database Management

- **SQLAlchemy Integration**:
  - Utilizes SQLAlchemy for ORM (Object-Relational Mapping) with session management and transaction handling.
  - Provides a robust way to interact with SQL databases, allowing for complex queries and data manipulation.
- **MongoDB Connector**:
  - A dedicated connector for MongoDB that allows seamless interaction with MongoDB databases.
  - Supports connection management and CRUD operations.

### Caching

- **Redis Caching**:

  - Implements caching using Redis to improve application performance by storing frequently accessed data in memory.
  - Supports various caching strategies, including method-level caching and memoization.

- **Cache Management**:
  - Provides a cache manager for setting, getting, and deleting cache entries, making it easy to manage cached data.

### Authentication and Authorization

- **JWT Authentication**:
  - Supports JSON Web Tokens (JWT) for secure user authentication, allowing for token-based authentication that is stateless and scalable.
- **Custom Permissions**:
  - Implements a permission system that checks user attributes against allowed values, controlling access to resources based on user roles and permissions.

### Logging

- **Structured Logging**:
  - Uses `structlog` for structured logging, allowing for better log management and analysis.
  - Integrates logging with various components, providing detailed logs for debugging and monitoring.

### Utilities

- **Path Parsing Utilities**:

  - Provides utility functions for parsing nested data structures using path expressions, making it easier to access deeply nested data.

- **Custom Decorators**:
  - Includes decorators for caching and ensuring methods are only called once per instance, enhancing code efficiency and readability.

### ViewSets

- **Django REST Framework Integration**:
  - Integrates with Django REST Framework to provide a structured way to create APIs.
  - Includes custom viewsets that handle requests, responses, and error handling, making it easier to build RESTful services.

## Requirements

- Python 3.6+
- Django 2.2+
- setuptools
- wheel

## Configuration

### Database Configuration

Configure your database settings in the `settings.py` file:

```python
# Example for SQLAlchemy
DB_URL = 'sqlite:///your_database.db'  # Change to your database URL
```

For MongoDB, set the connection URL:

```python
MONGO_URL = 'mongodb://localhost:27017/your_database'
```

### Caching Configuration

Configure Redis caching in the `settings.py` file:

```python
REDIS_CONNECTION_POOL = {
    'pool_1': {
        'host': 'localhost',
        'port': 6379,
        'db': 1,
    }
}
```

### JWT Authentication

Set up JWT authentication settings:

```python
JWT_AUTH = {
    'JWT_SECRET_KEY': 'your_secret_key',
    'JWT_ALGORITHM': 'HS256',
    'JWT_EXPIRATION_DELTA': timedelta(days=1),
}
```

### Logging Configuration

Configure logging settings in the `settings.py` file:

```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

### ViewSet, Authentication and Authorization Example

To use JWT authentication and custom permissions from Django Swifty, you can define your permissions and apply them in your viewsets:

```python
from swifty.auth.permissions import SwiftyPermission
from swifty.viewsets.viewsets import SwiftyViewSet
from .models import YourModel
from .serializers import YourModelSerializer


class YourCustomPermission(SwiftyPermission):
    permission_layers = [
        {"path": "role", "allowed": ["admin", "superuser"]},
    ]


class YourModelViewSet(SwiftyViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    permission_classes = [YourCustomPermission]  # Apply custom permission

    def perform_create(self, serializer):
        ...
```

## Documentation

For detailed documentation, please visit our [documentation page](https://django-swifty.readthedocs.io/).

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Phuc Le** - _Initial work_ - [Github](https://github.com/hphuc3005)

## Acknowledgments

- Thanks to the Django community for inspiration
- All the contributors who have helped with the project
- Special thanks to [list any special acknowledgments]

---

Made with ❤️ by the Django Swifty Team
