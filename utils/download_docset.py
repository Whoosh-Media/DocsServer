"""Utilty functions for fetching & parsing local docsets"""
import asyncio
import os
from pathlib import Path
import tarfile

import aiofiles
import aiohttp
from lxml import etree

from .constants import DOCSET_FOLDER, FEEDS_FOLDER


async def find_xml(lib: str) -> str | None:
    """Find and return the xml feed for a given library

    Args:
        lib (str): Library name

    Returns:
        str | None: Docset file path
    """
    xml = next(
        (
            docset
            for docset in Path(FEEDS_FOLDER).iterdir()
            if docset.name.startswith(lib)
        ),
        None,
    )
    return None if xml is None else str(xml)


async def download_docset(lib: str) -> str:
    """Download docset and return file path to .docset file/folder

    Args:
        lib (str): Library name for downloading

    Returns:
        str: File path
    """
    xml_file_path = await find_xml(lib)

    if not xml_file_path:
        print(f"Could not find xml file for {lib}")
        return None

    print(f"Found xml file for {lib} at {xml_file_path}")

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_file_path, parser)
    root = tree.getroot()

    if download_urls := root.xpath("./url[contains(text(), 'london')]/text()"):
        download_url = download_urls[0]
        print(f"Downloading {lib} from {download_url}")
        tar_file_path = await download_file(download_url)
        if not tar_file_path:
            print(f"Could not download {lib} from {download_url}")
            return None
        return await extract_docset(tar_file_path)
    else:
        print(f"Could not find download URL for {lib}")
        return None


async def download_file(url: str) -> str | None:
    """Downloads the tgz file for the docset

    Args:
        url (str): URL of the docset in the CDN

    Returns:
        str | None: Returns the file path of the downloaded file
    """

    print(f"Downloading {url}")
    docset_filename = url.split("/")[-1]
    print(f"Saving to {docset_filename}")
    docset_filepath = Path(DOCSET_FOLDER) / docset_filename
    print(docset_filepath)

    if docset_filepath.exists():
        print(f"File already exists at {docset_filepath} - skipping download")
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as response:
                if response.status == 200:
                    print("200 response")
                    async with aiofiles.open(docset_filepath, "wb") as file:
                        await file.write(await response.read())
                    print(f"Downloaded {url} to {docset_filepath}")
                    return docset_filepath
                else:
                    print(f"Failed to download {url} - status code {response.status}")
                    return None

    except Exception as err:  # noqa: F841
        # print(f"Failed to download {url} - {err}")
        return None


async def extract_docset(file_path: str) -> str:
    # sourcery skip: remove-unnecessary-cast
    """Extracts the docset from the tgz file

    Args:
        file_path (str): Path to the tgz file

    Returns:
        str: File path of the .docset file/folder
    """
    with tarfile.open(file_path, "r:gz") as tar:
        await asyncio.to_thread(tar.extractall, path=DOCSET_FOLDER)

    os.remove(file_path)

    return str(
        Path(DOCSET_FOLDER) / str(file_path).split("/")[-1].replace(".tgz", ".docset")
    )
