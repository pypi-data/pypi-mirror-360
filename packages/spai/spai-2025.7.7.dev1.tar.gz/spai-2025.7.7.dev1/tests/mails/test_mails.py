import pytest
from unittest.mock import patch
from spai.spai.mails.send import (
    send_mail,
    encode_file,
    get_filetype,
    curate_attachment,
)
from spai.spai.errors.mails import MailError


@pytest.fixture
def mock_mails_repo():
    with patch("spai.spai.mails.send.MailsRepo") as mock_repo:
        yield mock_repo.return_value


def test_send_mail_successful(mock_mails_repo):
    to = "recipient@example.com"
    subject = "Test Subject"
    body = "Test Body"

    mock_mails_repo.send.return_value.status_code = 200

    result = send_mail(to, subject, body)

    assert result == "Mail sent successfully"


def test_send_mail_failure(mock_mails_repo):
    to = "recipient@example.com"
    subject = "Test Subject"
    body = "Test Body"

    mock_mails_repo.send.return_value.status_code = 500

    with pytest.raises(MailError) as exc_info:
        send_mail(to, subject, body)

    assert "Email could not be sent." in str(exc_info.value)


def test_encode_file():
    path = "/path/to/file.txt"
    expected_encoded_file = "TW9ja2VkIGZpbGUgY29udGVudA=="

    with patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            b"Mocked file content"
        )
        result = encode_file(path)

    assert result == expected_encoded_file


def test_encode_file_file_not_found():
    path = "/nonexistent/file.txt"

    with pytest.raises(FileNotFoundError) as exc_info:
        encode_file(path)

    assert f"File {path} not found" in str(exc_info.value)


def test_get_filetype():
    path = "/path/to/file.txt"
    expected_filetype = "text/plain"

    result = get_filetype(path)

    assert result == expected_filetype


def test_get_filetype_unknown_extension(caplog):
    path = "/path/to/file.unknown"
    expected_filetype = "application/octet-stream"

    with pytest.warns(UserWarning):
        result = get_filetype(path)

    assert result == expected_filetype
    assert "MIMEType of" in caplog.text


def test_curate_attachment():
    path = "/path/to/attachment.txt"
    expected_attachment = {
        "filename": "attachment.txt",
        "encoded_file": "base64_encoded_content",
        "filetype": "text/plain",
    }

    with patch("spai.spai.mails.send.encode_file") as mock_encode_file:
        mock_encode_file.return_value = "base64_encoded_content"
        result = curate_attachment(path)

    assert result == expected_attachment
