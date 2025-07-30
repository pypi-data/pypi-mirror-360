# ENDPOINT
endpoint = "/datasets/products/files/{productIdentifier}/{fileName}"

# RESPONSE IS a binary stream of data with the content of the requested file name

documentation = """
The Download section contains large bulk files of the Bulk Data Directory available for download. Use this endpoint when you want to download bulk data sets.

Note: You are currently limited to 20 downloads of the same file per year for each API Key to avoid overtaxing the service. On the 21st request, you will get an error message with HTTP status response 429.

GET /datasets/products/files/{productIdentifier}/{fileName}

Returns a binary stream of data with the content of the requested file name.

Note: API Key is required. Obtain an API key.
"""
