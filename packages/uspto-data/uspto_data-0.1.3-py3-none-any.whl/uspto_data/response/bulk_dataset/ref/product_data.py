# ENDPOINT
endpoint = "/datasets/products/{productIdentifier}"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "bulkDataProductBag": [
    {
      "productIdentifier": "PTFWPRE",
      "productDescriptionText": "Patent File Wrapper Entire Dataset",
      "productTitleText": "Patent File Wrapper Entire Dataset",
      "productFrequencyText": "WEEKLY",
      "daysOfWeekText": "SUNDAY",
      "productLabelArrayText": [
        "PATENT"
      ],
      "productFromDate": "2001-01-01",
      "productToDate": "2024-05-13",
      "productTotalFileSize": 28866492413,
      "productFileTotalQuantity": 3,
      "modifiedDateTime": "2024-05-13 02:29:00",
      "mimeTypeIdentifierArrayText": [
        "JSON"
      ],
      "productFileBag": {
        "count": 3,
        "fileDataBag": [
          {
            "fileName": "2001-2010-patent-filewrapper-full-json.zip",
            "fileSize": 9981249979,
            "fileDataFromDate": "2001-01-01",
            "fileDataToDate": "2010-12-31",
            "fileTypeText": "Data",
            "fileDownloadURI": "https://data.uspto.gov/files/PTFWPRE/2001-2010-patent-filewrapper-full-json.zip",
            "fileReleaseDate": "2024-05-12 21:58:00",
            "fileDate": "2024-12-02 07:18:00",
            "fileLastModified": "2024-12-17 19:49:00"
          },
          {
            "fileName": "2011-2020-patent-filewrapper-full-json.zip",
            "fileSize": 15506284270,
            "fileDataFromDate": "2011-01-01",
            "fileDataToDate": "2020-12-31",
            "fileTypeText": "Data",
            "fileDownloadURI": "https://data.uspto.gov/files/PTFWPRE/2011-2020-patent-filewrapper-full-json.zip",
            "fileReleaseDate": "2024-05-13 01:33:00",
            "fileDate": "2024-12-02 07:18:00",
            "fileLastModified": "2024-12-17 19:49:00"
          },
          {
            "fileName": "2021-2024-patent-filewrapper-full-json.zip",
            "fileSize": 3378958164,
            "fileDataFromDate": "2021-01-01",
            "fileDataToDate": "2024-05-07",
            "fileTypeText": "Data",
            "fileDownloadURI": "https://data.uspto.gov/files/PTFWPRE/2021-2024-patent-filewrapper-full-json.zip",
            "fileReleaseDate": "2024-05-13 02:29:00",
            "fileDate": "2024-12-02 07:18:00",
            "fileLastModified": "2024-12-17 19:49:00"
          }
        ]
      }
    }
  ]
}

documentation = """
The Product Data section contains published, publicly available patent and trademark data in bulk form. Use this endpoint when you want data from a specific Bulk Dataset. You can test APIs right away in SwaggerUI.

All search syntaxes are applicable to this endpoint, meaning any number of combinations are possible. Some example requests are below, but for more information, view the Simplified Syntax documentation that is linked in the API Syntax Examples page. You can also test the API right away in Swagger UI.

You can download the JSON Scheme file to parse the JSON Responses returned by the APIs.

GET /datasets/products/{productIdentifier}

Returns a specific product that matches a productIdentifier

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
count	Total number of records matching the criteria	Number
bulkDataProductBag	List of products returned by the criteria	N/A
  productIdentifier	The unique number assigned by the USPTO to a product	String
  productDescriptionText	Product description text	String
  productTitleText	Product title text	String
  productFrequencyText	Frequency of updates to the product data files.	String
  productFromDate	Date from which product data is valid	Date
  productToDate	End Date of a valid product	String
  productTotalFileSize	Size in bytes, of all files for a combined product	Number
  productFileTotalQuantity	Number of product files a product contains	Number
  modifiedDateTime	Date when a product was last updated	Date
  mimeTypeIdentifierArrayText	Product files mime types e.g json, xml, pdf etc	List
productFileBag	Bag representing data of product files	List
  count	Total number product files of records	Number
fileDataBag	File data bag	N/A
  fileName	File name	String
  fileSize	File size in bytes	String
  fileDataFromDate	Date from data recorded in file	String
  fileDataToDate	Date till data recorded in file	String
  fileDownloadURI	Downloadable file URI	String
  fileReleaseDate	Date when file was last released	String
  fileDate	The period frequency date when the data file was generated	String
  fileLastModified	Date when file was last modified	String
"""
