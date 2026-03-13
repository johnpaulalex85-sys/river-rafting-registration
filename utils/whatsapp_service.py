"""
WhatsApp Confirmation Service using Meta WhatsApp Cloud API.
Sends booking confirmation after successful payment.

Setup:
1. Create a Meta Developer App at https://developers.facebook.com
2. Add "WhatsApp Business" product to your app
3. Get your Phone Number ID and a permanent Access Token
4. Set the environment variables below in your .env file
"""
import os
import logging
import requests

logger = logging.getLogger("whatsapp_service")

# Meta WhatsApp Cloud API endpoint
_META_API_URL = "https://graph.facebook.com/v19.0/{phone_number_id}/messages"


def _format_phone(phone: str) -> str:
    """
    Normalize phone number to E.164 format (no '+' sign, digits only).
    Meta API expects the number without the '+', e.g. 919876543210
    """
    digits = "".join(filter(str.isdigit, str(phone)))

    # Already has country code (12 digits starting with 91)
    if digits.startswith("91") and len(digits) == 12:
        return digits

    # 10-digit Indian number — prepend 91
    if len(digits) == 10:
        return f"91{digits}"

    return digits  # Return as-is for other formats


def send_whatsapp_confirmation(booking: dict) -> bool:
    """
    Send a WhatsApp booking confirmation using Meta's Cloud API.

    Uses a 'text' message type. For production with high volumes,
    use an approved WhatsApp Message Template instead.

    Required .env variables:
        WHATSAPP_ACCESS_TOKEN    - Meta permanent access token
        WHATSAPP_PHONE_NUMBER_ID - Your WhatsApp Business phone number ID

    Args:
        booking: The confirmed booking document from MongoDB.

    Returns:
        True if sent successfully, False otherwise.
    """
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

    if not access_token or not phone_number_id:
        logger.warning(
            "WhatsApp not configured: WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID "
            "missing in environment. Skipping confirmation."
        )
        return False

    # Get customer phone number
    phone = booking.get("phone") or booking.get("mobile") or booking.get("contact")
    if not phone:
        logger.warning(
            "No phone number found in booking %s. Skipping WhatsApp.", booking.get("_id")
        )
        return False

    to_number = _format_phone(phone)

    # Build confirmation message text
    name = booking.get("name") or booking.get("customer_name") or "Customer"
    date = booking.get("date") or "N/A"
    slot = booking.get("slot") or "N/A"
    group_size = booking.get("group_size") or "N/A"
    payment_id = booking.get("razorpay_payment_id") or "N/A"
    amount = booking.get("amount") or booking.get("advance_amount") or "N/A"
    booking_id = str(booking.get("_id", "N/A"))

    message_body = (
        f"✅ *Booking Confirmed!* 🎉\n\n"
        f"Hi {name},\n"
        f"Your river rafting booking is confirmed!\n\n"
        f"📅 *Date:* {date}\n"
        f"⏰ *Slot:* {slot}\n"
        f"👥 *Group Size:* {group_size}\n"
        f"🆔 *Booking ID:* {booking_id}\n"
        f"💳 *Payment ID:* {payment_id}\n"
        f"💰 *Amount Paid:* ₹{amount}\n\n"
        f"Thank you for booking with us!\n"
        f"See you at the river! 🚣‍♂️🌊"
    )

    url = _META_API_URL.format(phone_number_id=phone_number_id)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_body,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        msg_id = result.get("messages", [{}])[0].get("id", "unknown")
        logger.info(
            "WhatsApp confirmation sent to %s. Message ID: %s. Booking: %s",
            to_number,
            msg_id,
            booking_id,
        )
        return True

    except requests.exceptions.HTTPError as exc:
        error_body = exc.response.text if exc.response else ""
        logger.error(
            "Meta API HTTP error sending WhatsApp to %s for booking %s: %s -- %s",
            to_number,
            booking_id,
            exc,
            error_body,
        )
        print(f"Meta API Error Response: {error_body}")
        return False
    except Exception as exc:
        logger.error(
            "Failed to send WhatsApp confirmation to %s for booking %s: %s",
            to_number,
            booking_id,
            exc,
        )
        return False
