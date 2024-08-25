import aiohttp
import aiofiles
import os
import ssl
from urllib.parse import urlparse

async def download_image(url: str, save_dir: str) -> str:
    """
    Download an image from a URL and save it locally.
    Returns the local path of the saved image.
    """
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.basename(urlparse(url).path)
    local_path = os.path.join(save_dir, filename)

    # Create a custom SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ssl_context) as response:
            if response.status == 200:
                async with aiofiles.open(local_path, mode='wb') as f:
                    await f.write(await response.read())
                return local_path
    return ""