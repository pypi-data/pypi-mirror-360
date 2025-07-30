# ENDPOINT
endpoint = "/datasets/products/search"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 3,
  "bulkDataProductBag": [
    {
      "productIdentifier": "PTFWPRE",
      "productDescriptionText": "Patent File Wrapper Entire Dataset",
      "productTitleText": "Patent File Wrapper Entire Dataset",
      "productFrequencyText": "WEEKLY",
      "daysOfWeekText": "SUNDAY",
      "productLabelArrayText": [
        "PATENT",
        "RESEARCH"
      ],
      "productDataSetArrayText": [
        "Research"
      ],
      "productDataSetCategoryArrayText": [
        "Patent applications"
      ],
      "productFromDate": "2021-01-01",
      "productToDate": "2030-12-31",
      "productTotalFileSize": 10430070,
      "productFileTotalQuantity": 1,
      "modifiedDateTime": "2024-04-16 18:39:00",
      "mimeTypeIdentifierArrayText": [
        "json"
      ],
      "productFileBag": {
        "fileDataBag": [
          {
            "fileName": "2021-2023-pairbulk-full-20240114-json.zip",
            "fileSize": 10430070,
            "fileDataFromDate": "2021-01-01",
            "fileDataToDate": "2030-12-31",
            "fileTypeText": "Data",
            "fileDownloadURI": "https://data.uspto.gov/files/PTFWPRE/pairbulk-delta-20240129-json.zip",
            "fileReleaseDate": "2021-01-01",
            "fileDate": "2024-11-24",
            "fileLastModified": "2024-12-17 19:49:00"
          }
        ]
      }
    },
    {
      "productIdentifier": "PTFWPRD",
      "productDescriptionText": "Patent File Wrapper Delta Dataset",
      "productTitleText": "Patent File Wrapper Delta Dataset",
      "productFrequencyText": "DAILY",
      "productFromDate": "2023-04-15",
      "productToDate": "2024-04-17",
      "productTotalFileSize": 32156499361,
      "productFileTotalQuantity": 3,
      "modifiedDateTime": "2024-04-16 19:42:00",
      "mimeTypeIdentifierArrayText": [],
      "productFileBag": {
        "fileDataBag": [
          {
            "fileName": "e-OG20230910_1514-3.zip",
            "fileSize": 10430090,
            "fileDataFromDate": "2023-04-15",
            "fileDataToDate": "2023-04-16",
            "fileTypeText": "Data",
            "fileDownloadURI": "https://data.uspto.gov/files/PTFWPRD/e-OG20230910_1514-3.zip",
            "fileReleaseDate": "2023-04-15",
            "fileLastModified": "2024-12-17 19:49:00"
          },
          {
            "fileName": "e-OG20230910_1514-3.zip",
            "fileSize": 10430010,
            "fileDataFromDate": "2023-04-15",
            "fileDataToDate": "2023-04-16",
            "fileTypeText": "Data",
            "fileDownloadURI": "https://data.uspto.gov/files/PTFWPRD/e-OG20240417_1514-3.zip",
            "fileReleaseDate": "2023-04-15",
            "fileLastModified": "2024-12-17 19:49:00"
          },
          {
            "fileName": "pairbulk-delta-20240417.json.gz",
            "fileSize": 2060438119,
            "fileDataFromDate": "2024-04-17",
            "fileDataToDate": "2024-04-17",
            "fileTypeText": "Data",
            "fileDownloadURI": "https://data.uspto.govs3://odp-dev-dh-web/bulk-data/files/PTFWPRD/pairbulk-delta-20240417.json.gz",
            "fileReleaseDate": "2024-04-17",
            "fileLastModified": "2024-12-17 19:49:00"
          }
        ]
      }
    },
    {
      "productIdentifier": "PTNT",
      "productDescriptionText": "Patent File Another Entire Dataset",
      "productTitleText": "Patent File Another Entire Dataset",
      "productFrequencyText": "DAILY",
      "productLabelArrayText": [],
      "productTotalFileSize": 32156499361,
      "productFileTotalQuantity": 3,
      "modifiedDateTime": "2024-04-17 13:55:00",
      "mimeTypeIdentifierArrayText": [
        "xml"
      ]
    }
  ],
  "facets":
    {
      "productLabelBag": [
        {
          "value": "PATENT",
          "count": 1
        },
        {
          "value": "RESEARCH",
          "count": 1
        }
      ],
      "productDataSetBag": [
        {
          "value": "Research",
          "count": 1
        }
      ],
      "productCategoryBag": [
        {
          "value": "Patent applications",
          "count": 1
        }
      ],
    "productMimeTypeBag": [
      {
        "value": "PDF",
        "count": 1
      },
      {
        "value": "XML",
        "count": 4
      }
    ]
    }
}

documentation = """
Conduct a search of the repository of raw public bulk data. It contains research data from the Office of the Chief Economist. The files are updated on a regular or ongoing basis.

Use this endpoint if you are interested in searching across multiple patents or applications. For example, you want to return all Patent or Trademark products use productTitle and specify the products you are looking for Patent File Wrapper, for example.

Note: The other endpoint (Product Data) should be used when you're looking for a specific bulk dataset to find targeted information within the dataset. For example, you want to return all the relevant release dates for the Patent assignment XML bulk dataset.

Other details for using the Search endpoint:

If you don’t specify which attributes you would like to see in the response related to the search term(s), it returns all data attributes.

All search syntaxes are applicable to this endpoint, meaning any number of combinations is possible. Some example requests are below, but for more information, view the Simplified Syntax documentation that is linked in the API Syntax Examples page. You can also test the API right away in Swagger UI.

You can download the JSON Schema file to parse the JSON responses returned by the APIs.

GET /datasets/products/search

Returns a list of all products that match your search term.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
count	Total number of records matching the criteria	Number
bulkDataProductBag	List of products returned by the criteria	N/A
  productIdentifier	The unique number assigned by the USPTO to a product	String
  productDescriptionText	Product description text	String
  productTitleText	Product title text	String
  productFrequencyText	Frequency of product data files updates	String
  productFromDate	Begin Date of a valid product	Date
  productToDate	End Date of a valid product	String
  productTotalFileSize	Size in bytes, of all files for a product combined	Number
  productFileTotalQuantity	Number of product files a product contains	Number
  modifiedDateTime	Date when a product was last updated	Date
  mimeTypeIdentifierArrayText	Product files mime types e.g json, xml, pdf etc	List
productFileBag	Bag representing data of product files	List
fileDataBag	File data bag	N/A
  fileName	File name	String
  fileSize	File size in bytes	String
  fileDataFromDate	Date from data recorded in file	String
  fileDataToDate	Date till data recorded in file	String
  fileDownloadURI	Downloadable file URI	String
  fileReleaseDate	Date when file was last released	String
  fileDate	The period frequency date when the data file was generated	String
  fileLastModified	Date when file was last modified	String
facets	Object representing facet data	N/A
productLabelBag	Bag representing faceted data for product label	N/A
productDataSetBag	Bag representing faceted data for product data set	N/A
productCategoryBag	Bag representing Facet representing categories	N/A
productMimeTypeBag	Bag representing Facet representing MimeType for files	N/A
  count	Number representing facet count	Number
  value	Potential facet options within bags	String
"""