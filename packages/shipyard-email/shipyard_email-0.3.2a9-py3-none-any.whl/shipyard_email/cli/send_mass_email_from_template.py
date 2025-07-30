import sys
import argparse
from shipyard_email.email_client import EmailClient
from shipyard_email.utils import exceptions
import shipyard_bp_utils as shipyard
from shipyard_templates import ShipyardLogger, Messaging, ExitCodeException
import pandas as pd
import re
import os

MAX_SIZE_BYTES = 10000000
FILE_PATTERN = re.compile(r"\{\{[^\{\}]+\}\}")

logger = ShipyardLogger.get_logger()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file-name", dest="input_file_name", required=True)
    parser.add_argument(
        "--template", dest="template", required=True
    )
    parser.add_argument(
        "--send-method", dest="send_method", default="tls", required=False
    )
    parser.add_argument("--smtp-host", dest="smtp_host", required=True)
    parser.add_argument("--smtp-port", dest="smtp_port", default="", required=True)
    parser.add_argument(
        "--sender-address", dest="sender_address", default="", required=True
    )
    parser.add_argument("--sender-name", dest="sender_name", default="", required=False)
    parser.add_argument("--cc", dest="cc", default="", required=False)
    parser.add_argument("--bcc", dest="bcc", default="", required=False)
    parser.add_argument("--username", dest="username", default="", required=True)
    parser.add_argument("--password", dest="password", default="", required=True)
    parser.add_argument(
        "--include-workflows-footer",
        dest="include_workflows_footer",
        default="TRUE",
        required=False,
    )

    args = parser.parse_args()
    return args


def main():
    try:
        args = get_args()
        sender_address = args.sender_address
        username = args.username or sender_address

        _, input_file_type = os.path.splitext(args.input_file_name)
        template = args.template

        if input_file_type != ".csv":
            raise exceptions.InvalidFileInputError(
                f"Invalid file type `{args.input_file_name}`. Input file must be '.csv'"
            )

        if not os.path.exists(args.input_file_name):
            raise exceptions.InvalidFileInputError(
                f"{args.input_file_name} does not exist"
            )

        input_table = pd.read_csv(args.input_file_name)
        for replaceable in FILE_PATTERN.findall(template):
            if replaceable[2:7] == "text:":
                template = template.replace(replaceable, Messaging.message_content_file_injection(replaceable).strip(), 1)

        for replaceable in FILE_PATTERN.findall(template):
            if replaceable[2:-2] not in input_table.columns:
                raise exceptions.InvalidFileInputError(
                    f"'{replaceable[2:-2]}' is neither a column in '{args.input_file_name}' nor is formatted as a file injection."
                )

        for index, row in input_table.iterrows():
            message = template
            for col_name in input_table.columns:
                message = message.replace(f"{{{{{col_name}}}}}", str(row[col_name]))
            send_method = args.send_method.lower() or "tls"
            sender_address = sender_address
            username = username
            message = message

            cc = row.get("cc", "")
            bcc = row.get("bcc", "")

            client = EmailClient(
                args.smtp_host, args.smtp_port, username, args.password, send_method
            )

            client.send_message(
                sender_address=sender_address,
                message=message,
                sender_name=args.sender_name,
                to=str(row["recipient_address"]),
                cc=cc,
                bcc=bcc,
                subject=str(row["subject"]),
                include_footer=args.include_workflows_footer,
                inject_files=False,
            )

    except ExitCodeException as error:
        logger.error(error.message)
        sys.exit(error.exit_code)
    except Exception as e:
        logger.error(f"Failed to send email. {e}")
        sys.exit(Messaging.EXIT_CODE_UNKNOWN_ERROR)


if __name__ == "__main__":
    main()
