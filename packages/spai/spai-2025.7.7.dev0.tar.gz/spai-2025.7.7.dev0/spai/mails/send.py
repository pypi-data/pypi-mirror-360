"""
Module for sending emails
"""
import base64
import logging
import warnings

from typing import List, Union
from os.path import basename, splitext

from .mimetypes import MIMETYPES
from ..errors import MailError
from ..repos.MailsRepo import MailsRepo

logger = logging.getLogger(__name__)

ACCEPTED_RESPONSES = (200, 201, 202)


def send_mail(
    to: Union[List, str],
    subject: str,
    body: str,
    attachment: Union[List, str, None] = None,
):
    """
    Send an email.

    Parameters
    ----------
    to : Union[str, List]
        The email address of the recipient
    subject : str
        The subject of the email
    body : str
        The body of the email
    attachment : Union[List, str, None], optional
        The attachment of the email, if needed, by default None
    """
    mails_repo = MailsRepo()

    body = {"to": to, "subject": subject, "body": body}  # TODO validate

    if attachment:
        if isinstance(attachment, str):
            attach = curate_attachment(attachment)
        elif isinstance(attachment, list):
            attach = [curate_attachment(path) for path in attachment]

        body["attachment"] = attach

    r = mails_repo.send(body)

    if r.status_code not in ACCEPTED_RESPONSES:
        m = f"Email could not be sent. Response: {r.status_code}; Reason: {r.reason}, {r.text}"
        raise MailError(m)

    return "Mail sent successfully"


def encode_file(path: str):
    """
    Encode a file to base64

    Parameters
    ----------
    path : str
        Path to the file to encode

    Returns
    -------
    str
        The encoded file
    """
    try:
        with open(path, "rb") as f:
            data = f.read()
            f.close()
    except FileNotFoundError:
        m = f"File {path} not found"
        logger.error(m)
        raise FileNotFoundError(m)

    encoded_file = base64.b64encode(data).decode()

    return encoded_file


def get_filetype(path: str):
    """
    Get the filetype of a file

    Parameters
    ----------
    path : str
        Path to the file

    Returns
    -------
    filetype
        The filetype of the file

    Raises
    ------
    Exception
        If the filetype cannot be guessed
    """
    ext = splitext(path)[1]

    if ext in MIMETYPES:
        filetype = MIMETYPES[ext]
    else:
        filetype = "application/octet-stream"
        m = f"MIMEType of {path} is not in MIMETYPES, assuming {filetype}"
        logger.warning(m)
        warnings.warn(m)

    return filetype


def curate_attachment(path: str):
    """
    Curate an attachment to be sent

    Parameters
    ----------
    path : str
        Path to the file to attach

    Returns
    -------
    dict
        The attachment to be sent
    """
    encoded_file = encode_file(path)
    filetype = get_filetype(path)
    filename = basename(path)

    return {"filename": filename, "encoded_file": encoded_file, "filetype": filetype}
