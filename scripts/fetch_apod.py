#!/usr/bin/env python
"""
A simple script to download the latest APOD from the NASA API.

Packages used:
- [httpx](https://www.python-httpx.org/) for API requests.
- [tqdm](https://tqdm.github.io/) for showing progress bar while downloading the image.
"""
import logging as logger
import os

logger.basicConfig(level=logger.INFO)

try:
    import httpx
    from httpx import HTTPStatusError, TimeoutException, TooManyRedirects
    from tqdm import tqdm
except ImportError:
    logger.critical(
        "Opps! Looks like some dependencies are missing! Please install them and try again later."  # noqa: E501
    )


def get_apod_url():
    """Retrieve the url of the Astronomy Picture of the Day from the ellanan's APOD API.

    Raises:
        HTTPStatusError: if the response status code is not 200.

    Returns:
        The url to the APOD image.
    """
    try:
        response = httpx.get("https://apod.ellanan.com/api").json()
        logger.info("Successfully retrieved the latest APOD.")
        hdurl = response["hdurl"]
        return hdurl if hdurl else response["url"]
    except HTTPStatusError as exc:
        raise exc


def get_and_check_file_path(url):
    """Check if the file already exists and returns the path to the file.

    Args:
        url: The URL of the image to download.

    Returns:
        The name & path to the image file.
    """
    name = os.path.basename(url)
    path = os.path.join(os.getcwd(), name)

    for _, _, files in os.walk(os.getcwd()):
        for file in files:
            if file == name:
                raise FileExistsError(f"File {name} already exists.")

    return name, path


def download_apod():
    """
    Downloads an APOD (Astronomy Picture of the Day) object and saves it
    in the current working directory.

    Args:
        apod: An dit containing information about the picture to download.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are insufficient permissions to download the file.
        TimeoutException: If the request to download the file times out.
        TooManyRedirects: If too many redirects occur while accessing the file.
    """
    url = get_apod_url()
    file_name, file_path = get_and_check_file_path(url)

    try:
        logger.info("Downloading the latest APOD image...")
        with open(file_path, "wb") as file:
            with httpx.stream("GET", url) as response:
                total = int(response.headers["Content-Length"])

                with tqdm(
                    total=total, unit_scale=True, unit_divisor=1024, unit="B"
                ) as progress:
                    num_bytes_downloaded = response.num_bytes_downloaded

                    for chunk in response.iter_bytes():
                        file.write(chunk)
                        progress.update(
                            response.num_bytes_downloaded - num_bytes_downloaded
                        )
                        num_bytes_downloaded = response.num_bytes_downloaded

        logger.info(f"Successfully downloaded {file_name}")
    except (TimeoutException, TooManyRedirects) as e:
        logger.error(f"Error while downloading {file_name}: {e}")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File {file_name} does not exist.") from e
    except PermissionError as e:
        raise PermissionError(
            f"Insufficient permissions to download {file_name}"
        ) from e


def main():
    download_apod()


if __name__ == "__main__":
    main()
