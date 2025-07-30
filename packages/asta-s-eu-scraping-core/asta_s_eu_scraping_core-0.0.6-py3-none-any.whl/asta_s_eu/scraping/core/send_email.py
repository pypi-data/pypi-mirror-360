from typing import Any, Optional, Sequence, cast

import datetime
import json
import logging
import smtplib
import socket
from dataclasses import dataclass
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from textwrap import dedent

import retry
from jinja2 import BaseLoader, Environment

from .config import CONFIG_DIR
from .typing import Prospects

LOG = logging.getLogger(__name__)


@dataclass
class Email:  # pylint: disable=too-many-instance-attributes
    """
    Wrap all common many parameters for send_email in one structure
    to remove verbosity in signature for functions
    """
    sender: str  # 'from' nane is reserved
    to: str
    subject: str
    password: str
    html: str
    text: Optional[str] = None
    smtp_host: str = 'smtp.gmail.com'
    smtp_port: int = 587
    files: Sequence[Path] = tuple()


def _render_template(template: str, **template_kwargs: Any) -> str:
    the_template = Environment(loader=cast(BaseLoader, Optional)).from_string(template)
    return the_template.render(hostname=socket.gethostname(), **template_kwargs)


def _prospects_to_email_content(template: str, prospects: Prospects) -> str:
    return _render_template(template, prospects=prospects)


@retry.retry(ConnectionRefusedError, tries=3, delay=5)
def send_any_email(email: Email) -> None:
    """
    credits to https://stackoverflow.com/a/26369282
    """
    LOG.info('Prepare to send email with subject %r', email.subject)
    #
    # if no connection fail before build payload
    #

    # Send the message via local SMTP server.
    mail = smtplib.SMTP(email.smtp_host, email.smtp_port)
    mail.ehlo()
    mail.starttls()
    mail.login(email.sender, email.password)

    #
    # build payload
    #

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = email.subject
    msg['From'] = email.sender
    msg['To'] = email.to

    LOG.info("Sending email with subject %r...", email.subject)

    if email.text:
        # Record the MIME types of both parts - text/plain and text/html.
        text_part = MIMEText(email.text, 'plain')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(text_part)

    # Record the MIME types of both parts - text/plain and text/html.
    html_part = MIMEText(email.html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(html_part)

    for path in email.files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(path.read_bytes())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={path.name}')
        msg.attach(part)

    #
    # send payload
    #

    # TODO write an integration test to test email send
    mail.sendmail(f'-SB- <{email.sender}>', email.to, msg.as_string())

    mail.quit()


def _prospects_to_html(prospects: Prospects) -> str:
    template = Path(__file__).parent.joinpath(  # pylint: disable=unspecified-encoding
        "prospects.jinja2.html"
    ).read_text()
    return _prospects_to_email_content(template, prospects=prospects)


def _prospects_to_txt(prospects: Prospects) -> str:
    return _prospects_to_email_content(dedent("""
            {% for prospect in prospects %}   
            index: {{ loop.index }}
            link: {{ prospect['link'] }} 	
            price: {{ prospect['price'] }}
            title: {{ prospect['text'] }}
            img: {{ prospect['img'] }}
            -----
            {% endfor %}    
        """), prospects=prospects)


def _log_prospects(subject: str, prospects: Prospects) -> None:
    now = datetime.datetime.now(datetime.UTC)

    dumps = json.dumps(prospects, indent=4)
    CONFIG_DIR.joinpath(  # pylint: disable=unspecified-encoding
        f"last.{now:%Y-%m-%dT%H:%M:%S}-{subject}.json"
    ).write_text(dumps)


def gmailing_prospects(from_: str,
                       to: str,
                       subject: str,
                       password: str,
                       prospects: Prospects) -> None:
    """
    Send prospects to an email via gmail account
    """
    text = _prospects_to_txt(prospects)
    html = _prospects_to_html(prospects)

    send_any_email(
        Email(
            sender=from_,
            to=to,
            subject=subject,
            password=password,
            text=text,
            html=html
        )
    )

    _log_prospects(subject, prospects)


def gmailing_logs(logs: str, email: Email) -> None:
    """
    In case of some alarms detected email them
    """
    email.text = logs
    email.html = _render_template(dedent("""
        <!DOCTYPE html>
        <html>
            <head>
                
            </head>
            <body> 
                <pre>  
                    {{ logs }}
                </pre>
                <sub>{{ hostname }}</sub> 
            </body>
        </html>
        """), logs=logs)

    send_any_email(email)
