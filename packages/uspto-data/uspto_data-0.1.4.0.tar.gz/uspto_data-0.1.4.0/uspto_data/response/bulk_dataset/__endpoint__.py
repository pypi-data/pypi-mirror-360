from uspto_data.response.bulk_dataset import search, products

urls = [
    ("datasets/products/search", ["GET"], search.ResponseParser),
    ("datasets/products/{productIdentifier}", ["GET"], products.ResponseParser),
    ("datasets/products/files/{productIdentifier}/{fileName}", ["GET"], lambda x: x)
]

documentation_urls = [
    "/apis/bulk-data/search",
    "/apis/bulk-data/product",
    "/apis/bulk-data/download"
]
