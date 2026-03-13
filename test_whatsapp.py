"""
Quick test for WhatsApp confirmation via Meta Cloud API.
Usage: python test_whatsapp.py <phone_number>
Example: python test_whatsapp.py 9876543210
"""
import sys
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Add project root to path so utils can be imported
sys.path.insert(0, os.path.dirname(__file__))

from utils.whatsapp_service import send_whatsapp_confirmation

if len(sys.argv) < 2:
    print("Usage: python test_whatsapp.py <phone_number>")
    print("Example: python test_whatsapp.py 9876543210")
    sys.exit(1)

phone = sys.argv[1].strip()

# Fake booking to simulate a real confirmation
test_booking = {
    "_id": "TEST123456",
    "name": "Test Customer",
    "phone": phone,
    "date": "2026-04-10",
    "slot": "10:00 AM",
    "group_size": 4,
    "razorpay_payment_id": "pay_TestPaymentID001",
    "amount": 1300,
}

print(f"Sending WhatsApp confirmation to {phone}...")
success = send_whatsapp_confirmation(test_booking)

if success:
    print("SUCCESS: WhatsApp message sent! Check your WhatsApp.")
else:
    print("FAILED: Could not send. Check the error logs above.")
