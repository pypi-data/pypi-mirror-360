# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/document"
# JSON RESPONSE SAMPLE
example_json = {
  "documentBag": [
    {
      "applicationNumberText": "16123123",
      "officialDate": "2020-08-31T01:20:29.000-0400",
      "documentIdentifier": "LDXBTPQ7XBLUEX3",
      "documentCode": "WFEE",
      "documentCodeDescriptionText": "Fee Worksheet (SB06)",
      "documentDirectionCategory": "INTERNAL",
      "downloadOptionBag": [
        {
          "mimeTypeIdentifier": "PDF",
          "downloadURI": "https://beta-api.uspto.gov/api/v1/patent/application/documents/16123123/LDXBTPQ7XBLUEX3.pdf",
          "pageTotalQuantity": 2
        }
      ]
    }
  ]
}

documentation = """
The Documents section contains details on documents attached to the patent application, as well as options for downloading the documents. This includes documents under all codes (Examiner’s Amendment Communication, Printer Rush, IDS Filed, Application is Now Complete, PTA 36 months). Use this endpoint when you want documents related to a specific patent application whose application number you know. You can test the API right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/documents

Returns document meta-data along with document download URI for supplied application number.
"""

response_info = """
Property	Description	Type
documentBag	Details of the documents related to an application.	N/A
  applicationNumberText	The unique number assigned by the USPTO to a patent application upon receipt when it is filed.	String
  officialDate	The date correspondence is received at the USPTO, either through the mail room or via the Internet.	Date
  documentIdentifier	A unique identifier for a document stored in the repository.	String
  documentCode	The unique reference value (number and letters) for an application/patent document.	String
  documentCodeDescriptionText	Document code's description.	String
  documentDirectionCategory	Category for the document type (Incoming, Outgoing.	String
downloadOptionBag	Details about download options for the documents.	N/A
  mimeTypeIdentifier	Document type identifier (e.g., PDF/XML/Dox)	String
  downloadUrl	Link to download	String
  pageTotalQuantity	Total number of pages in the document.	Number
"""