# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/assignment"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "assignmentBag": {
        "reelNumber": "60620",
        "frameNumber": "769",
        "reelNumber/frameNumber": "60620/769",
        "pageNumber": 16,
        "assignmentReceivedDate": "2022-07-11",
        "assignmentRecordedDate": "2022-07-11",
        "assignmentMailedDate": "2022-07-28",
        "conveyanceText": "ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).",
        "assignorBag": [
          {
            "assignorName": "STMICROELECTRONICS SA",
            "executionDate": "2022-06-30"
          }
        ],
        "assigneeBag": [
          {
            "assigneeNameText": "STMICROELECTRONICS SA",
            "assigneeAddress": {
              "addressLineOneText": "CHEMIN DU CHAMP-DES-FILLES 39",
              "addressLineTwoText": "1228 PLAN-LES-OUATES",
              "cityName": "GENEVA",
              "geographicRegionName": "CHX",
              "geographicRegionCode": "string",
              "countryName": "Switzerland",
              "postalCode": "20123"
            }
          }
        ],
        "correspondenceAddressBag": {
          "correspondentNameText": "STMICROELECTRONICS, INC.",
          "addressLineOneText": "750 CANYON DRIVE",
          "addressLineTwoText": "SUITE 300",
          "addressLineThreeText": "COPPELL, TX 75019",
          "addressLineFourText": "Address Line Four"
        }
      }
    }
  ],
  "requestIdentifier": "bb38eb61-f05b-42f7-a4bd-2beac9fb15de"
}

documentation = """
The Assignments section provides additional information concerning the assignments of each patent. Use this endpoint when you want assignments data related to a specific patent application whose application number you know. You can test the API right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/assignment

Returns assignment data for supplied application number.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
assignmentBag	The collection of national assignments related to a patent or trademark.	N/A
  reelNumber	1-6 digit number identifies the reel number to be used to locate the assignment on microfilm.	String
  frameNumber	1-4 digit number that identifies the frame number to be used to locate the first image (page) of the assignment on microfilm.	String
  reelNumber/frameNumber	1-6 digit number identifies the reel number to be used to locate the assignment on microfilm. / 1-4 digit number that identifies the frame number to be used to locate the first image (page) of the assignment on microfilm.	String
  pageNumber	Identifies the total page count of the assignment (i.e., the number of pages captured on microfilm).	Number
  assignmentReceivedDate	The date an assignment was received. Contains a date element with an 8-digit date in YYYY-MM-DD date format.	Date
  assignmentRecordedDate	Identifies when the assignment was recorded in the USPTO. Contains a date element with an 8-digit date in YYYY-MM-DD date format.	Date
  assignmentMailedDate	The date an assignment request was mailed to the office or received by the office. Contains a date element with an 8-digit date in YYYY-MM-DD date format.	Date
  conveyanceText	Contains textual description of the interest conveyed or transaction recorded.	String
assignorBag	Collection of assignors/details related to the assignor(s).	N/A
  assignorName	A party that transfers its interest and right to the patent to the transferee (assignee) or the party receiving the patent.	String
  executionDate	Identifies the date from the supporting legal documentation that the assignment was executed. Contains a date element with an 8-digit date in YYYY-MM-DD date format.	Date
assigneeBag	Collection of assignees/details related to the assignee(s).	N/A
  assigneeNameText	A person or entity that has the property rights to the patent, as a result of being the recipient of a transfer of a patent application or patent grant. Refers to ST.9 INID Code 73.	String
  assigneeAddress	Address details on file for the assignee.	N/A
  addressLineOneText	First line of address associated with the assignee.	String
  addressLineTwoText	Second line of address associated with the assignee.	String
  cityName	Name of the city	String
  geographicRegionName	Geographic region name	String
  geographicRegionCode	Geographic region code	String
  countryName	Country name.	String
  postalCode	Postal code	String
correspondenceAddressBag	The address of the patent correspondence	N/A
  correspondentNameText	The correspondent name	String
  addressLineOneText	First line of address associated with the correspondent.	String
  addressLineTwoText	Second line of address associated with the correspondent.	String
  addressLineThreeText	Third line of address associated with the correspondent.	String
  addressLineFourText	Fourth line of address associated with the correspondent, if applicable.	String
"""