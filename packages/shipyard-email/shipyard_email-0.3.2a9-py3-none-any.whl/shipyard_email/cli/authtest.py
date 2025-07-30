# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "shipyard-email",
# ]
# ///
import os
import sys
from shipyard_email.email_client import EmailClient


def main():
    sys.exit(
        EmailClient(
            smtp_host=os.environ["EMAIL_SMTP_HOST"],
            smtp_port=int(os.environ["EMAIL_SMTP_PORT"]),
            username=os.environ["EMAIL_USERNAME"],
            password=os.environ["EMAIL_PASSWORD"],
            send_method="tls",
        ).connect()
    )


if __name__ == "__main__":
    main()
