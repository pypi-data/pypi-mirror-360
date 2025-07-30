# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/foreign-priority"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "12620694",
      "foreignPriorityBag": [
        {
          "ipOfficeName": "FRANCE",
          "filingDate": "2012-12-19",
          "applicationNumberText": "08 020 164.3"
        }
      ]
    }
  ],
  "requestIdentifier": "df5b5478-ad3e-4ad2-b3bc-611838ccb56c"
}

documentation = """
The Foreign Priority section provides additional information concerning the foreign priority related to each patent. Use this endpoint when you want foreign priority information related to a specific patent application whose application number you know. You can test APIs right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/foreign-priority

Returns foreign priority data for supplied application number.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
foreignPriorityBag	Contains information about relevant foreign priority.	N/A
  applicationNumberText	Free format of application number.	String
  filingDate	The date on which a priority claim was filed.	Date
  ipOfficeName	Names of states, other entities and intergovernmental organizations the legislation of which provides for the protection of IP rights or which organizations are acting in the framework of a treaty in the field of IP	String
"""
