# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/continuity"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "14104993",
      "parentContinuityBag": [
        {
          "firstInventorToFileIndicator": True,
          "parentApplicationStatusCode": 159,
          "parentPatentNumber": "8968299",
          "parentApplicationStatusDescriptionText": "Patent Expired Due to NonPayment of Maintenance Fees Under 37 CFR 1.362",
          "parentApplicationFilingDate": "2012-05-23",
          "parentApplicationNumberText": "123123133",
          "childApplicationNumberText": "string",
          "claimParentageTypeCode": "CODE",
          "claimParentageTypeCodeDescription": "some description"
        }
      ],
      "childContinuityBag": [
        {
          "childApplicationStatusCode": 150,
          "parentApplicationNumberText": "14104993",
          "childApplicationNumberText": "14853719",
          "childApplicationStatusDescriptionText": "Patented Case",
          "childApplicationFilingDate": "2015-09-14",
          "firstInventorToFileIndicator": False,
          "childPatentNumber": "9704967",
          "claimParentageTypeCode": "DIV",
          "claimParentageTypeCodeDescription": "some desc"
        }
      ]
    }
  ],
  "requestIdentifier": "df5b5478-ad3e-4ad2-b3bc-611838ccb56c"
}

documentation = """
The Continuity section contains continuity details for the patent, including parent and/or child continuity data. Continuity Data includes Parent Continuity Data and Child Continuity Data. Use this endpoint when you want continuity data for a specific patent application whose application number you know. You can test the API right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/continuity

Returns a list of all patents and applications that match your search term.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
parentContinuityBag	All continuity details related to the parent application.	N/A
  firstInventorToFileIndicator	First Inventor on file indicator.	Boolean
  parentApplicationStatusCode	This data element classifies the application by its status relative to the total application process.	Number
  parentPatentNumber	The number that uniquely identifies an issued patent. It is also the document number in the USTPO-published Redbook and the Official Gazette. This number can be for an originally-issued patent or a re-issued patent. It will not be for a Re-exam Certificate, a Correction Certificate, a SIR, or a notice of a request for a Re-exam or a Reissue. This number is equivalent to WIPO ST.9 as INID 11. 5012717.	String
  parentApplicationStatusDescriptionText	Status of the parent application, depending on which bag it falls under; values: new = new application, patented case, patent expired...	String
  parentApplicationFilingDate	Date on which a patent application was filed and received in the USPTO.	Date
  parentApplicationNumberText	Application number of the parent application, which is the unique value assigned by the USPTO to a patent application upon receipt.	String
  claimParentageTypeCode	Claim parentage type code.	String
  claimParentageTypeCodeDescription	Claim parentage type code description.	String
childContinuityBag	All continuity details related to the parent application	N/A
  childApplicationStatusCode	This data element classifies the application by its status relative to the total application process.	Number
  parentApplicationNumberText	Application number of the parent application, which is the unique value assigned by the USPTO to a patent application upon receipt.	String
  childApplicationNumberText	Application number of the child application, which is the unique value assigned by the USPTO to a patent application upon receipt.	String
  childApplicationStatusDescriptionText	Status of the child application, depending on which bag it falls under; values: new = new application, patented case, patent expired...	String
  childApplicationFilingDate	Date on which a patent application was filed and received in the USPTO.	Date
  firstInventorToFileIndicator	First Inventor on file indicator.	Boolean
  childPatentNumber	The number that uniquely identifies an issued patent. It is also the document number in the USTPO-published Redbook and the Official Gazette. This number can be for an originally-issued patent or a re-issued patent. It will not be for a Re-exam Certificate, a Correction Certificate, a SIR, or a notice of a request for a Re-exam or a Reissue. This number is equivalent to WIPO ST.9 as INID 11. 5012717.	String
  claimParentageTypeCode	Claim parentage type code.	String
  claimParentageTypeCodeDescription	Claim parentage type code description.	String
"""