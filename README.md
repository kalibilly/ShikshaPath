# ShikshaPath - E-Learning Platform

ShikshaPath is a modern, scalable e-learning platform that enables instructors to create courses, upload content, and generate 3D animated educational videos. Students can enroll in courses, access learning materials, and track their progress.

## ✨ Features

### For Instructors
- 📚 **Create & Manage Courses** - Build structured courses with detailed descriptions
- 📹 **3D Animation Generation** - Generate 3D animated videos from course content
- 📤 **Content Upload** - Upload PDF, Word, PowerPoint, Excel, Text, and Video files
- 🎨 **Course Customization** - Organize content with sections and modules
- 📊 **Student Analytics** - Track student enrollment and progress (future feature)

### For Students
- 🎓 **Course Enrollment** - Browse and enroll in available courses
- 📖 **Learning Materials** - Access all course content and materials
- 🎥 **Watch Videos** - View generated 3D animated educational videos
- 👤 **User Profile** - Manage profile and learning preferences
- 🌈 **Theme Customization** - Choose from 10+ beautiful color themes

### For Everyone
- 🔐 **Secure Authentication** - Email/Password, Mobile OTP, Firebase Phone Auth
- 📧 **Email Verification** - Secure account creation with email verification
- 🌍 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast Performance** - Optimized for speed with Tailwind CSS
- 🌙 **Dark Mode Support** - Beautiful dark and light theme options

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2.7
- **Language**: Python 3.12
- **Database**: PostgreSQL (production) / SQLite (development)
- **Task Queue**: Celery + Redis
- **Authentication**: Django Auth + Firebase Admin + Custom OTP

### Frontend
- **Styling**: Tailwind CSS 3
- **Icons**: Font Awesome 6.0
- **Interactive Elements**: Alpine.js (if needed)
- **Templates**: Django Templates

### APIs & Services
- **REST API**: Django REST Framework
- **Firebase**: Phone authentication, Firestore database
- **Email Service**: Django Mail (configurable)

### File Processing
- **PDF**: PyPDF2
- **Word Documents**: python-docx
- **Images**: Pillow
- **Videos**: ffmpeg-python, moviepy, imageio

### DevOps & Deployment
- **Web Server**: Gunicorn
- **Static Files**: Whitenoise
- **Hosting**: Render.com (recommended), Heroku, AWS
- **Database**: PostgreSQL (Render, ElephantSQL, AWS RDS)

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/shikshapath.git
   cd shikshapath/shikshapath
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate      # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Homepage: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - Register new account or login with superuser

## 📦 Installation & Dependencies

All dependencies are listed in `requirements.txt`:

**Core**: Django, asgiref, sqlparse
**Database**: psycopg2-binary, dj-database-url, PyMySQL
**Authentication**: PyJWT, cryptography, bcrypt, firebase-admin
**File Processing**: PyPDF2, python-docx, Pillow
**Video Processing**: ffmpeg-python, moviepy, imageio
**Async Tasks**: celery, redis, kombu
**APIs**: djangorestframework, django-cors-headers
**Production**: gunicorn, whitenoise

To install all packages:
```bash
pip install -r requirements.txt
```

## 🌐 Deployment Guide

### Deploy to Render (Recommended)

**Full instructions available in: `CLOUD_POSTGRES_SETUP.txt`**

#### Quick Steps:

1. **Create PostgreSQL Database on Render**
   - Go to https://render.com
   - Create new PostgreSQL database
   - Copy connection string

2. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   ```

3. **Create Web Service on Render**
   - Connect your GitHub repository
   - Set environment variables:
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `SECRET_KEY`: Django secret key
     - `DEBUG`: False
     - `ALLOWED_HOSTS`: your-domain.com,www.yourdomain.com

4. **Deploy**
   - Click "Deploy"
   - Wait 3-10 minutes for build completion
   - Visit your live site!

5. **Configure Custom Domain (Optional)**
   - Update DNS records
   - Add domain to Render
   - Wait for SSL certificate (5-10 minutes)

### Environment Variables Required

```
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**Optional (if configured)**:
```
FIREBASE_API_KEY=your-firebase-key
EMAIL_HOST_PASSWORD=your-email-password
STRIPE_API_KEY=your-stripe-key
```

## 📁 Project Structure

```
shikshapath/
├── accounts/                 # User authentication & profiles
│   ├── migrations/
│   ├── forms.py             # Registration, login, profile forms
│   ├── models.py            # CustomUser model
│   ├── views.py             # Auth views
│   ├── urls.py              # Auth URL routing
│   └── theme_views.py       # Theme switching functionality
├── courses/                 # Course management
│   ├── migrations/
│   ├── models.py            # Course, Instructor, Category models
│   ├── views.py             # Course CRUD operations
│   ├── forms.py             # Course forms
│   └── urls.py
├── video_generation/        # 3D Animation video generation
│   ├── migrations/
│   ├── models.py            # VideoGenerationTask model
│   ├── views.py             # Video generation logic
│   ├── forms.py             # Video generation form
│   └── urls.py
├── payments/                # Payment processing
│   ├── migrations/
│   ├── models.py            # Payment model
│   ├── views.py             # Payment views
│   └── urls.py
├── videos/                  # Video management
│   ├── migrations/
│   ├── models.py            # Video model
│   ├── views.py
│   └── urls.py
├── shikshapath/            # Project settings
│   ├── settings.py         # Django configuration
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── templates/              # HTML templates
│   ├── base.html           # Master template
│   ├── accounts/           # Auth templates
│   ├── courses/            # Course templates
│   ├── payments/           # Payment templates
│   └── videos/             # Video templates
├── static/                 # CSS, JavaScript, images
│   ├── animations.css      # Animation definitions
│   ├── themes.css          # Theme color definitions
│   ├── base.css            # Base styles
│   └── base.js             # JavaScript functionality
├── requirements.txt        # Project dependencies
├── manage.py              # Django management script
└── db.sqlite3            # SQLite database (development only)
```

## 🔐 Authentication Methods

### Email/Password Authentication
- Standard Django authentication
- Secure password hashing with bcrypt
- Email verification on signup

### Mobile OTP Authentication
- One-Time Password sent to mobile
- Time-based validation (10 minutes)
- Automatic OTP expiry

### Firebase Phone Authentication (Optional)
- Firebase Authentication integration
- Phone number verification
- One-time password via SMS

## 🎨 Theme System

Choose from 10+ beautiful themes:
- **Dark** (Default) - Professional dark theme
- **Gaming** - High contrast gaming-inspired
- **Purple** - Elegant purple tones
- **Ocean** - Calm blue ocean colors
- **Forest** - Natural green theme
- **Sunset** - Warm orange/red tones
- **Midnight** - Deep blue night theme
- **Cyber** - Futuristic cyan theme
- **Retro** - Vintage color palette
- **Minimal** - Clean minimalist theme

Themes are fully customizable in `static/themes.css`

## 🚨 Firebase Configuration

Firebase is optional. To enable:

1. Create Firebase project at https://console.firebase.google.com
2. Download service account key (JSON)
3. Create `firebase_config.py`:
   ```python
   FIREBASE_CONFIG = {
       "type": "service_account",
       "project_id": "your-project-id",
       "private_key_id": "...",
       # ... other Firebase credentials
   }
   ```

Without Firebase configuration, app uses standard email/password auth (fully functional).

## 📖 API Documentation

### REST API Endpoints

**Courses**:
- `GET /api/courses/` - List all courses
- `GET /api/courses/{id}/` - Get course details
- `POST /api/courses/` - Create course (instructor only)
- `PUT /api/courses/{id}/` - Update course
- `DELETE /api/courses/{id}/` - Delete course

**Videos**:
- `GET /api/videos/` - List videos
- `POST /api/videos/` - Upload video
- `GET /api/videos/{id}/` - Get video details

See `djangorestframework` documentation for full API details.

## 🧪 Testing

Run tests with:
```bash
# All tests
python manage.py test

# Specific app tests
python manage.py test accounts
python manage.py test courses
python manage.py test videos

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🔧 Configuration

### Django Settings

Key settings in `shikshapath/settings.py`:

```python
DEBUG = False                          # Always False in production
ALLOWED_HOSTS = ['yourdomain.com']    # Your domain
DATABASE_URL = os.environ.get('DATABASE_URL')  # From environment
SECRET_KEY = os.environ.get('SECRET_KEY')      # From environment
```

### Database Configuration

Automatically detects and uses:
- **PostgreSQL** if `DATABASE_URL` environment variable is set
- **SQLite** if no `DATABASE_URL` (local development)

### Static Files

In production, static files served by Whitenoise:
```bash
python manage.py collectstatic --noinput
```

## 📚 Documentation Files

- **`CLOUD_POSTGRES_SETUP.txt`** - Complete cloud deployment guide
- **`DEPLOYMENT_QUICK_START.txt`** - 30-minute fast deployment
- **`DEPLOYMENT_CHECKLIST.txt`** - Verification checklist
- **`RENDER_BUILD_FIX.txt`** - Fix PyPI package issues
- **`QUICK_FIX_GUIDE.txt`** - Quick action guide

## 🐛 Troubleshooting

### Firebase Warning
If you see Firebase warning on runserver:
- This only appears in DEBUG mode (development)
- Firebase is optional - app works fine without it
- To configure: Create `firebase_config.py` with credentials

### Database Connection Error
```
ERROR: could not connect to server
```
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL is running
- Test connection string with psql client

### Static Files Not Loading
```
GET /static/base.css 404 Not Found
```
- Run: `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify static files directory exists

### Build Failed on Render
```
ERROR: Could not find a version that satisfies the requirement
```
- Check `requirements.txt` has valid versions
- See `RENDER_BUILD_FIX.txt` for package version issues
- All packages must exist on PyPI

## 📈 Performance Tips

1. **Database Optimization**
   - Add database indexes for frequently queried fields
   - Use `select_related()` and `prefetch_related()` in queries
   - Cache database query results with Redis

2. **Static Files**
   - Compress CSS/JavaScript files
   - Use CDN (CloudFlare) for faster delivery
   - Enable browser caching headers

3. **Server**
   - Use appropriate `gunicorn` worker count
   - Enable GZIP compression
   - Monitor memory usage

4. **Images**
   - Optimize images before upload
   - Use responsive image sizes
   - Consider lazy loading for image galleries

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and commit: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

Created as an e-learning platform project for educational purposes.

## 📞 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check documentation files in repository
- Review Django/PostgreSQL documentation

## 🎯 Roadmap

### Completed ✅
- User authentication (email/password, OTP, Firebase)
- Course creation and management
- Content upload (PDF, Word, Excel, PowerPoint, Text, Video)
- 3D animation video generation
- Theme switching system (10+ themes)
- Responsive design
- Django admin panel
- Email verification
- User profiles

### Planned Features 🚀
- Student progress tracking
- Quiz and assessments
- Certificate generation
- Video streaming optimization
- Chat/messaging system
- Discussion forums
- Payment integration (Stripe)
- Social sharing
- Advanced analytics
- Mobile app (React Native)

## 📊 Project Statistics

- **Lines of Code**: 5000+
- **Models**: 10+
- **Views**: 30+
- **Templates**: 20+
- **Apps**: 6
- **Dependencies**: 48 packages
- **Deployment Ready**: ✅ Yes

## 🌟 Acknowledgments

- Django Community
- Tailwind CSS
- Font Awesome
- Firebase
- All contributors and testers

---

## Getting Started

1. **Clone**: `git clone https://github.com/yourusername/shikshapath.git`
2. **Setup**: Follow "Quick Start" section above
3. **Deploy**: See `CLOUD_POSTGRES_SETUP.txt` for deployment
4. **Customize**: Modify settings and themes as needed
5. **Enjoy**: Your e-learning platform is ready!

---

**Happy Learning! 🎓**

*ShikshaPath - Empowering Education Through Technology*
