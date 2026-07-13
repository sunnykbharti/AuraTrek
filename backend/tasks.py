import os
import csv
from datetime import datetime, timedelta
from app import celery_app
from models import db, Users, Treks, TrekApplications
from mail import send_email
from celery.schedules import crontab

# Configure Celery Beat Periodic Clock Schedules
celery_app.conf.beat_schedule = {
    'send-daily-trekking-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=7, minute=0), # Fires daily at 7:00 AM local time
    },
    'send-monthly-activity-report': {
        'task': 'tasks.generate_monthly_admin_report',
        'schedule': crontab(day_of_month=1, hour=0, minute=0), # Midnight on the first day of the month
    },
}

# --- Job A: Scheduled Daily Reminders ---
@celery_app.task
def send_daily_reminders():
    # Target window: Treks beginning exactly tomorrow
    tomorrow_dt = datetime.utcnow() + timedelta(days=1)
    tomorrow_str = tomorrow_dt.strftime('%Y-%m-%d')
    
    # Logic Fixed: Added filter to match treks that specifically start tomorrow
    upcoming_bookings = db.session.query(TrekApplications, Users, Treks).\
        join(Users, TrekApplications.u_id == Users.u_id).\
        join(Treks, TrekApplications.s_id == Treks.t_id).\
        filter(TrekApplications.a_status == 'APPROVED').\
        filter(Treks.t_start_date == tomorrow_str).all() # <--- Crucial Date Logic Filter Added

    for app, user, trek in upcoming_bookings:
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #ee710a;">🎒 Ready for the Trail, {user.username}?</h2>
                <p>This is your daily reminder that your expedition space is confirmed!</p>
                <div style="background-color: #fdfbf7; padding: 15px; border: 1px solid #ebdcb9; border-radius: 8px;">
                    <p><strong>Trail Destination:</strong> {trek.t_name}</p>
                    <p><strong>Location Details:</strong> {trek.t_location}</p>
                    <p><strong>Difficulty Rating:</strong> {trek.t_difficulty}</p>
                    <p><strong>Duration Length:</strong> {trek.t_duration} Days</p>
                </div>
                <p style="font-size: 12px; color: #777; margin-top: 15px;">Please make sure to carry your safety kit parameters. See you out there!</p>
            </body>
        </html>
        """
        send_email(user.username, "🎒 AuraTrek: Upcoming Expedition Reminder!", html_content)
    return f"Processed reminders loop sequence for tomorrow ({tomorrow_str})."


# --- Job B: Scheduled Monthly Admin Report ---
@celery_app.task
def generate_monthly_admin_report():
    admin_user = Users.query.filter_by(u_role='admin').first()
    if not admin_user:
        return "Admin account entity missing."

    # Compute Core Performance Metrics
    total_treks = Treks.query.count()
    total_participants = TrekApplications.query.filter_by(a_status='APPROVED').count()
    
    # Query Fixed: Order By engine exception bypass handled natively
    popular_treks = db.session.query(Treks.t_name, db.func.count(TrekApplications.a_id).label('booking_count')).\
        join(TrekApplications, Treks.t_id == TrekApplications.s_id).\
        group_by(Treks.t_name).\
        order_by(db.desc(db.func.count(TrekApplications.a_id))).limit(3).all()

    popular_rows = "".join([f"<li><strong>{t_name}</strong> ({count} active bookings)</li>" for t_name, count in popular_treks])

    html_report = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4ebd9; padding: 20px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #d69c0c;">
                <h2 style="color: #ee710a; border-bottom: 2px solid #ebdcb9; padding-bottom: 10px;">📊 AuraTrek Monthly Executive Report</h2>
                <p>Hello System Administrator, here are the platform metrics statistics for the past month:</p>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #efede7;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #cbd5e1;">Metric Parameter</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #cbd5e1;">Total Compiled Value</th>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #cbd5e1;">Active Managed Treks</td>
                        <td style="padding: 12px; border: 1px solid #cbd5e1; font-weight: bold;">{total_treks}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #cbd5e1;">Trekkers Participated</td>
                        <td style="padding: 12px; border: 1px solid #cbd5e1; font-weight: bold;">{total_participants}</td>
                    </tr>
                </table>
                <h3>🗺️ Top Trending Trails This Month:</h3>
                <ul>
                    {popular_rows if popular_rows else "<li>No active trail data logs logged yet.</li>"}
                </ul>
            </div>
        </body>
    </html>
    """
    send_email(admin_user.username, "📊 AuraTrek: Monthly Management Performance Review", html_report)
    return "Monthly compilation metrics dispatch completed."


# --- Job C: User Triggered Async CSV Export ---
@celery_app.task
def export_booking_history_csv(user_id, user_email):
    # Ensure export directory context exists locally
    os.makedirs('exports', exist_ok=True)
    target_path = f"exports/booking_history_{user_id}.csv"

    # Fetch rows compilation matrix
    records = db.session.query(TrekApplications, Treks).\
        join(Treks, TrekApplications.t_id == Treks.t_id).\
        filter(TrekApplications.u_id == user_id).all()

    with open(target_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['User ID', 'Trek Destination', 'Location Grid', 'Booking Status'])
        for app, trek in records:
            writer.writerow([user_id, trek.t_name, trek.t_location, app.a_status])

    # Send confirmation notification alert right once generation processing finishes
    alert_html = """
    <html>
        <body>
            <h3 style="color: #ee710a;">📦 Your Expedition Data Export is Ready!</h3>
            <p>We have successfully compiled your booking history records. Find your attached data CSV archive sheet below.</p>
        </body>
    </html>
    """
    send_email(user_email, "📦 AuraTrek: Your Booking Data CSV Export", alert_html, attachment_path=target_path)
    return target_path