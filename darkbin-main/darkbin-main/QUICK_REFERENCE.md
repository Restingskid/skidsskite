# 🚀 skids.rest - Quick Reference Card

## ⚡ Quick Start
```bash
python start.py
```
**URL:** http://localhost:5000  
**Admin:** admin / admin123

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app_new.py` | Main application (NEW) |
| `models.py` | Database models |
| `database.py` | DB configuration |
| `init_db.py` | Initialize database |
| `start.py` | Quick start script |
| `.env` | Configuration |

---

## 🗄️ Database Tables

1. **users** - User accounts & profiles
2. **pastes** - Code/text pastes
3. **comments** - Profile comments
4. **support_tickets** - Support system
5. **chat_messages** - Real-time chat
6. **security_logs** - Audit logs

---

## 🔗 Main Routes

### Public
- `/` - Homepage
- `/register` - Sign up
- `/login` - Sign in
- `/paste/<id>` - View paste
- `/user/<username>` - User profile
- `/hol` - Hall of Autism
- `/tos` - Terms of Service

### Authenticated
- `/new` - Create paste
- `/chat` - Real-time chat
- `/support` - Submit ticket
- `/support/tickets` - My tickets
- `/upgrade` - Go premium
- `/logout` - Sign out

### Admin
- `/admin` - Admin panel
- `/admin/users` - User management
- `/admin/tickets` - Ticket management

### API
- `/api/users` - Get users (JSON)
- `/api/pastes` - Get pastes (JSON)

---

## 👤 User Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full access |
| **manager** | Full access |
| **mod** | Moderate content |
| **council** | Special user |
| **clique** | Special user |
| **user** | Standard user |

---

## 🎨 User Badges

- **★ PREMIUM** - Premium subscriber (gold)
- **ADMIN** - Administrator (red)
- **MANAGER** - Manager (orange)
- **MOD** - Moderator (cyan)

---

## 🔐 Security Features

- ✅ Bcrypt password hashing
- ✅ Rate limiting (5-20/hour)
- ✅ Security audit logs
- ✅ IP tracking
- ✅ Session management
- ✅ CORS protection

---

## ⚙️ Environment Variables

```env
DATABASE_URL=postgresql://...     # Required
SECRET_KEY=...                    # Required
STRIPE_SECRET_KEY=...             # Optional
DISCORD_WEBHOOK_URL=...           # Optional
MAIL_USERNAME=...                 # Optional
```

---

## 📊 Rate Limits

| Action | Limit |
|--------|-------|
| Register | 5/hour |
| Login | 10/hour |
| Create Paste | 20/hour |
| Comment | 10/hour |
| Support Ticket | 5/hour |

---

## 💬 WebSocket Events

### Send Message
```javascript
socket.emit('send_message', {
    message: 'Hello!',
    room: 'global'
});
```

### Receive Message
```javascript
socket.on('new_message', (data) => {
    // data: { id, username, content, timestamp, user_color }
});
```

---

## 🛠️ Common Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Initialize Database
```bash
python init_db.py
```

### Start Application
```bash
python app_new.py
```

### Quick Start (All-in-One)
```bash
python start.py
```

---

## 🐛 Troubleshooting

### Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### Database Connection Error
- Check `DATABASE_URL` in `.env`
- Verify Neon.tech access

### Port Already in Use
- Change port in `app_new.py`
- Or kill process on port 5000

---

## 📚 Documentation

- `SETUP_GUIDE.md` - Complete setup
- `README_NEW_FEATURES.md` - Feature docs
- `IMPLEMENTATION_SUMMARY.md` - What was built

---

## 🎯 Feature Checklist

- ✅ User authentication
- ✅ User profiles
- ✅ Paste system
- ✅ Real-time chat
- ✅ Support tickets
- ✅ Premium subscriptions
- ✅ Admin panel
- ✅ Security logging
- ✅ Role-based access
- ✅ Rate limiting

---

## 🔄 Migration

### From Old App
```bash
mv app.py app_old.py
mv app_new.py app.py
```

---

## 🚀 Production Deployment

1. Change `SECRET_KEY` in `.env`
2. Set `debug=False` in `app_new.py`
3. Use Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app_new:app
   ```
4. Set up Nginx reverse proxy
5. Configure SSL/TLS

---

## 📞 Quick Help

### Can't Login?
- Check username/password
- Verify account not banned
- Check security logs

### Chat Not Working?
- Ensure logged in
- Check WebSocket connection
- Verify flask-socketio installed

### Database Error?
- Check `DATABASE_URL`
- Run `python init_db.py`
- Verify network access

---

## 🎉 You're Ready!

Start your application:
```bash
python start.py
```

Visit: **http://localhost:5000**

Login: **admin / admin123**

Enjoy! 🚀