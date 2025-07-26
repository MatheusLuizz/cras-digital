# CRAS Digital

A comprehensive digital platform for managing social assistance services at CRAS (Centro de Referência de Assistência Social) centers. This Django-based application provides appointment scheduling, service management, user administration, and support features for social workers and beneficiaries.

## Project Purpose

CRAS Digital aims to modernize and digitize the social assistance service management process, providing:

- **Appointment Management**: Schedule and track appointments between beneficiaries and social workers
- **Service Catalog**: Manage available social services and their locations
- **User Management**: Handle beneficiary profiles with vulnerability indicators and CadÚnico integration
- **Location Management**: Organize CRAS centers and their service offerings
- **Support System**: Provide assistance and support features for users
- **Authentication**: Secure user authentication and authorization system

## Features

- **RESTful API**: Complete API for frontend integration
- **Admin Interface**: Django admin with Jazzmin theme for easy management
- **User Profiles**: Extended user profiles with social vulnerability indicators
- **Appointment Scheduling**: Full appointment lifecycle management
- **Service Management**: Comprehensive service catalog with duration and location tracking
- **Document Management**: File upload capabilities for user documents
- **Multi-location Support**: Manage multiple CRAS centers
- **Production Ready**: Deployed on Fly.io with PostgreSQL database

## Technology Stack

- **Backend**: Django 5.2 with Django REST Framework
- **Database**: PostgreSQL with psycopg2
- **Authentication**: JWT-based authentication
- **API Documentation**: Swagger/OpenAPI with drf-yasg
- **Admin Interface**: Django Jazzmin
- **Deployment**: Docker with Fly.io
- **Testing**: Django test framework with coverage
- **Code Quality**: Flake8, pre-commit hooks

## Prerequisites

- Python 3.10+
- PostgreSQL
- Docker (optional, for containerized deployment)
- Git

## Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cras_digital
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgres://username:password@localhost:5432/cras_digital
   ```

5. **Set up the database**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### API Endpoints

The application provides RESTful API endpoints for all major features:

#### Authentication
- `POST /api/v1/authentication/token/` - User login
- `POST /api/v1/authentication/refresh/` - Refresh JWT token
- `POST /api/v1/authentication/logout/` - User logout

#### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - Get user details
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

#### Appointments
- `GET /api/v1/appointments/` - List appointments
- `POST /api/v1/appointments/` - Create appointment
- `GET /api/v1/appointments/{id}/` - Get appointment details
- `PUT /api/v1/appointments/{id}/` - Update appointment
- `DELETE /api/v1/appointments/{id}/` - Cancel appointment

#### Services
- `GET /api/v1/services/` - List available services
- `POST /api/v1/services/` - Create service
- `GET /api/v1/services/{id}/` - Get service details
- `PUT /api/v1/services/{id}/` - Update service
- `DELETE /api/v1/services/{id}/` - Delete service

### Admin Interface

Access the admin interface at `https://cras-digital.fly.dev/admin/` to manage:
- Users and user profiles
- Appointments and their status
- Available services
- CRAS locations
- Support tickets

### Example API Usage

```python
import requests

# Login and get token
response = requests.post('https://cras-digital.fly.dev/api/v1/authentication/token/', {
    'username': 'your_username',
    'password': 'your_password'
})
token = response.json()['access']

# Create an appointment
headers = {'Authorization': f'Bearer {token}'}
appointment_data = {
    'date': '2024-01-15',
    'time': '14:00:00',
    'description': 'Social assistance consultation'
}
response = requests.post('https://cras-digital.fly.dev/api/v1/appointments/', 
                        json=appointment_data, headers=headers)
```

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run tests with coverage
python run_tests.bat  # Windows
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Deployment

### Fly.io Deployment

The application is configured for deployment on Fly.io:

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly**
   ```bash
   fly auth login
   ```

3. **Deploy the application**
   ```bash
   fly deploy
   ```

The application will be available at `https://cras-digital.fly.dev`

### Environment Variables for Production

Set the following environment variables in your production environment:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgres://username:password@host:port/database
```

## Project Structure

```
cras_digital/
├── apps/
│   ├── authentication/     # JWT authentication
│   ├── users/              # User management and profiles
│   ├── appointments/       # Appointment scheduling
│   ├── services/           # Service catalog
│   ├── support/            # Support system
│   └── cras_locations/     # CRAS center management
├── cras_digital/           # Django project settings
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── fly.toml                # Fly.io deployment config
└── manage.py               # Django management script
```

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   python manage.py test
   ```
5. **Check code quality**
   ```bash
   flake8 .
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add: description of your changes"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

### Code Style

- Follow Flake8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new features
- Update documentation as needed

### Pre-commit Hooks

The project uses pre-commit hooks to maintain code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

1. Check the [Issues](https://github.com/your-repo/cras_digital/issues) page
2. Create a new issue for bugs or feature requests
3. Contact the development team

## Version History

- **v1.0.0** - Initial release with core CRAS functionality
- **v1.1.0** - Added appointment management and user profiles
- **v1.2.0** - Enhanced admin interface and API documentation

## Acknowledgments

- Django community for the excellent framework
- Fly.io for hosting infrastructure
- All contributors and social workers who provided feedback

---

**Note**: This is a digital transformation project for social assistance services. Please ensure compliance with local data protection regulations and social service guidelines when deploying in production environments.