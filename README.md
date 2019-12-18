# tm-mailgun
This module provides wrapper for [Mailgun APIs](https://documentation.mailgun.com/en/latest/api_reference.html).

## Installation
```bash
pip install tm-mailgun
```

## Usage
```python
import takeme_mailgun

API_KEY = 'xxxxxxxxxxxx'
DOMAIN = 'xxx.abc.jp'
EMAIL = 'hr@abc.jp'
MAIL_FROM = 'from@abc.jp'
MAIL_SUBJECT = 'Test Mail'
MAIL_BODY = 'Hello World'    

mailgun = takeme_mailgun.Mailgun(DOMAIN, API_KEY)
mailgun.mail_from = MAIL_FROM
if mailgun.is_valid(EMAIL):
    mailgun.messages(EMAIL, MAIL_SUBJECT, '', MAIL_BODY)
else:
    print('[{}] is an ivalid email.'.format(EMAIL))

if mailgun.is_delivered(EMAIL):
    print('[{}] is delivered successfully.'.format(EMAIL))
```

