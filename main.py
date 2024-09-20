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
    """
    SMTP（简单邮件传输协议）主要使用以下端口进行邮件发送：
    端口 25：这是 SMTP 的标准端口。通常用于服务器之间的邮件传输。在许多网络环境中，这个端口可能会被 ISP 或防火墙阻止，用于防止垃圾邮件。
    端口 587：这是 SMTP 的另一个常用端口，专门用于客户端到邮件服务器的传输。它支持 STARTTLS，允许客户端与服务器之间进行加密连接。它是推荐的端口，用于发送邮件。
    端口 465：这是一个较老的 SMTP 端口，通常与 SMTPS（SMTP Secure）相关联，这是一种通过 SSL/TLS 加密的 SMTP 发送方式。虽然这个端口并不如 587 被广泛使用，但在某些配置中仍然可能被采用。
    """

    try:
        with smtplib.SMTP(config['smtp_server'], port=465, timeout=timeout) as s:
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
            timeout=30
        )
    except Exception as e:
        logging.error('Error send_email: %s', e)
        exit(1)

# Save current product name
with open('last_product.pickle', 'wb') as f:
    pickle.dump(productName, f)