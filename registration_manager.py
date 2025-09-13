import sqlite3
from datetime import datetime, timedelta

from notifier import Notifier

class RegistrationManager:
    """Manage registration records and notifications."""

    def __init__(self, notifier: Notifier, db_path: str = "SQLite db/registration_form.db") -> None:
        self.notifier = notifier
        self.db_path = db_path

    def update_expired_memberships(self) -> None:
        current_date = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registration")
        registrations = cursor.fetchall()

        for registration in registrations:
            end_date = registration[15]
            contact_no = registration[9]
            if datetime.strptime(end_date, "%Y-%m-%d") < current_date:
                cursor.execute(
                    "UPDATE registration SET status=? WHERE id=?",
                    ("Expired", registration[0]),
                )
                conn.commit()
                sms_message = (
                    "Your gym membership has expired. Renew your subscription to continue accessing D'GRIT GYM."
                )
                self.notifier.send(contact_no, sms_message)

        conn.close()

    def notify_expiring_members(self) -> None:
        current_date = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registration")
        registrations = cursor.fetchall()

        for registration in registrations:
            end_date = registration[15]
            contact_no = registration[9]
            if datetime.strptime(end_date, "%Y-%m-%d") == current_date + timedelta(days=3):
                sms_message = (
                    "Your gym membership will expire in 3 days. Renew your subscription to continue accessing D'GRIT GYM."
                )
                self.notifier.send(contact_no, sms_message)

        conn.close()
