from typing import List,Optional
import os, logging, aiohttp, asyncio
from tqdm.asyncio import tqdm

async def download_files(urls: List[str], destination_folder: str, authorization: str = None):
    tasks = [download_file(file, os.path.join(destination_folder, os.path.basename(file)), authorization=authorization) for file in urls]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    for i, result in enumerate(results):
        if not result:
            raise Exception(f"Download failed for file: {urls[i]}")

async def download_file(url: str, destination: str, chunk_size: int = 8192, authorization: str = None) -> Optional[str]:
  """
  Downloads a file from a given URL to a destination path asynchronously.

  Args:
      url: The URL of the file to download
      destination: The local path where the file should be saved
      chunk_size: Size of chunks to download (default: 8192 bytes)

  Returns:
      str: Path to the downloaded file if successful, None otherwise

  Raises:
      Various exceptions are caught and logged
  """
  try:
      # Ensure the destination directory exists
      os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)

      async with aiohttp.ClientSession() as session:
          if authorization:
            headers = {'Authorization': authorization}
            session.headers.update(headers)
          async with session.get(url) as response:
              # Check if the request was successful
              if response.status != 200:
                  logging.error(f"Failed to download file. Status code: {response.status}")
                  return None

              # Get the total file size if available
              total_size = int(response.headers.get('content-length', 0))
              # Open the destination file and write chunks
              with open(destination, 'wb') as f:
                  with tqdm(
                      total=total_size,
                      desc="Downloading",
                      unit='B',
                      unit_scale=True,
                      unit_divisor=1024
                  ) as pbar:
                      async for chunk in response.content.iter_chunked(chunk_size):
                          if chunk:
                              f.write(chunk)
                              pbar.update(len(chunk))

              logging.info(f"File downloaded successfully to {destination}")
              return destination

  except aiohttp.ClientError as e:
      logging.error(f"Network error occurred: {str(e)}")
      return None
  except asyncio.TimeoutError:
      logging.error("Download timed out")
      return None
  except IOError as e:
      logging.error(f"IO error occurred: {str(e)}")
      return None
  except Exception as e:
      logging.error(f"Unexpected error occurred: {str(e)}")
      return None
  finally:
      # If download failed and file was partially created, clean it up
      if os.path.exists(destination) and os.path.getsize(destination) == 0:
          try:
              os.remove(destination)
              logging.info(f"Cleaned up incomplete download: {destination}")
          except OSError:
              pass
