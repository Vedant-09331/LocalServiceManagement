# Local Service Management Platform

A full-stack Django web application for managing local home services, bookings, payments, and vendor profiles. Connect service providers with customers for seamless service booking, cart-based checkout, and AI-powered assistance.

## ✨ Features

### Core
- **Service Management**: Vendors can create and list services with descriptions, pricing, and images
- **Booking System**: Users can book services with date/time selection
- **Review & Ratings**: Customers can review and rate services (1–5 stars)
- **Vendor Profiles**: Detailed vendor profiles with verification status
- **Search & Filter**: Live search services by name and category
- **User Authentication**: Custom user model with role-based access (Admin, Vendor, User)
- **Favorites**: Users can save services to a favorites list

### 🛒 Cart & Razorpay Payments
- Add multiple services to a cart with quantity controls
- Order summary with total calculation
- **Razorpay integration** for secure online payments
- Automatic booking creation upon successful payment
- Payment verification with Razorpay signature validation

### 💬 Chat Module (Booking-Restricted)
- Real-time messaging between users and vendors
- **Access restricted**: Users can only chat with vendors they have booked services from
- AJAX-based message sending with polling for new messages
- Premium chat UI with gradient bubbles and timestamps

### 🤖 Gemini AI Chatbot
- Floating chatbot widget on every page (for authenticated users)
- Powered by **Google Gemini** via the `google-genai` SDK
- Context-aware: queries live service and booking data from the database
- 3 quick-action suggestions:
  - 🔍 Find services
  - 📋 Check booking status
  - 💰 Show cheapest services

### 🖼️ Image Deduplication
- MD5-hash based deduplication prevents storing duplicate image files
- Optimized for Cloudinary storage on free-tier deployments

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.2 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Bootstrap 5, Crispy Forms, Font Awesome |
| Payments | Razorpay |
| AI | Google Gemini (`google-genai`) |
| Static Files | WhiteNoise |
| Deployment | Render |

## Installation

### Prerequisites
- Python 3.10+
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

4. **Configure environment variables**

   Create a `.env` file inside the `LocalServiceManagement/` subdirectory:

   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key

   # Database (optional — defaults to local PostgreSQL)
   DATABASE_URL=postgresql://user:pass@host:5432/dbname

   # Razorpay
   RAZORPAY_KEY_ID=rzp_test_xxxxx
   RAZORPAY_KEY_SECRET=your_secret

   # Gemini AI
   GEMINI_API_KEY=your_gemini_api_key

   # Email
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password

   # Cloudinary (Required for Free Tier deployment)
   CLOUDINARY_STORAGE_NAME=your_cloud_name
   CLOUDINARY_STORAGE_API_KEY=your_api_key
   CLOUDINARY_STORAGE_API_SECRET=your_api_secret
   ```

5. **Apply migrations**
   ```bash
   cd LocalServiceManagement
   python manage.py makemigrations
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
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                      # User authentication
├── services/                  # Service management & image dedup
├── bookings/                  # Booking management
├── payments/                  # Razorpay payment processing
├── cart/                      # Shopping cart & checkout
├── chat/                      # User-Vendor messaging
├── chatbot/                   # Gemini AI assistant
├── vendors/                   # Vendor profiles
├── professionals/             # Professional profiles
├── templates/                 # HTML templates
├── media/                     # User uploaded files
├── manage.py
└── requirements.txt
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DEBUG` | `True` for development |
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `RAZORPAY_KEY_ID` | Razorpay API key |
| `RAZORPAY_KEY_SECRET` | Razorpay secret |
| `GEMINI_API_KEY` | Google Gemini API key |
| `CLOUDINARY_STORAGE_NAME` | Cloudinary Cloud Name |
| `CLOUDINARY_STORAGE_API_KEY` | Cloudinary API Key |
| `CLOUDINARY_STORAGE_API_SECRET` | Cloudinary API Secret |
| `EMAIL_HOST_USER` | SMTP email address |
| `EMAIL_HOST_PASSWORD` | SMTP app password |

## Deployment (Render - Free Tier)

> **Important**: Render's free tier has an ephemeral filesystem. To persist images, you **must** configure the Cloudinary environment variables.

1. Create a free account at [Cloudinary](https://cloudinary.com)
2. Set all environment variables (PostgreSQL, Razorpay, Gemini, Cloudinary) in the Render dashboard
3. Build command: `pip install -r requirements.txt && cd LocalServiceManagement && python manage.py collectstatic --noinput && python manage.py migrate`
4. Start command: `cd LocalServiceManagement && gunicorn LocalServiceManagement.wsgi`
5. After deployment, run `python manage.py seed_data` from the Render Shell to populate your database.

## License

MIT License — feel free to use in your projects.
