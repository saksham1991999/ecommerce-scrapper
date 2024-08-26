import os
import ssl
from typing import Optional
from urllib.parse import urlparse

import aiofiles
import aiohttp


async def download_image(url: str, save_dir: str) -> Optional[str]:
    """
    Download an image from a URL and save it locally.

    Args:
        url (str): The URL of the image to download.
        save_dir (str): The directory where the image should be saved.

    Returns:
        Optional[str]: The local path of the saved image if successful, None otherwise.

    Raises:
        aiohttp.ClientError: If there's an error during the HTTP request.
        IOError: If there's an error writing the file.
    """
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.basename(urlparse(url).path)
    local_path = os.path.join(save_dir, filename)

    # Create a custom SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=ssl_context) as response:
                if response.status == 200:
                    async with aiofiles.open(local_path, mode='wb') as f:
                        await f.write(await response.read())
                    return local_path
                else:
                    print(f"Failed to download image. Status code: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Error during HTTP request: {str(e)}")
    except IOError as e:
        print(f"Error writing file: {str(e)}")

    return None
