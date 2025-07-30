import sys
import argparse
from shipyard_email.email_client import EmailClient
import shipyard_bp_utils as shipyard
from shipyard_email.utils.exceptions import (
    InvalidInputError,
)
from shipyard_templates import ShipyardLogger, Messaging, ExitCodeException

MAX_SIZE_BYTES = 10000000

logger = ShipyardLogger.get_logger()


def get_args():
    # TODO: Remove unused arguments when blueprints can be updated safely

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--send-method", dest="send_method", default="tls", required=False
    )
    parser.add_argument("--smtp-host", dest="smtp_host", required=True)
    parser.add_argument("--smtp-port", dest="smtp_port", default="", required=True)
    parser.add_argument(
        "--sender-address", dest="sender_address", default="", required=True
    )
    parser.add_argument("--sender-name", dest="sender_name", default="", required=False)
    parser.add_argument("--to", dest="to", default="", required=False)
    parser.add_argument("--cc", dest="cc", default="", required=False)
    parser.add_argument("--bcc", dest="bcc", default="", required=False)
    parser.add_argument("--username", dest="username", default="", required=False)
    parser.add_argument("--password", dest="password", default="", required=True)
    parser.add_argument("--subject", dest="subject", default="", required=False)
    parser.add_argument("--message", dest="message", default="", required=True)
    parser.add_argument(
        "--include-workflows-footer",
        dest="include_workflows_footer",
        default="TRUE",
        required=False,
    )

    args = parser.parse_args()
    if not (args.to or args.cc or args.bcc):
        raise InvalidInputError(
            "Email requires at least one recipient using --to, --cc, or --bcc"
        )
    return args


def main():
    try:
        args = get_args()
        sender_address = args.sender_address
        username = args.username or sender_address
        send_method = args.send_method.lower() or "tls"
        sender_address = sender_address
        username = username
        message = args.message

        client = EmailClient(
            args.smtp_host, args.smtp_port, username, args.password, send_method
        )

        client.send_message(
            sender_address=sender_address,
            message=message,
            sender_name=args.sender_name,
            to=args.to,
            cc=args.cc,
            bcc=args.bcc,
            subject=args.subject,
            include_footer=shipyard.args.convert_to_boolean(
                args.include_workflows_footer, default=True
            ),
        )

    except ExitCodeException as error:
        logger.error(error.message)
        sys.exit(error.exit_code)
    except Exception as e:
        logger.error(f"Failed to send email. {e}")
        sys.exit(Messaging.EXIT_CODE_UNKNOWN_ERROR)


if __name__ == "__main__":
    main()
