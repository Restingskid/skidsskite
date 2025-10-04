"""
skids.rest - Enhanced Flask Application
Full-featured pastebin with user management, chat, support system, and premium subscriptions
"""
from flask import Flask, render_template, request, url_for, redirect, jsonify, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import sys
import json
import stripe
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from sqlalchemy.exc import IntegrityError

# Import models and database
from models import User, Paste, Comment, SupportTicket, ChatMessage, SecurityLog
from database import db_session, init_db, engine

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['SESSION_TYPE'] = 'filesystem'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID')

# Discord Webhook
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")
mail = Mail(app)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
)

# Legacy data paths (for migration)
DATA = os.path.join(os.getcwd(), "data")
ADMIN_PASTES = os.path.join(os.getcwd(), "data", "admin")
ANON_PASTES = os.path.join(os.getcwd(), "data", "other")


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter_by(id=user_id).first()


# Helper function to log security events
def log_security_event(action, success=True, user_id=None, additional_data=None):
    """Log security events to database"""
    try:
        log = SecurityLog(
            action=action,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            user_id=user_id,
            success=success,
            additional_data=additional_data
        )
        db_session.add(log)
        db_session.commit()
    except Exception as e:
        print(f"Error logging security event: {e}")
        db_session.rollback()


# Helper function to send Discord notifications
def send_discord_notification(message):
    """Send notification to Discord webhook"""
    if not DISCORD_WEBHOOK_URL:
        return
    
    try:
        import requests
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Error sending Discord notification: {e}")


# Context processor to inject user data into templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)


# Teardown function to close database session
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route("/register", methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        
        # Validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('register.html')
        
        if len(username) < 3 or len(username) > 50:
            flash('Username must be between 3 and 50 characters', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        # Check if user exists
        existing_user = db_session.query(User).filter_by(username=username).first()
        if existing_user:
            flash('Username already taken', 'error')
            log_security_event('register', success=False, additional_data={'username': username})
            return render_template('register.html')
        
        # Create user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            password=hashed_password,
            email=email if email else None
        )
        
        try:
            db_session.add(new_user)
            db_session.commit()
            log_security_event('register', success=True, user_id=username)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db_session.rollback()
            flash('Username or email already exists', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = db_session.query(User).filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # Check if banned or suspended
            if user.is_banned:
                flash('Your account has been banned', 'error')
                log_security_event('login', success=False, user_id=username, additional_data={'reason': 'banned'})
                return render_template('login.html')
            
            if user.is_suspended:
                if user.suspended_until and user.suspended_until > datetime.utcnow():
                    flash(f'Your account is suspended until {user.suspended_until.strftime("%Y-%m-%d %H:%M")}', 'error')
                    log_security_event('login', success=False, user_id=username, additional_data={'reason': 'suspended'})
                    return render_template('login.html')
                else:
                    # Suspension expired
                    user.is_suspended = False
                    user.suspended_until = None
                    db_session.commit()
            
            login_user(user)
            log_security_event('login', success=True, user_id=username)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            log_security_event('login', success=False, additional_data={'username': username})
    
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    log_security_event('logout', success=True, user_id=username)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route("/")
def index():
    """Homepage with paste listings"""
    # Get pinned pastes (admin posts)
    admin_posts = db_session.query(Paste).filter_by(
        is_pinned=True,
        is_deleted=False
    ).order_by(desc(Paste.pinned_at)).limit(10).all()
    
    # Get recent public pastes (anonymous posts)
    anon_posts = db_session.query(Paste).filter_by(
        is_public=True,
        is_deleted=False,
        is_pinned=False
    ).order_by(desc(Paste.created_date)).limit(20).all()
    
    # Convert to format expected by template
    admin_posts_list = []
    for paste in admin_posts:
        admin_posts_list.append({
            'id': str(paste.id),
            'name': paste.title,
            'creation_date': paste.created_date.strftime('%d-%m-%Y') if paste.created_date else '',
            'creation_time': paste.created_date.strftime('%H:%M:%S') if paste.created_date else '',
            'size': round(len(paste.content) / 1000, 2) if paste.content else 0
        })
    
    anon_posts_list = []
    for paste in anon_posts:
        anon_posts_list.append({
            'id': str(paste.id),
            'name': paste.title,
            'creation_date': paste.created_date.strftime('%d-%m-%Y') if paste.created_date else '',
            'creation_time': paste.created_date.strftime('%H:%M:%S') if paste.created_date else '',
            'size': round(len(paste.content) / 1000, 2) if paste.content else 0
        })
    
    return render_template(
        'index.html',
        admin_posts_list=admin_posts_list,
        anon_posts_list=anon_posts_list
    )


@app.route("/post/<file>")
def post(file):
    """View anonymous paste (compatibility route)"""
    # Try to find paste by title (for backward compatibility)
    paste = db_session.query(Paste).filter_by(title=file, is_deleted=False).first()
    
    if not paste:
        flash('Paste not found', 'error')
        return redirect(url_for('index'))
    
    # Check if expired
    if paste.expires_at and paste.expires_at < datetime.utcnow():
        flash('This paste has expired', 'error')
        return redirect(url_for('index'))
    
    # Increment view count
    paste.views += 1
    db_session.commit()
    
    return render_template(
        'post.html',
        filename=paste.title,
        file_content=paste.content,
        creation_date=paste.created_date.strftime('%d-%m-%Y') if paste.created_date else '',
        creation_time=paste.created_date.strftime('%H:%M:%S') if paste.created_date else '',
        size=round(len(paste.content) / 1000, 2) if paste.content else 0
    )


@app.route("/admin/<file>")
def admin_post(file):
    """View admin/pinned paste (compatibility route)"""
    # Try to find pinned paste by title
    paste = db_session.query(Paste).filter_by(
        title=file,
        is_pinned=True,
        is_deleted=False
    ).first()
    
    if not paste:
        flash('Paste not found', 'error')
        return redirect(url_for('index'))
    
    # Increment view count
    paste.views += 1
    db_session.commit()
    
    return render_template(
        'admin.html',
        filename=paste.title,
        file_content=paste.content,
        creation_date=paste.created_date.strftime('%d-%m-%Y') if paste.created_date else '',
        creation_time=paste.created_date.strftime('%H:%M:%S') if paste.created_date else '',
        size=round(len(paste.content) / 1000, 2) if paste.content else 0
    )


@app.route("/new")
def new_paste():
    """Show new paste form"""
    _DEFAULT_POST_TEMPLATE = "# Welcome to skids.rest\n# Paste your code here"
    return render_template('new.html', paste_template_text=_DEFAULT_POST_TEMPLATE)


@app.route("/new_paste", methods=['POST'])
@limiter.limit("20 per hour")
def new_paste_form_post():
    """Create new paste (form submission)"""
    try:
        title = request.form.get('pasteTitle', 'Untitled').strip()
        content = request.form.get('pasteContent', '').strip()
        
        if not content:
            flash('Paste content cannot be empty', 'error')
            return redirect(url_for('new_paste'))
        
        # Replace forward slashes in title to avoid path issues
        title = title.replace("/", "%2F")
        
        # Create paste
        paste = Paste(
            title=title,
            content=content,
            language='text',  # Default language
            is_public=True,   # Default to public
            expires_at=None,  # Never expires by default
            created_by=current_user.username if current_user.is_authenticated else 'anonymous'
        )
        
        db_session.add(paste)
        
        # Update user paste count
        if current_user.is_authenticated:
            current_user.paste_count += 1
        
        db_session.commit()
        
        log_security_event(
            'paste_create',
            success=True,
            user_id=current_user.username if current_user.is_authenticated else None,
            additional_data={'paste_id': str(paste.id), 'title': title}
        )
        
        flash('Paste created successfully!', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        db_session.rollback()
        flash(f'Error creating paste: {str(e)}', 'error')
        return redirect(url_for('new_paste'))


@app.route("/paste/<paste_id>")
def view_paste(paste_id):
    """View a paste"""
    paste = db_session.query(Paste).filter_by(id=paste_id).first()
    
    if not paste or paste.is_deleted:
        flash('Paste not found', 'error')
        return redirect(url_for('index'))
    
    # Check if expired
    if paste.expires_at and paste.expires_at < datetime.utcnow():
        flash('This paste has expired', 'error')
        return redirect(url_for('index'))
    
    # Check visibility
    if not paste.is_public and (not current_user.is_authenticated or current_user.username != paste.created_by):
        flash('This paste is private', 'error')
        return redirect(url_for('index'))
    
    # Increment view count
    paste.views += 1
    db_session.commit()
    
    return render_template('view_paste.html', paste=paste)


# ============================================================================
# USER PROFILE ROUTES
# ============================================================================

@app.route("/user/<username>")
def user_profile(username):
    """View user profile"""
    user = db_session.query(User).filter_by(username=username).first()
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    # Get user's public pastes
    user_pastes = db_session.query(Paste).filter_by(
        created_by=username,
        is_public=True,
        is_deleted=False
    ).order_by(desc(Paste.created_date)).limit(10).all()
    
    # Get profile comments
    comments = db_session.query(Comment).filter_by(
        profile_user=username
    ).order_by(desc(Comment.created_at)).limit(20).all()
    
    return render_template(
        'user_profile.html',
        user=user,
        user_pastes=user_pastes,
        comments=comments
    )


@app.route("/user/<username>/comment", methods=['POST'])
@login_required
@limiter.limit("10 per hour")
def post_comment(username):
    """Post a comment on user's profile"""
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('user_profile', username=username))
    
    comment = Comment(
        content=content,
        created_by=current_user.username,
        profile_user=username
    )
    
    db_session.add(comment)
    
    # Update comment count
    current_user.comment_count += 1
    
    db_session.commit()
    
    flash('Comment posted!', 'success')
    return redirect(url_for('user_profile', username=username))


# ============================================================================
# CHAT ROUTES (WebSocket)
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    if current_user.is_authenticated:
        emit('user_connected', {'username': current_user.username}, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    if current_user.is_authenticated:
        emit('user_disconnected', {'username': current_user.username}, broadcast=True)


@socketio.on('send_message')
def handle_message(data):
    """Handle chat message"""
    if not current_user.is_authenticated:
        return
    
    content = data.get('message', '').strip()
    room = data.get('room', 'global')
    
    if not content:
        return
    
    # Save message to database
    message = ChatMessage(
        user_id=current_user.username,
        username=current_user.username,
        content=content,
        room=room
    )
    
    db_session.add(message)
    db_session.commit()
    
    # Broadcast message
    emit('new_message', {
        'id': str(message.id),
        'username': current_user.username,
        'content': content,
        'timestamp': message.created_at.isoformat(),
        'user_color': current_user.username_color
    }, broadcast=True)


@app.route("/chat")
@login_required
def chat():
    """Chat page"""
    # Get recent messages
    messages = db_session.query(ChatMessage).filter_by(
        room='global'
    ).order_by(desc(ChatMessage.created_at)).limit(100).all()
    
    messages.reverse()  # Show oldest first
    
    return render_template('chat.html', messages=messages)


# ============================================================================
# SUPPORT TICKET ROUTES
# ============================================================================

@app.route("/support", methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def support():
    """Support ticket submission"""
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        email = request.form.get('email', '').strip()
        priority = request.form.get('priority', 'normal')
        
        if not subject or not message:
            flash('Subject and message are required', 'error')
            return render_template('support.html')
        
        # Create ticket
        ticket = SupportTicket(
            user_id=current_user.username if current_user.is_authenticated else None,
            email=email if not current_user.is_authenticated else current_user.email,
            subject=subject,
            message=message,
            priority=priority
        )
        
        db_session.add(ticket)
        db_session.commit()
        
        # Send Discord notification
        send_discord_notification(
            f"🎫 New Support Ticket #{str(ticket.id)[:8]}\n"
            f"**Subject:** {subject}\n"
            f"**Priority:** {priority}\n"
            f"**From:** {current_user.username if current_user.is_authenticated else email}"
        )
        
        flash('Support ticket submitted successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('support.html')


@app.route("/support/tickets")
@login_required
def view_tickets():
    """View user's support tickets"""
    tickets = db_session.query(SupportTicket).filter_by(
        user_id=current_user.username
    ).order_by(desc(SupportTicket.created_at)).all()
    
    return render_template('my_tickets.html', tickets=tickets)


# ============================================================================
# PREMIUM/STRIPE ROUTES
# ============================================================================

@app.route("/upgrade")
def upgrade():
    """Premium upgrade page"""
    return render_template('upgrade.html', stripe_key=STRIPE_PUBLISHABLE_KEY)


@app.route("/create-checkout-session", methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('upgrade', _external=True),
            metadata={
                'user_id': str(current_user.id),
                'username': current_user.username
            }
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route("/payment-success")
@login_required
def payment_success():
    """Payment success page"""
    session_id = request.args.get('session_id')
    
    if session_id:
        # Update user to premium
        current_user.tier = 'premium'
        current_user.tier_status = 'active'
        current_user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
        db_session.commit()
        
        flash('Welcome to Premium! 🎉', 'success')
    
    return render_template('payment_success.html')


# ============================================================================
# ADMIN ROUTES
# ============================================================================

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'manager']:
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    """Admin panel"""
    # Get statistics
    total_users = db_session.query(User).count()
    total_pastes = db_session.query(Paste).count()
    total_tickets = db_session.query(SupportTicket).filter_by(status='open').count()
    
    # Get recent security logs
    recent_logs = db_session.query(SecurityLog).order_by(
        desc(SecurityLog.timestamp)
    ).limit(50).all()
    
    return render_template(
        'admin_panel.html',
        total_users=total_users,
        total_pastes=total_pastes,
        total_tickets=total_tickets,
        recent_logs=recent_logs
    )


@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    """Admin user management"""
    users = db_session.query(User).order_by(desc(User.joined_date)).all()
    return render_template('admin_users.html', users=users)


@app.route("/admin/ban-user", methods=['POST'])
@login_required
@admin_required
def ban_user():
    """Ban a user"""
    username = request.form.get('username')
    reason = request.form.get('reason', 'No reason provided')
    permanent = request.form.get('permanent') == 'true'
    
    user = db_session.query(User).filter_by(username=username).first()
    
    if user:
        user.is_banned = True
        user.banned_by = current_user.username
        user.ban_reason = reason
        user.banned_at = datetime.utcnow()
        user.banned_until = None if permanent else datetime.utcnow() + timedelta(days=30)
        
        db_session.commit()
        
        log_security_event(
            'admin_action',
            success=True,
            user_id=current_user.username,
            additional_data={'action': 'ban_user', 'target': username}
        )
        
        flash(f'User {username} has been banned', 'success')
    
    return redirect(url_for('admin_users'))


@app.route("/admin/tickets")
@login_required
@admin_required
def admin_tickets():
    """Admin ticket management"""
    tickets = db_session.query(SupportTicket).order_by(
        desc(SupportTicket.created_at)
    ).all()
    
    return render_template('admin_tickets.html', tickets=tickets)


# ============================================================================
# HALL OF AUTISM (Featured Users)
# ============================================================================

@app.route("/hol")
def hall_of_loosers():
    """Hall of Loosers - Featured users"""
    import json
    DATA = os.path.join(os.getcwd(), "data")
    
    # Load from JSON file for backward compatibility
    try:
        with open(os.path.join(DATA, "hol.json"), "r", encoding="utf-8") as file:
            data = json.load(file)
            loosers_list = data.get("loosers", [])
    except:
        loosers_list = []
    
    return render_template('hol.html', loosers_list=loosers_list)


# ============================================================================
# LEGACY ROUTES (for backward compatibility)
# ============================================================================

@app.route("/tos")
def tos():
    """Terms of Service"""
    DATA = os.path.join(os.getcwd(), "data")
    with open(os.path.join(DATA, "tos"), "r", encoding="utf-8") as file:
        filec = file.read()
    return render_template("tos.html", file_content=filec)


@app.route("/links")
@app.route("/pages")
def list_of_pages():
    """List of pages"""
    return render_template("pages.html")


# ============================================================================
# API ROUTES (for AJAX requests)
# ============================================================================

@app.route("/api/users")
def api_users():
    """API: Get all users"""
    users = db_session.query(User).all()
    return jsonify([{
        'username': u.username,
        'role': u.role,
        'reputation': u.reputation_points,
        'joined': u.joined_date.isoformat()
    } for u in users])


@app.route("/api/pastes")
def api_pastes():
    """API: Get public pastes"""
    pastes = db_session.query(Paste).filter_by(
        is_public=True,
        is_deleted=False
    ).order_by(desc(Paste.created_date)).limit(50).all()
    
    return jsonify([{
        'id': str(p.id),
        'title': p.title,
        'language': p.language,
        'views': p.views,
        'created_by': p.created_by,
        'created_date': p.created_date.isoformat()
    } for p in pastes])


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    # Initialize database
    print("🚀 Initializing skids.rest...")
    init_db()
    print("✅ Database initialized!")
    
    # Run app
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)