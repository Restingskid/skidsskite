# 🚀 skids.rest - Complete Setup Guide

## Overview
This guide will help you set up the full-featured skids.rest application with all features from the PROJECT_OVERVIEW.md including:
- ✅ User authentication & profiles
- ✅ PostgreSQL database
- ✅ Real-time chat (WebSocket)
- ✅ Support ticket system
- ✅ Premium subscriptions (Stripe)
- ✅ Admin panel
- ✅ Security logging
- ✅ Role-based access control

---

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database (Neon.tech configured)
- pip (Python package manager)

---

## 🔧 Installation Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask & extensions (Flask-Login, Flask-SocketIO, Flask-Bcrypt)
- SQLAlchemy & psycopg2 (PostgreSQL)
- Stripe (payment processing)
- And all other dependencies

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database (already configured)
DATABASE_URL=postgresql://neondb_owner:npg_zg5rQPL3ZTiO@ep-young-butterfly-ada3tk76-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

# Flask Secret Key (CHANGE THIS!)
SECRET_KEY=your-random-secret-key-here

# Stripe (optional - for premium subscriptions)
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_PRICE_ID=price_your_price_id

# Discord Webhook (optional - for notifications)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook

# Email (optional - for support tickets)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 3: Initialize Database

Run the database initialization script:

```bash
python init_db.py
```

This will:
- Create all database tables
- Create a default admin user (username: `admin`, password: `admin123`)

### Step 4: Run the Application

```bash
python app_new.py
```

The application will start on `http://localhost:5000`

---

## 🗄️ Database Schema

The following tables will be created:

### **users**
- User accounts with authentication
- Profiles (bio, avatar, banner)
- Premium subscriptions
- Moderation fields (bans, suspensions)
- Role-based access control

### **pastes**
- Code/text pastes
- Syntax highlighting
- Public/private visibility
- Expiration dates
- View counters
- Pinning (admin feature)

### **comments**
- Profile wall comments
- User-to-user messaging

### **support_tickets**
- Support ticket system
- Staff assignment
- Internal notes
- Priority levels

### **chat_messages**
- Real-time chat messages
- WebSocket-based

### **security_logs**
- Security audit logs
- Login attempts
- Admin actions

---

## 👤 Default Admin Account

After running `init_db.py`, you can login with:

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **IMPORTANT:** Change this password immediately after first login!

---

## 🎯 Features Overview

### 1. **User System**
- Registration & Login
- User profiles with customization
- Role-based permissions (admin, manager, mod, council, clique, user)
- Premium subscriptions via Stripe

### 2. **Pastebin**
- Create, view, edit pastes
- Syntax highlighting
- Public/private visibility
- Expiration dates
- View counters

### 3. **Real-Time Chat**
- WebSocket-based global chat
- Message history
- User presence indicators

### 4. **Support System**
- Ticket submission (guest & authenticated)
- Staff assignment
- Internal notes
- Discord notifications

### 5. **Admin Panel**
- User management (ban, suspend, role changes)
- Paste moderation (delete, pin)
- Security logs viewer
- Support ticket management

### 6. **Premium Features**
- Stripe integration
- Subscription management
- Premium badges

---

## 🔐 Security Features

- ✅ Bcrypt password hashing
- ✅ Rate limiting (login, registration, paste creation)
- ✅ Security audit logging
- ✅ Session management
- ✅ CORS protection
- ✅ Input validation

---

## 📁 File Structure

```
darkbin-main/
├── app_new.py              # Main application (NEW)
├── models.py               # Database models (NEW)
├── database.py             # Database configuration (NEW)
├── init_db.py              # Database initialization (NEW)
├── requirements.txt        # Updated dependencies
├── .env                    # Environment variables
├── templates/
│   ├── base.html           # Base template (NEW)
│   ├── navbar.html         # Updated navbar
│   ├── register.html       # Registration page (NEW)
│   ├── login.html          # Login page (NEW)
│   ├── chat.html           # Chat page (NEW)
│   └── ... (other templates)
└── static/
    └── files/
        └── darkbin.css     # Existing styles
```

---

## 🚦 Running in Production

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app_new:app
```

### Using Docker (optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app_new:app"]
```

Build and run:

```bash
docker build -t skidsrest .
docker run -p 5000:5000 --env-file .env skidsrest
```

---

## 🔄 Migration from Old App

The new `app_new.py` coexists with the old `app.py`. To migrate:

1. Run `init_db.py` to create database tables
2. Test the new application on a different port
3. Once satisfied, rename:
   - `app.py` → `app_old.py` (backup)
   - `app_new.py` → `app.py`

---

## 🐛 Troubleshooting

### Database Connection Issues

If you get connection errors:
1. Check your `DATABASE_URL` in `.env`
2. Ensure your IP is whitelisted in Neon.tech
3. Test connection: `python -c "from database import engine; print(engine.connect())"`

### Module Not Found Errors

```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use

Change the port in `app_new.py`:
```python
socketio.run(app, host="0.0.0.0", port=5001, debug=True)
```

---

## 📚 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Pastes
- `GET /` - Homepage with paste listings
- `GET /new` - Create new paste form
- `POST /new` - Submit new paste
- `GET /paste/<id>` - View paste

### User Profiles
- `GET /user/<username>` - View user profile
- `POST /user/<username>/comment` - Post profile comment

### Chat
- `GET /chat` - Chat page
- WebSocket events: `send_message`, `new_message`

### Support
- `GET /support` - Support ticket form
- `POST /support` - Submit ticket
- `GET /support/tickets` - View user's tickets

### Admin
- `GET /admin` - Admin panel
- `GET /admin/users` - User management
- `POST /admin/ban-user` - Ban user
- `GET /admin/tickets` - Ticket management

### API (JSON)
- `GET /api/users` - Get all users (JSON)
- `GET /api/pastes` - Get public pastes (JSON)

---

## 🎨 Customization

### Change Theme Colors

Edit `static/files/darkbin.css` or add custom styles in templates.

### Add New Roles

Edit `models.py` and add role checks in routes:

```python
if current_user.role in ['admin', 'manager', 'your_new_role']:
    # Allow access
```

### Configure Rate Limits

Edit limits in `app_new.py`:

```python
@limiter.limit("10 per hour")  # Adjust as needed
def your_route():
    pass
```

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review error logs
3. Check database connection
4. Verify environment variables

---

## ✅ Next Steps

1. ✅ Install dependencies
2. ✅ Configure `.env`
3. ✅ Run `init_db.py`
4. ✅ Start application with `python app_new.py`
5. ✅ Login with admin account
6. ✅ Change admin password
7. ✅ Configure Stripe (optional)
8. ✅ Configure Discord webhook (optional)
9. ✅ Test all features
10. ✅ Deploy to production

---

## 🎉 You're All Set!

Your skids.rest application is now ready with all features from the PROJECT_OVERVIEW.md!

Visit `http://localhost:5000` and start using your full-featured pastebin platform.