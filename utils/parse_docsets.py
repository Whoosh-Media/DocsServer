"""Utilty functions for fetching & parsing local docsets"""
from pathlib import Path
from xml.etree.ElementTree import ElementTree, Element
from .constants import DOCSET_FOLDER


def find_docset(lib: str) -> str | None:
    """Find and return the docset for a given library

    Args:
        lib (str): Library name

    Returns:
        str | None: Docset file path
    """
    docset = next(
        (
            docset
            for docset in Path(DOCSET_FOLDER).iterdir()
            if docset.name.startswith(lib)
        ),
        None,
    )
    return None if docset is None else str(docset)


def parse_docset(docset: str | None) -> str | None:
    """Find the plist file for a given docset.

    Args:
        docset (str | None): docset file path

    Returns:
        str | None: Plist file path for the docset
    """
    if docset is None:
        return None

    return next(iter(Path(docset).glob("**/Info.plist")), None)


def parse_plist(plist: str) -> str | None:
    """Parse the docset plist to find the root page.

    Args:
        plist (str): File path of plist file

    Returns:
        str | None: File path of root page
    """
    tree = ElementTree()
    tree.parse(plist)
    root = tree.getroot()

    dash_index_file_path = find_dash_index_file_path(root)
    if dash_index_file_path is not None:
        print(f"Found dashIndexFilePath: {dash_index_file_path}")
    else:
        print("Could not find dashIndexFilePath")

    return dash_index_file_path


def find_dash_index_file_path(element: Element) -> str | None:
    """Recursively search for the dashIndexFilePath key in an XML element.

    Args:
        element (ElementTree.Element): Root element

    Returns:
        str | None: Value of dashIndexFilePath key
    """
    if "dashIndexFilePath" in element.attrib:
        return element.attrib["dashIndexFilePath"]
    for child in element:
        result = find_dash_index_file_path(child)
        if result is not None:
            return result
    return None
