from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import escape
from datetime import datetime

def send_welcome_email(email_recipient, username):
    try:
        username = escape(username) 
        subject = "Welcome to ABCRM"
        from_email = settings.EMAIL_HOST_USER 
        to = [email_recipient]
        text_content = "Thank you for registering!" 
        current_year = datetime.now().year

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to ABCRM</title>
        </head>
        <body style="background: linear-gradient(to right, #1e293b, #0f172a); margin: 0; padding: 20px; font-family: Arial, sans-serif; color: #ffffff; text-align: center;">
            <div style="max-width: 600px; background-color: rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 30px; margin: auto; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);">
                <h1 style="font-size: 24px; font-weight: bold; color: #38bdf8; margin-bottom: 15px;">Welcome, {username}!</h1>
                <p style="font-size: 16px; color: #e2e8f0; line-height: 1.6; margin-bottom: 20px;">
                    Thank you for joining <b>ABCRM</b>, your go-to platform for managing employees, tracking tasks, and gathering feedback efficiently.
                </p>

                <ul style="text-align: left; padding-left: 20px; list-style-type: disc; margin-bottom: 20px;">
                    <li style="margin-bottom: 8px;"><b>Employee Management:</b> Organize employee data effortlessly.</li>
                    <li style="margin-bottom: 8px;"><b>Task Tracking:</b> Stay on top of project deadlines.</li>
                    <li style="margin-bottom: 8px;"><b>Feedback System:</b> Foster a culture of improvement.</li>
                    <li style="margin-bottom: 8px;"><b>Performance Reviews:</b> Gain deep insights into your team’s progress.</li>
                </ul>

                <a href="http://127.0.0.1:8000/"
                   style="display: inline-block; padding: 12px 20px; font-size: 16px; font-weight: bold;
                          background: linear-gradient(to right, #06b6d4, #3b82f6); color: #fff; 
                          text-decoration: none; border-radius: 8px; transition: 0.3s ease-in-out;
                          box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);">
                    Get Started Now
                </a>

                <p style="margin-top: 20px; font-size: 12px; color: #94a3b8;">&copy; {current_year} ABCRM. All Rights Reserved.</p>
            </div>
        </body>
        </html>
        """

        
        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False
