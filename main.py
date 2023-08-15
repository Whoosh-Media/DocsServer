from flask import Flask, abort

from utils.download_docset import download_docset

app = Flask(__name__)


@app.route("/docs/<lib>")
def lib_page(lib: str):  # sourcery skip: assign-if-exp, reintroduce-else
    """Return docs for library"""
    if not lib:
        return abort(400, "No library specified")

    return f"{lib} docs"


@app.route("/files/*")
def files():
    """Files route"""
    return "Return files"


@app.route("/api/downloaded-docs")
def downloaded_docs():
    """Returns a list of all downloaded docsets"""
    return "Downloaded docsets!"


@app.route("/api/all-docs")
def all_docs():
    """Returns a list of all docsets and whether they are downloaded or not"""
    return "All docsets!"


@app.route("/api/download/<lib>")
async def download(lib: str):
    """Downloads the docset for the given library. Does NOT return it."""

    if not lib:
        return abort(400, "No library specified")

    res = await download_docset(lib)

    return f"Downloaded {lib}!" if res else f"Failed to download {lib}"


if __name__ == "__main__":
    app.run(debug=True)
