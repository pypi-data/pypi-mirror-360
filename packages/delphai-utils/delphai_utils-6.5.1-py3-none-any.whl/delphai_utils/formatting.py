from uuid import uuid5, NAMESPACE_URL
from datetime import datetime, timezone


def clean_url(url, keep_www=False):
    """
    Format and clean an url to be saved or checked.
    Args:
        url: url to be formatted
        keep_www: keep the 'www' part of the url
    Returns: formatted url
    """

    url = url.strip()
    url = url.replace("https://", "").replace("http://", "").rstrip("/")
    if not keep_www:
        url = url.replace("www.", "")
    split_url = url.split("/")
    split_url[0] = split_url[0].lower()
    return "/".join(split_url)


def get_clean_domain(url):
    """
    Format and clean an url and returns domain.
    Args:
        url: url to be formatted
    Returns: formatted domain
    """

    return clean_url(url).split("/")[0]


def create_blob_reference(url: str, timestamp: datetime, blob_type: str):
    """
    Creates a a blob reference using the domain of the URL, a UUID5 of the URL, the timestamps ISO format and the given blob type.
    Args:
        url: Url representing the blob
        timestamp: The timezone-aware timestamp of the blob
        blob_type: The type of the blob. Like "html" or "content"
    """

    if not timestamp.tzinfo:
        raise ValueError("timestamp must be timezone-aware")
    timestamp = timestamp.astimezone(timezone.utc)

    return f"{get_clean_domain(url)}/{uuid5(NAMESPACE_URL, url)}/{timestamp.isoformat()}/{blob_type}"
