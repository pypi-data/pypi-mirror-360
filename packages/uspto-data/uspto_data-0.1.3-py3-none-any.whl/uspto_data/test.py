import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse


def download_uspto_docs(base_url="https://www.uspto.gov/guidance", save_dir="uspto_guidance_docs", visited=None):
    """
    Recursively finds and downloads all guidance documents (PDFs) from the USPTO guidance page.

    Args:
        base_url (str): The URL to start scraping from.
        save_dir (str): Directory where documents will be stored.
        visited (set): Set to track visited URLs to avoid infinite loops.

    Returns:
        list: A list of downloaded document file paths.
    """
    if visited is None:
        visited = set()

    # Skip if already visited
    if base_url in visited:
        return []
    visited.add(base_url)

    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)

    # Pause before making a request (to be polite)
    time.sleep(0.4)

    # Fetch the page content
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to retrieve {base_url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    downloaded_files = []
    links_to_visit = []  # Store HTML pages to visit *after* handling PDFs

    # Step 1: First process all PDFs
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)

        # Skip external links (not on USPTO)
        if "uspto.gov" not in parsed_url.netloc:
            continue

        # If it's a PDF, check if it exists before downloading
        if full_url.endswith('.pdf'):
            doc_name = os.path.basename(parsed_url.path)
            doc_path = os.path.join(save_dir, doc_name)

            if os.path.exists(doc_path):
                print(f"Already exists: {doc_name}, skipping download.")
                continue

            print(f"Downloading: {doc_name}")
            with requests.get(full_url, stream=True) as doc_response:
                if doc_response.status_code == 200:
                    with open(doc_path, 'wb') as doc_file:
                        for chunk in doc_response.iter_content(chunk_size=8192):
                            doc_file.write(chunk)
                    downloaded_files.append(doc_path)
                else:
                    print(f"Failed to download: {full_url}")

    # Step 2: Now process non-PDF pages for recursive exploration
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)

        if full_url not in visited and full_url.endswith(('.html', '/')):
            links_to_visit.append(full_url)  # Store links for later

    # Now visit stored HTML links (after handling PDFs)
    for html_url in links_to_visit:
        print(f"Visiting: {html_url}")
        downloaded_files.extend(download_uspto_docs(html_url, save_dir, visited))

    return downloaded_files


# Example usage
if __name__ == "__main__":
    downloaded_docs = download_uspto_docs()
    print(f"\nTotal documents downloaded: {len(downloaded_docs)}")
