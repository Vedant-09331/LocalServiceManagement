# Local Service Management Platform

A Django-based web application for managing local services, bookings, and vendor profiles. Connect service providers with customers for seamless service booking and management.

## Features

- **Service Management**: Vendors can create and list services with descriptions, pricing, and images
- **Booking System**: Users can book services with date/time selection
- **Review & Ratings**: Customers can review and rate services
- **Vendor Profiles**: Detailed vendor profiles with verification status
- **Search & Filter**: Search services by name and category
- **User Authentication**: Custom user model with role-based access (Admin, Vendor, User)
- **Responsive Design**: Bootstrap 5 ui with crispy forms

## Tech Stack

- **Backend**: Django 6.0.2
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5 with Crispy Forms
- **Image Processing**: Pillow
- **Authentication**: Django custom user model

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LocalServiceManagement
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   
   # Windows
   env\Scripts\activate
   
   # macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Apply migrations**
   ```bash
   cd LocalServiceManagement
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Homepage: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
LocalServiceManagement/
├── LocalServiceManagement/    # Project settings
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI application
├── core/                     # User authentication app
│   ├── models.py            # Custom User model
│   ├── views.py             # Auth views
│   └── urls.py              
├── services/                # Service management app
│   ├── models.py            # Service, Review, Category models
│   ├── views.py             # Service views
│   ├── forms.py             # Service forms
│   └── urls.py              
├── bookings/                # Booking management app
│   ├── models.py            # Booking model
│   ├── views.py             # Booking views
│   └── urls.py              
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── navbar.html         # Navigation
│   ├── services/           # Service templates
│   ├── bookings/           # Booking templates
│   └── core/               # Auth templates
├── media/                  # User uploaded files
├── .env                    # Environment variables (create from .env.example)
├── manage.py              # Django management
└── requirements.txt       # Python dependencies
```

## Key Models

### User (core.models)
- Custom user model with email authentication
- Roles: admin, vendor, user
- Email, password, timestamps

### Service (services.models)
- Title, name, description, price
- Vendor relationship (ForeignKey to User)
- Image upload support
- Rating and rating count

### Review (services.models)
- Rating (1-5)
- Comment/feedback
- Related to Service and User

### Booking (bookings.models)
- Service and User references
- Booking date/time
- Status tracking (pending, confirmed, completed, cancelled)
- Address for service delivery

### VendorProfile (services.models)
- Extended vendor information
- Phone, address, experience level
- Verification status

## API Endpoints

### Services
- `GET /services/` - List all services with search
- `GET /services/detail/<id>/` - Service details
- `GET /services/vendor/` - Vendor's services (authenticated)
- `POST /services/add/` - Create service (authenticated, vendor)

### Bookings
- `GET /bookings/` - List bookings
- `POST /bookings/` - Create booking (authenticated)

## Development

### Create new migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Run tests
```bash
python manage.py test
```

### Create admin user
```bash
python manage.py createsuperuser
```

### Access Django admin
Navigate to http://127.0.0.1:8000/admin/ with admin credentials

## Configuration

### Secret Key
Change the `SECRET_KEY` in `.env` for production. Generate a new one:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Database
Update `DATABASE_URL` in `.env` to use PostgreSQL:
```
DATABASE_URL=postgres://user:password@localhost:5432/localservice
```

### Security Settings
For production, update in `.env`:
```
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

## Deployment

### Using Heroku
1. Install Heroku CLI
2. Add `Procfile`:
   ```
   web: gunicorn LocalServiceManagement.wsgi
   ```
3. Deploy:
   ```bash
   heroku create
   heroku config:set DEBUG=False SECRET_KEY=<new-key>
   git push heroku main
   ```

### Using Docker
Create `Dockerfile` for containerization (optional)

## Troubleshooting

### Port already in use
```bash
python manage.py runserver 8001
```

### Database errors
```bash
python manage.py migrate --run-syncdb
```

### Static files issues
```bash
python manage.py collectstatic
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT License - feel free to use in your projects

## Support

For issues or questions, please create an issue in the repository.

## Roadmap

- [ ] Payment integration (Stripe/PayPal)
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Admin dashboard with analytics
- [ ] Mobile app
- [ ] Real-time notifications
- [ ] Service categories and subcategories
- [ ] Advanced search and filters
