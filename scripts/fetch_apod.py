#!/usr/bin/env python

import os
from dataclasses import dataclass
from typing import Optional

import httpx
from dataclass_wizard import JSONWizard


@dataclass
class APOD(JSONWizard):
    title: str
    explanation: str
    date: str
    hdurl: Optional[str] = None
    service_version: str
    copyright: Optional[str] = None
    media_type: str
    url: str
    credit: Optional[str] = None


def get_apod():
    """
    Retrieves the Astronomy Picture of the Day from the ellanan's APOD API.

    Raises:
        HTTP status code error if the response status code is not 200.

    Returns:
        APOD object parsed from the API response.
    """
    try:
        response = httpx.get("https://apod.ellanan.com/api")

        return APOD.from_dict(response.json())
    except httpx.HTTPStatusError as exc:
        raise exc


def download_apod(apod: APOD):
    """
    Downloads an APOD (Astronomy Picture of the Day) object and saves it
    in the current working directory.

    Args:
        apod (APOD): An APOD object containing information about the picture to download.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are insufficient permissions to download the file.
        httpx.TimeoutException: If the request to download the file times out.
        httpx.TooManyRedirects: If too many redirects occur while trying to download the file.
    """  # noqa: E501

    file_name = os.path.basename(apod.url)
    file_path = os.path.join(os.getcwd(), file_name)

    for _, _, files in os.walk(os.getcwd()):
        for file in files:
            if file == file_name:
                print(f"File {file_name} already exists.")
                exit()

    try:
        with httpx.stream("GET", apod.hdurl or apod.url) as response:
            with open(file_path, "wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
                print(f"Successfully downloaded {file_name}")
    except (httpx.TimeoutException, httpx.TooManyRedirects) as e:
        print(f"Error while downloading {file_name}: {e}")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File {file_name} does not exist.") from e
    except PermissionError as e:
        raise PermissionError(
            f"Insufficient permissions to download {file_name}"
        ) from e


def main():
    apod = get_apod()

    if not isinstance(apod, APOD):
        raise TypeError(f"Expected APOD, got {type(apod)}")

    download_apod(apod)


if __name__ == "__main__":
    main()
