import requests
import os # For path manipulation and checking directories

def download_file_requests(url, save_path=None):
    """
    Downloads a file from a given URL using the requests library.

    Args:
        url (str): The URL of the file to download.
        save_path (str, optional): The full path including filename to save the file.
                                   If None, it tries to infer from URL or uses a default.
    Returns:
        str: The path where the file was saved, or None if download failed.
    """
    if save_path is None:
        # Try to infer filename from URL
        filename = url.split('/')[-1]
        if '?' in filename: # Remove query parameters if present
            filename = filename.split('?')[0]
        if not filename:
            filename = "downloaded_file" # Default if no filename in URL
        save_path = os.path.join(os.getcwd(), filename) # Save in current directory

    try:
        # Send a GET request to the URL
        # stream=True allows iterating over the response content, good for large files
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)

        # Open the file in binary write mode
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                # Write each chunk to the file
                file.write(chunk)

        print(f"File downloaded successfully to: {save_path}")
        return save_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None