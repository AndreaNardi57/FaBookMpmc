from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from models import Book, Copies, User, Loan
import smtplib
from email.message import EmailMessage


def check_overdue_loans():
    db: Session = SessionLocal()

    try:
        one_month_ago = datetime.utcnow() - timedelta(days=30)

        stmt = (
            db.query(
                Loan.id,
                Book.title,
                Book.author,
                Loan.status,
                Copies.id.label('cp_id'),
                User.first_name,
                User.last_name,
                User.username,
                User.email,
                Loan.borrowed,
                Loan.due_back,
                Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
        ).filter (
                models.Loan.status == "on_loan",
                models.Loan.borrowed <= one_month_ago,
                models.Loan.return_date == '9999-01-01'
                )


        overdue_loans = stmt.all()
        
        for loan in overdue_loans:
            send_reminder_email(loan.email, loan)

    finally:
        db.close()



def send_reminder_email(to_email: str, loan):
    msg = EmailMessage()
    msg["Subject"] = "Promemoria restituzione libro" 
    msg["From"] = "info@ilmartinpescatore.com"
    msg["To"] = to_email

    msg.set_content(
        f"""
        Gentile {loan.first_name} {loan.last_name},

        il libro {loan.title} di {loan.author} preso in prestito il {loan.borrowed} 
        non risulta ancora restituito.

        Ti preghiamo di restituirlo al più presto.

        Grazie,
        La Biblioteca del Martin Pescatore Mosca Club
        """
        )

    # esempio con Gmail SMTP
    with smtplib.SMTP_SSL("smtps.aruba.it", 465) as smtp:
    ## with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        ## smtp.login("andrea.nardi.mail@gmail.com", "xiyq apim shld klau")
        smtp.login("info@ilmartinpescatore.com", "ilmartino")
        smtp.send_message(msg)

check_overdue_loans()
