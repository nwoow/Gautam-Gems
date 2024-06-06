import random
import requests


def send_otp_to_phone(phone_number):
    try:
        otp =random.randint(100000, 999999)
        url = f"https://api.authkey.io/request?authkey=ea048f1e37474761&mobile={phone_number}&country_code=91&sid=8732&company=DECORLINE&otp={otp}"
        response = requests.get(url)
        return otp

    except Exception as e:
        print(e)