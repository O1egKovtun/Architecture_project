# controllers/routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from functools import wraps

from services.auth_service import AuthService
from services.event_service import EventService
from services.booking_service import BookingService
from repositories.db_repository import UserRepository, BookingRepository

main_bp = Blueprint('main', __name__)

# Ініціалізація сервісів
auth_service = AuthService()
event_service = EventService()
booking_service = BookingService()
user_repo = UserRepository()


# ==========================================
# ДЕКОРАТОРИ ЗАХИСТУ (Guards)
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("⚠️ Будь ласка, увійдіть у систему для виконання цієї дії.", "warning")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("⛔ Доступ заборонено. Потрібні права адміністратора.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated


# ==========================================
# МАРШРУТИ ДОДАТКУ (Routes)
# ==========================================
@main_bp.route('/')
def index():
    events = event_service.get_all_events()
    return render_template('index.html', events=events)


@main_bp.route('/create-event', methods=['POST'])
def create_event():
    """Публічний або адмінський швидкий маршрут для генерації події за допомогою Builder + Factory."""
    try:
        event_service.create_event(request.form)
        flash("🎉 Подію успішно згенеровано через Builder та збережено!", "success")
    except Exception as e:
        flash(f"Помилка створення: {e}", "danger")
    return redirect(url_for('main.index'))


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        user_id, role = auth_service.register_user(name, email)

        if user_id:
            session.update({'user_id': user_id, 'user_name': name, 'role': role})
            flash("🎉 Акаунт успішно створено!", "success")
            return redirect(url_for('main.index'))
        flash("Помилка реєстрації. Можливо, такий email вже зайнятий.", "danger")
    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user = auth_service.login_user(email)

        if user:
            role = 'admin' if 'admin' in user['email'].lower() else 'user'
            session.update({'user_id': user['id'], 'user_name': user['name'], 'role': role})
            flash(f"З поверненням, {user['name']}! 👋", "success")
            return redirect(url_for('main.index'))
        flash("Користувача з таким email не знайдено.", "danger")
    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    flash("Ви успішно вийшли з системи.", "info")
    return redirect(url_for('main.index'))


@main_bp.route('/book/<int:event_id>', methods=['POST'])
@login_required
def book_event(event_id):
    try:
        tickets_count = int(request.form.get('tickets_count', 1))
    except ValueError:
        tickets_count = 1

    result = booking_service.create_booking(session['user_id'], event_id, tickets_count)
    if isinstance(result, int):
        flash("✅ Бронювання успішне! Квиток додано в кабінет.", "success")
        return redirect(url_for('main.profile'))

    flash(f"⚠️ {result}", "danger")
    return redirect(url_for('main.index'))


@main_bp.route('/profile')
@login_required
def profile():
    bookings = booking_service.get_user_bookings(session['user_id'])
    notifications = user_repo.get_notifications(session['user_id'])
    stats = {
        "total_bookings": len(bookings),
        "total_spent": sum(b['total_price'] for b in bookings if b['status'] != 'Скасовано')
    }
    return render_template('profile.html', bookings=bookings, stats=stats, notifications=notifications)


@main_bp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking_service.cancel_booking(booking_id)
    flash("Бронювання успішно скасовано. Кошти повернуто на віртуальний рахунок.", "info")
    return redirect(url_for('main.profile'))