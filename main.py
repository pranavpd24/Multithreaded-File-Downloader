# Importing used modules
import threading
import requests
import os

# Function for downloading chunks
def download_chunk(url, start, end, chunk_num):
    """
    Downloads a chunk of the file from the given URL.

    Parameters:
    url (str): The URL of the file to download.
    start (int): The starting byte of the chunk.
    end (int): The ending byte of the chunk.
    chunk_num (int): The chunk number for naming the file.
    """
    headers = {"Range": f"bytes={start}-{end}"}
    response = requests.get(url, headers=headers, stream=True)
    with open(f"chunk_{chunk_num}", "wb") as chunk_file:
        chunk_file.write(response.content)

# Function for merging all downloaded chunks
def merge_chunk(chunk_count, output_file):
    """
    Merges all the downloaded chunks into a single file.

    Parameters:
    chunk_count (int): The number of chunks to merge.
    output_file (str): The name of the final output file.
    """
    with open(output_file, "wb") as output_file:
        for i in range(chunk_count):
            with open(f"chunk_{i}", "rb") as chunk_file:
                output_file.write(chunk_file.read())
            os.remove(f"chunk_{i}")

# Main Function Creating Threads for each chunk of data and merging all downloaded chunks
def main_function(url, output_file, chunk_size):
    """
    Main function to download a file using multiple threads and merge the chunks.

    Parameters:
    url (str): The URL of the file to download.
    output_file (str): The name of the final output file.
    chunk_size (int): The size of each chunk in bytes.
    """
    # Get the final URL after redirections
    response = requests.head(url, allow_redirects=True)
    final_url = response.url

    # Get the total file size
    file_size = int(response.headers['Content-Length'])

    # Calculate the number of chunks
    chunk_count = file_size // chunk_size + (1 if file_size % chunk_size else 0)

    # Create threads for downloading each chunk
    threads = []
    for i in range(chunk_count):
        start = i * chunk_size
        end = start + chunk_size - 1
        if end >= file_size:
            end = file_size - 1
        thread = threading.Thread(target=download_chunk, args=(final_url, start, end, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Merge all the chunks into the final output file
    merge_chunk(chunk_count, output_file)

# Example usage
if __name__ == "__main__":
    url = "http://example.com/largefile.zip"
    output_file = "largefile.zip"
    chunk_size = 1024 * 1024  # 1 MB
    main_function(url, output_file, chunk_size)