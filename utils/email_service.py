import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_booking_email(booking, is_success=True):
    sender_email = os.environ.get("GMAIL_EMAIL")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not sender_email or not sender_password:
        logger.error("Gmail credentials missing in environment variables. Cannot send email.")
        return False

    recipient_email = booking.get("email") or booking.get("booking_details", {}).get("email")
    if not recipient_email:
        logger.warning(f"No email found for booking {booking.get('_id', 'unknown')}")
        return False

    user_name = booking.get("user_name") or booking.get("booking_details", {}).get("name") or "Valued Customer"
    date = booking.get("date") or "N/A"
    slot = booking.get("slot") or "N/A"
    amount = booking.get("amount") or "N/A"
    order_id = booking.get("razorpay_order_id") or "N/A"
    
    msg = MIMEMultipart()
    msg['From'] = f"River Rafting <{sender_email}>"
    msg['To'] = recipient_email
    
    if is_success:
        msg['Subject'] = "Booking Confirmed - Your Rafting Adventure Awaits!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #f4fdfa; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #c2f0dc;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #059669; margin: 0;">Payment Successful!</h2>
                </div>
                <p>Dear <strong>{user_name}</strong>,</p>
                <p>Your booking has been successfully confirmed and payment is received. We are excited to host you!</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">Order ID</td>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{order_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">Date</td>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">Slot</td>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{slot}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">Amount Paid</td>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹{amount}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Status</td>
                        <td style="padding: 10px; color: #059669; font-weight: bold;">Confirmed</td>
                    </tr>
                </table>
                <p style="margin-top: 20px;">We look forward to seeing you. Please arrive at least 30 minutes before your slot.</p>
                <p>Best regards,<br><strong>The River Rafting Team</strong></p>
            </div>
        </body>
        </html>
        """
    else:
        msg['Subject'] = "Payment Failed - Action Required for Your Booking"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #fef2f2; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; border: 1px solid #fecaca;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #dc2626; margin: 0;">Payment Failed</h2>
                </div>
                <p>Dear <strong>{user_name}</strong>,</p>
                <p>Unfortunately, the payment for your recent booking attempt was unsuccessful.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">Order ID</td>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{order_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">Date</td>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">Slot</td>
                        <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{slot}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Status</td>
                        <td style="padding: 10px; color: #dc2626; font-weight: bold;">Payment Failed</td>
                    </tr>
                </table>
                <p style="margin-top: 20px;">Your seats have not been reserved. Please try processing the payment again or contact our support team if you need assistance.</p>
                <p>Best regards,<br><strong>The River Rafting Team</strong></p>
            </div>
        </body>
        </html>
        """

    msg.attach(MIMEText(html_body, 'html'))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        logger.info(f"Successfully sent {'success' if is_success else 'failure'} email to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        return False
