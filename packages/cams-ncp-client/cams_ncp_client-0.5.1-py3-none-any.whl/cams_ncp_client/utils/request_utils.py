from pathlib import Path

import requests


def download_file(response: requests.Response, output_path: Path | str, chunk_size=8192) -> Path:
    """
    Download a file from a requests.Response object and save it to the specified output path.
    Args:
        response (requests.Response): The response object containing the file data.
        output_path (Path | str): The directory where the file will be saved.
    Returns:
        The path to the downloaded file.
    """
    # Raise exception for HTTP errors
    response.raise_for_status()
    if not isinstance(output_path, Path):
        output_path = Path(output_path)
    # Get filename from Content-Disposition header or create a default one
    filename = None
    content_disposition = response.headers.get("Content-Disposition")
    if content_disposition:
        import re

        filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
        if filename_match:
            filename = filename_match.group(1)

    if not filename:
        raise ValueError("Filename not found in response headers. Please specify the output path.")

    # Determine the output file path
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / filename

    # Write the file
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)

    return file_path