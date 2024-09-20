import requests
import json
import logging
from datetime import datetime
import pickle
import smtplib
from email.mime.text import MIMEText
import configparser

logging.basicConfig(filename='launchpool.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO
                    )

def from_timestamp(timestamp):
    timestamp = int(timestamp) // 1000
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object

def send_email(subject, body, config, timeout=30):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config['from_email']
    msg['To'] = config['to']

    try:
        with smtplib.SMTP(config['smtp_server'], timeout=timeout) as s:
            s.starttls()  # Start TLS for security
            s.login(config['from_email'], config['smtp_password'])
            s.sendmail(config['from_email'], [config['to']], msg.as_string())
        logging.info(f"Email sent successfully to {config['to']}")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred while sending email: {e}")
        raise

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['Email']

url = 'https://appapi.beeeye.xyz/v1/finance/launchpool/product/list'

headers = {
    'authority': 'www.bitget.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'apptheme': 'dark',
    'content-type': 'application/json;charset=UTF-8',
    'devicelanguage': 'zh_CN',
    'language': 'zh_CN',
    'locale': 'zh_CN',
    'origin': 'https://www.bitget.com',
    'referer': 'https://www.bitget.com/zh-CN/earn/launchpool',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'securitynew': 'true',
    'terminaltype': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}

data = {"pageNo":1,"matchType":0}

response = requests.post(url, headers=headers, data=json.dumps(data))
# logging.info('launchpool Response: %s', response.text)
try:
    items = response.json()['data']['items']
except Exception as e:
    logging.info('launchpool Response: %s', response.text)
    logging.error('Error: %s', e)
    exit(1)

last_product = items[0]
productName = last_product['productName']
startTime = last_product['startTime']
endTime = last_product['endTime']

logging.info('last productName:%s, %s -> %s', productName, from_timestamp(startTime), from_timestamp(endTime))

# Load last product name
try:
    with open('last_product.pickle', 'rb') as f:
        last_product_name = pickle.load(f)
except FileNotFoundError:
    last_product_name = None

if productName != last_product_name:
    email_config = load_config()
    logging.info('send_email to {}'.format(email_config['to']))

    try:
        send_email(
            'Bitget LaunchPool New product available',
            f'New product: {productName}, {from_timestamp(startTime)} -> {from_timestamp(endTime)}',
            email_config,
            timeout=60
        )
    except Exception as e:
        logging.error('Error send_email: %s', e)
        exit(1)

# Save current product name
with open('last_product.pickle', 'wb') as f:
    pickle.dump(productName, f)