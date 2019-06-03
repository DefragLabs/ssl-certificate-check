import ssl
import socket
import datetime

from botocore.vendored import requests

SLACK_WEBHOOK = "https://hooks.slack.com/services/********/******/****************"
TRACKING_DOMAINS = [
    'test@sample.com'
]


def ssl_expiry_date(domain_name):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=domain_name,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)
    conn.connect((domain_name, 443))
    ssl_info = conn.getpeercert()
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt).date()


def ssl_valid_time_remaining(domain_name):
    """Number of days left."""
    expires = ssl_expiry_date(domain_name)
    return expires - datetime.datetime.utcnow().date()


def notify_on_slack(msg):
    requests.post(SLACK_WEBHOOK, json={"text": msg})


# Main section
def lambda_handler(event, context):
    msg = "*SSL Certificate check service - {} UTC* \n\n".format(str(datetime.datetime.utcnow().date()))
    for domain in TRACKING_DOMAINS:
        expiry_date = ssl_valid_time_remaining(domain.strip())
        (a, b) = str(expiry_date).split(',')
        (c, d) = a.split(' ')
        if int(c) < 15:
            msg = "> Certificate for `{}` expires in `{}` days <!channel> \n".format(domain, str(c)) + msg
        else:
            msg += "> Certficate for `{}` expires in `{}` days \n".format(domain, str(c))

    notify_on_slack(msg)
