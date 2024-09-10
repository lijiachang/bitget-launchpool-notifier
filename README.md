# bitget-launchpool-notifier
Monitoring Bitget launchpool and sending notifications；  
监控Bitget的launchpool币种上新 并发送邮件通知


This project monitors the Bitget Launchpool for new products and sends email notifications when a new product is detected.

## Setup

1. Clone the repository:
```
git clone https://github.com/lijiachang/bitget-launchpool-notifier.git
cd bitget-launchpool-notifier
```

2. Install the required packages:

```pip install -r requirements.txt```

3. Create a `config.ini` file in the project root with your email configuration:
```ini
[Email]
to = your_email@example.com
from_email = your_sender_email@example.com
smtp_server = smtp.example.com
smtp_password = your_smtp_password
```

## Usage
### Manual Execution

You can run the script manually for testing:

`python3 main.py`

### Cron Job Setup

For continuous monitoring, set up a cron job to run the script at regular intervals. Here's how to set it up to run every 10 minutes:

`crontab -e`

Add the following line (adjust the paths as necessary):


    */10 * * * * /usr/bin/python3 /path/to/bitget-launchpool-notifier/main.py >> /path/to/bitget-launchpool-notifier/cron.log 2>&1

This will run the script every 10 minutes and append both standard output and errors to cron.log.

Save and exit the crontab editor.


The script logs its activities to launchpool.log in the project directory. When run as a cron job, additional output is logged to cron.log.

## Troubleshooting
If you encounter any issues with the cron job:

    Check the cron.log file for any error messages.
    Ensure that all paths in the cron command are absolute paths.
    Make sure the script has the necessary permissions to run and write to log files.
    Verify that the Python environment used by cron has all the required packages installed.
