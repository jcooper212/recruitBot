import requests

# Set your Square API access token
access_token = "EAAAly5KjqBnmdkqta6OOFn1sTGYM66QmFMnTXuIxvGT-vmbIKMFtW1rrvL2EpuS"

# Square API endpoint for creating an invoice
url = "https://connect.squareup.com/v2/invoices"

# Request headers
headers = {
    "Square-Version": "2024-01-18",
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

# Request payload for creating an invoice
data = {
    "idempotency_key": "ce3748f9-5fc1-4762-aa12-aae5e843f1f4",
    "invoice": {
        "location_id": "ES0RJRZYEC39A",
        "order_id": "CAISENgvlJ6jLWAzERDzjyHVybY",
        "scheduled_at": "2030-01-13T10:00:00Z",
        "primary_recipient": {
            "customer_id": "JDKYHBWT1D4F8MFH63DBMEN8Y4"
        },
        "delivery_method": "EMAIL",
        "payment_requests": [
            {
                "request_type": "BALANCE",
                "due_date": "2030-01-24",
                "tipping_enabled": True,
                "automatic_payment_source": "NONE",
                "reminders": [
                    {
                        "message": "Your invoice is due tomorrow",
                        "relative_scheduled_days": -1
                    }
                ]
            }
        ],
        "invoice_number": "inv-100",
        "title": "Event Planning Services",
        "description": "We appreciate your business!",
        "accepted_payment_methods": {
            "card": True,
            "square_gift_card": False,
            "bank_account": False,
            "buy_now_pay_later": False,
            "cash_app_pay": False
        },
        "custom_fields": [
            {
                "label": "Event Reference Number",
                "value": "Ref. #1234",
                "placement": "ABOVE_LINE_ITEMS"
            },
            {
                "label": "Terms of Service",
                "value": "The terms of service are...",
                "placement": "BELOW_LINE_ITEMS"
            }
        ],
        "sale_or_service_date": "2030-01-24",
        "store_payment_method_enabled": False
    }
}

# Make the API request
response = requests.post(url, headers=headers, json=data)

# Check the response
if response.status_code == 200:
    print("Invoice created successfully!")
    print(response.json())
else:
    print("Error creating invoice:")
    print(response.status_code, response.text)
