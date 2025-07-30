# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/associated-documents"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "14104993",
      "pgpubDocumentMetaData": {
        "zipFileName": "ipa240801.zip",
        "productIdentifier": "APPXML",
        "fileLocationURI": "https://bulkdata.uspto.gov/data/patent/application/redbook/fulltext/2024/ipa240104.zip",
        "fileCreateDateTime": "2024-08-09:11:30:00",
        "xmlFileName": "ipa240801.xml"
      },
      "grantDocumentMetaData": {
        "zipFileName": "ipg240102.zip",
        "productIdentifier": "PTGRXML",
        "fileLocationURI": "https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2016/ipg160405.zip",
        "fileCreateDateTime": "2024-08-09:11:30:00",
        "xmlFileName": "ipg160405.xml"
      }

    }
  ],
  "requestIdentifier": "0ff4c603-a290-4659-8092-f68b408150c4"
}

documentation = """
The Associated Documents section contains the PGPUB XML extracted from the bulk data product "Patent Application Full-Text Data (No Images)" zip file. It also includes the Patent Grant XML extracted from the bulk data product "Patent Grant Full-Text Data (No Images) - XML" zip file if the corresponding application has PGPUB/Patent Grant data available. You can test the API right away in Swagger UI.

These XML datasets are only available for published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/associated-documents

e.g. /api/v1/patent/applications/16330077/associated-documents

Returns Associated Documents for supplied application number.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
PatentFileWrapperDataBag	Patent File Wrapper data.	N/A
  applicationNumberText	The unique number assigned by the USPTO to a patent application when it is filed.	String
pgpubDocumentMetaData	Details of PgPub document meta data.	N/A
  zipFileName	Zip file name	String
  productIdentifier	Product identifier.	String
  fileLocationURI	File location URI.	String
  fileCreateDateTime	The date file was created.	Date
  xmlFileName	XML file name.	String
grantDocumentMetaData	Grant document meta data.	N/A
  zipFileName	Zip file name	String
  productIdentifier	Product identifier.	String
  fileLocationURI	File location URI.	String
  fileCreateDateTime	The date file was created.	Date
  xmlFileName	XML file name.	String
"""
