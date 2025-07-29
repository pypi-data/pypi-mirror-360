from django.core.mail import EmailMultiAlternatives


class Messaging:
    
    @staticmethod
    def send_email(data: dict) -> None:
        msg = EmailMultiAlternatives(data['subject'], data['text'], data['from'], data['to'])
        msg.attach_alternative(data['html'], "text/html")
        msg.send()
    

    @staticmethod
    def send_sms(data: dict) -> None:
        uri_data = "{u}/send?From={f}&To={to}&Content={body}&ClientID={id}&ClientSecret={secret}&registredDelivery=true"
        # full_url = str(uri_data).format(
        #     u=settings.SMS_CONFIG['URL'],
        #     from=data['from'],
        #     to=data['to'],
        #     body=data['body'],
        #     id=settings.SMS_CONFIG['Id'],
        #     secret=settings.SMS_CONFIG['Secret']
        # )
        # sms_req = requests.get(full_url, data=None, headers=None)
