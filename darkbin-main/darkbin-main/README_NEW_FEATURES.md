# 🎉 skids.rest - New Features Documentation

## 🚀 What's New?

Your skids.rest application has been upgraded from a simple file-based pastebin to a **full-featured social platform** with all the features described in your PROJECT_OVERVIEW.md!

---

## ✨ New Features Added

### 1. **User Authentication System** 🔐
- User registration with email (optional)
- Secure login with bcrypt password hashing
- Session management
- Role-based access control (6 roles: admin, manager, mod, council, clique, user)
- User profiles with customization

### 2. **PostgreSQL Database** 🗄️
- Migrated from file-based storage to PostgreSQL
- Connected to your Neon.tech database
- 6 database tables:
  - `users` - User accounts and profiles
  - `pastes` - Code/text pastes
  - `comments` - Profile wall comments
  - `support_tickets` - Support system
  - `chat_messages` - Real-time chat
  - `security_logs` - Security audit logs

### 3. **User Profiles** 👤
- Customizable profiles (bio, avatar, banner)
- Custom username colors
- Reputation/karma system
- Follower/following counts
- Profile wall comments
- User statistics (paste count, comment count)

### 4. **Premium Subscriptions** 💎
- Stripe integration for payments
- Premium tier with special badges
- Subscription management
- Automatic expiration handling

### 5. **Real-Time Chat** 💬
- WebSocket-based global chat
- Message history stored in database
- User presence indicators
- Custom username colors in chat
- Real-time message broadcasting

### 6. **Support Ticket System** 🎫
- Guest and authenticated ticket submission
- Staff assignment
- Internal notes (staff-only)
- Priority levels (normal/urgent)
- Status tracking (open/pending/closed)
- Discord webhook notifications

### 7. **Admin Panel** 👨‍💼
- User management:
  - Ban users (temporary or permanent)
  - Suspend users
  - Change user roles
  - View user statistics
- Paste moderation:
  - Delete pastes
  - Pin important pastes
- Security logs viewer
- Support ticket management

### 8. **Enhanced Paste System** 📝
- Database-backed storage (no more file system)
- Public/private visibility
- Expiration dates
- View counters
- Syntax highlighting
- Pin to homepage (admin feature)
- Soft delete (can be recovered)

### 9. **Security Features** 🛡️
- Rate limiting on all sensitive endpoints
- Brute force protection
- Security audit logging
- IP address tracking
- User agent logging
- Session management
- CORS protection
- Input validation

### 10. **Hall of Autism** 🏆
- Featured users system
- Reputation-based ranking
- Admin can feature/unfeature users

---

## 📊 Database Schema

### Users Table
```sql
- id (UUID)
- username (unique)
- password (bcrypt hashed)
- email (optional)
- role (admin/manager/mod/council/clique/user)
- bio, profile_image, banner_url
- username_color (default: #ff69b4)
- paste_count, comment_count
- reputation_points
- follower_count, following_count
- Premium fields (tier, stripe_customer_id, etc.)
- Moderation fields (is_banned, ban_reason, etc.)
- is_featured (for Hall of Autism)
```

### Pastes Table
```sql
- id (UUID)
- title, content, language
- is_public, expires_at
- views, created_date, created_by
- Moderation fields (is_deleted, deleted_by, etc.)
- Pinning fields (is_pinned, pinned_by, etc.)
```

### Comments Table
```sql
- id (UUID)
- content
- created_at, created_by
- profile_user (who's profile the comment is on)
```

### Support Tickets Table
```sql
- id (UUID)
- user_id, email, subject, message
- status (open/pending/closed)
- priority (normal/urgent)
- assigned_to (staff username)
- notes (JSON array of internal notes)
- created_at, updated_at
```

### Chat Messages Table
```sql
- id (UUID)
- user_id, username, content
- room (default: global)
- created_at
```

### Security Logs Table
```sql
- id (UUID)
- action (login/register/paste_create/etc.)
- ip_address, user_agent
- timestamp, user_id
- success (boolean)
- additional_data (JSON)
```

---

## 🎯 User Roles & Permissions

### Admin
- Full access to everything
- Can ban/suspend users
- Can delete/pin pastes
- Can change user roles
- Can view security logs
- Can manage support tickets

### Manager
- Same as admin (second-tier admin)

### Mod
- Can moderate content
- Can view support tickets
- Limited admin access

### Council
- Special user tier
- Custom badge

### Clique
- Special user tier
- Custom badge

### User
- Standard user
- Can create pastes
- Can comment on profiles
- Can use chat

---

## 🔗 New Routes

### Authentication
- `/register` - User registration page
- `/login` - User login page
- `/logout` - Logout (requires login)

### User Profiles
- `/user/<username>` - View user profile
- `/user/<username>/comment` - Post comment (POST, requires login)

### Chat
- `/chat` - Real-time chat page (requires login)

### Support
- `/support` - Submit support ticket
- `/support/tickets` - View your tickets (requires login)

### Premium
- `/upgrade` - Premium upgrade page
- `/create-checkout-session` - Stripe checkout (POST, requires login)
- `/payment-success` - Payment success page

### Admin
- `/admin` - Admin panel (requires admin role)
- `/admin/users` - User management
- `/admin/ban-user` - Ban user (POST)
- `/admin/tickets` - Ticket management

### API (JSON)
- `/api/users` - Get all users (JSON)
- `/api/pastes` - Get public pastes (JSON)

### Legacy (Updated)
- `/` - Homepage (now shows database pastes)
- `/new` - Create paste (now saves to database)
- `/paste/<id>` - View paste (now from database)
- `/hol` - Hall of Autism (now from database)
- `/tos` - Terms of Service

---

## 🎨 UI Enhancements

### Navbar Updates
- Shows username with custom color
- Premium badge (★ PREMIUM)
- Role badges (ADMIN, MANAGER, MOD)
- Login/Register links for guests
- Chat and Support links for logged-in users
- Admin Panel link for admins

### Flash Messages
- Success messages (green)
- Error messages (red)
- Info messages (blue)
- Auto-hide after 5 seconds
- Smooth animations

### User Badges
- Premium: Gold star badge
- Admin: Red badge
- Manager: Orange badge
- Mod: Cyan badge

---

## 🔧 Configuration

### Environment Variables (.env)
```env
DATABASE_URL=postgresql://...  # Your Neon.tech database
SECRET_KEY=...                 # Flask secret key
STRIPE_SECRET_KEY=...          # Stripe API key (optional)
DISCORD_WEBHOOK_URL=...        # Discord notifications (optional)
MAIL_USERNAME=...              # Email for support (optional)
```

### Rate Limits
- Registration: 5 per hour
- Login: 10 per hour
- Paste creation: 20 per hour
- Comments: 10 per hour
- Support tickets: 5 per hour

---

## 📱 WebSocket Events (Chat)

### Client → Server
- `send_message` - Send a chat message
  ```javascript
  socket.emit('send_message', { message: 'Hello!', room: 'global' });
  ```

### Server → Client
- `new_message` - Receive new message
  ```javascript
  socket.on('new_message', (data) => {
      // data: { id, username, content, timestamp, user_color }
  });
  ```
- `user_connected` - User joined chat
- `user_disconnected` - User left chat

---

## 🔐 Security Features

### Password Security
- Bcrypt hashing with salt
- Minimum 6 characters
- No plain text storage

### Rate Limiting
- IP-based rate limiting
- Prevents brute force attacks
- Progressive delays on failed logins

### Security Logging
- All login attempts logged
- Admin actions logged
- IP addresses tracked
- User agents recorded

### Session Management
- Secure session cookies
- Session expiration
- CSRF protection

---

## 🚀 Quick Start

### Option 1: Use the Quick Start Script
```bash
python start.py
```

This will:
1. Check dependencies
2. Create .env if needed
3. Initialize database
4. Create admin user
5. Start the application

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start application
python app_new.py
```

### Default Admin Credentials
- **Username:** admin
- **Password:** admin123
- ⚠️ **Change this immediately after first login!**

---

## 📈 Migration from Old App

The old file-based app (`app.py`) still exists. The new app is in `app_new.py`.

### To fully migrate:
1. Test the new app thoroughly
2. Export any important data from old file system
3. Rename files:
   ```bash
   mv app.py app_old.py
   mv app_new.py app.py
   ```

### Data Migration
Old pastes in `data/admin/` and `data/other/` are not automatically migrated. You can:
1. Manually recreate important pastes in the new system
2. Write a migration script to import them
3. Keep the old app running alongside for reference

---

## 🎯 Next Steps

### Immediate
1. ✅ Run `python start.py`
2. ✅ Login with admin account
3. ✅ Change admin password
4. ✅ Create a test user account
5. ✅ Test all features

### Optional Configuration
1. Configure Stripe for premium subscriptions
2. Set up Discord webhook for notifications
3. Configure email for support tickets
4. Customize theme colors
5. Add more user roles

### Production Deployment
1. Change `SECRET_KEY` in .env
2. Set `debug=False` in app_new.py
3. Use Gunicorn or uWSGI
4. Set up Nginx reverse proxy
5. Configure SSL/TLS
6. Set up monitoring

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Database connection errors
- Check DATABASE_URL in .env
- Verify Neon.tech database is accessible
- Check firewall/network settings

### "Port already in use"
- Change port in app_new.py (line at bottom)
- Or kill the process using port 5000

### WebSocket not working
- Make sure flask-socketio is installed
- Check browser console for errors
- Verify CORS settings

---

## 📚 Additional Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Flask-SocketIO Documentation:** https://flask-socketio.readthedocs.io/
- **Stripe Documentation:** https://stripe.com/docs

---

## 🎉 Congratulations!

Your skids.rest application now has all the features from your PROJECT_OVERVIEW.md!

Enjoy your full-featured pastebin platform with:
- ✅ User authentication
- ✅ Real-time chat
- ✅ Support tickets
- ✅ Premium subscriptions
- ✅ Admin panel
- ✅ And much more!

Happy coding! 🚀