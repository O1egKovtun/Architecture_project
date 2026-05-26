from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from functools import wraps

from services.auth_service import AuthService
from services.event_service import EventService
from services.booking_service import BookingService
from repositories.db_repository import UserRepository, BookingRepository

# Blueprint — "модуль" маршрутів, зареєстрований в app.py
main_bp = Blueprint('main', __name__)

# Ініціалізуємо сервіси один раз (не в кожному запиті)
auth_service = AuthService()
event_service = EventService()
booking_service = BookingService()
user_repo = UserRepository()


# ==========================================
# ДЕКОРАТОРИ (Guards)
# ==========================================

def login_required(f):
    """Захищає маршрут: лише для авторизованих користувачів."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("⚠️ Будь ласка, увійдіть у систему.", "warning")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Захищає маршрут: лише для адміністраторів."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("⛔ Доступ заборонено. Потрібні права адміністратора.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


# ==========================================
# МАРШРУТИ (Routes)
# ==========================================

@main_bp.route('/')
def index():
    events = event_service.get_all_events()
    # Виводимо лише активні події на головній
    active = [e for e in events if e['status'] == 'Активна'][:3]
    return render_template('index.html', events=active)


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        res = auth_service.register(request.form.get('name'), request.form.get('email'))
        if res["success"]:
            session.update({'user_id': res['user_id'], 'user_name': res['name'], 'role': res['role']})
            flash("🎉 Акаунт успішно створено!", "success")
            return redirect(url_for('main.events'))
        flash(res["error"], "danger")
    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        res = auth_service.login(request.form.get('email'))
        if res["success"]:
            session.update({'user_id': res['user_id'], 'user_name': res['name'], 'role': res['role']})
            flash(f"З поверненням, {res['name']}! 👋", "success")
            target = 'main.admin_panel' if res['role'] == 'admin' else 'main.profile'
            return redirect(url_for(target))
        flash(res["error"], "danger")
    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    flash("Ви вийшли з системи.", "info")
    return redirect(url_for('main.index'))


@main_bp.route('/events')
def events():
    all_events = event_service.get_all_events()
    return render_template('events.html', events=all_events)


@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = event_service.get_event_with_availability(event_id)
    if not event:
        flash("Подію не знайдено.", "danger")
        return redirect(url_for('main.events'))
    return render_template('event_detail.html', event=event)


@main_bp.route('/book/<int:event_id>', methods=['POST'])
@login_required
def book_event(event_id):
    try:
        tickets_count = int(request.form.get('tickets_count', 1))
    except ValueError:
        tickets_count = 1

    result = booking_service.book_tickets(session['user_id'], event_id, tickets_count)
    if result['success']:
        flash(f"✅ Бронювання успішне! До сплати: {result['total_price']:.2f} грн.", "success")
        return redirect(url_for('main.profile'))
    flash(result['error'], "danger")
    return redirect(url_for('main.event_detail', event_id=event_id))


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
    booking_service.cancel_booking(booking_id, session['user_id'])
    flash("Бронювання скасовано.", "info")
    return redirect(url_for('main.profile'))


@main_bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    booking_repo = BookingRepository()
    all_bookings = booking_repo.get_all()
    all_events = event_service.get_all_events()
    return render_template('admin.html', bookings=all_bookings, events=all_events)


@main_bp.route('/admin/create_event', methods=['POST'])
@login_required
@admin_required
def admin_create_event():
    try:
        event_service.create_event(request.form)
        flash("🎉 Подію успішно створено!", "success")
    except (ValueError, KeyError) as e:
        flash(f"Помилка: {e}", "danger")
    return redirect(url_for('main.admin_panel'))


@main_bp.route('/admin/update_event/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_event(event_id):
    new_status = request.form.get('status')
    event_service.update_event_status(event_id, new_status)
    flash(f"Статус події оновлено до «{new_status}».", "success")
    return redirect(url_for('main.admin_panel'))
