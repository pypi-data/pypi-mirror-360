# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/transactions"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "12620694",
      "eventDataBag": [
        {
          "eventCode": "ELC_RVW",
          "eventDescriptionText": "Electronic Review",
          "eventDate": "2018-10-18"
        }
      ]
    }
  ],
  "requestIdentifier": "df5b5478-ad3e-4ad2-b3bc-611838ccb56c"
}

documentation = """
The transactions section contains additional information concerning the transaction activity that has occurred for each patent application. This includes details on the date of the transaction, code (Examiner’s Amendment Communication, Printer Rush, IDS Filed, Application is Now Complete, PTA 36 months), and transaction description. Use this endpoint when you want transaction data related to a specific patent application whose application number you know. You can test the API right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/transactions

Returns all transactions associated for supplied application.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
eventDataBag	Details of the contents of all transactions on an application/patent.	N/A
  eventCode	A short text field that denotes the A16 CT codes.	String
  eventDescriptionText	A text field that denotes the use or function of the activity	String
  eventDate	The date of the legal status change event.	Date
"""
