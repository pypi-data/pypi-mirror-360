# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/adjustment"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "12620694",
      "patentTermAdjustmentData": {
        "aDelayQuantity": 0,
        "adjustmentTotalQuantity": 0,
        "applicantDayDelayQuantity": 28,
        "bDelayQuantity": 0,
        "cDelayQuantity": 0,
        "filingDate": "2013-12-12",
        "grantDate": "2016-06-07",
        "nonOverlappingDayQuantity": 0,
        "overlappingDayQuantity": 0,
        "ipOfficeDayDelayQuantity": 0,
        "patentTermAdjustmentHistoryDataBag": [
          {
            "eventDate": "2016-06-07",
            "applicantDayDelayQuantity": 4,
            "eventDescriptionText": "Patent Issue Date Used in PTA Calculation",
            "eventSequenceNumber": 65,
            "ipOfficeDayDelayQuantity": 0,
            "originatingEventSequenceNumber": 0,
            "ptaPteCode": "PTA"
          }
        ]
      }
    }
  ],
  "requestIdentifier": "df5b5478-ad3e-4ad2-b3bc-611838ccb56c"
}

documentation = """
The Patent Term Adjustment section provides additional information concerning the patent term adjustment that has occurred for each patent. Use this endpoint when you want patent term adjustment data related to a specific patent application whose application number you know. You can test APIs right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/adjustment

Returns adjustment data for supplied application number.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
patentTermAdjustmentData	Patent term adjustment data.	N/A
  applicantDayDelayQuantity	This entry reflects adjustments of the patent term due to the Applicant's failure to engage in reasonable efforts to conclude prosecution of the application for the cumulative period in excess of three months. See 35 U.S.C. § 154(b)(2)(C)(ii) and implementing regulation 37 CFR 1.704(b). The entry also reflects additional Applicant's failure to engage in reasonable efforts to conclude prosecution of the application. See 35 U.S.C. § 154(b)(2)(C)(iii) and implementing regulations 37 CFR 1.704(c)(1)-(11).	Number
  overlappingDayQuantity	Patent term adjustment overlapping days quantity number that reflects the calculation of overlapping delays consistent with the federal circuit's interpretation.	Number
  filingDate	The date assigned by the USPTO that identifies when a patent application meets certain criteria to qualify as having been "filed."	Date
  grantDate	The data the patent is granted	Date
  cDelayQuantity	This entry reflects adjustments to the term of the patent based upon USPTO delays pursuant to 35 U.S.C. § 154(C)(i)-(iii) and implementing regulations 37 CFR 1.702 (c)-(e) & 1.703(c)-(e). These delays include delays caused by interference proceedings, secrecy orders, and successful appellate reviews.	Number
  adjustmentTotalQuantity	This entry reflects the summation of the following entries: NONOVERLAPPING USPTO DELAYS (+/or – USPTO MANUAL ADJUSTMENTS) – APPLICANT DELAYS. It is noted that the TOTAL PTA CALCULATION determined at the time of the notice of allowance will not reflect PALM entries that are entered after the entry or mailing of the notice of allowance.	Number
  ptoDelayDays	This entry reflects the UPSTO personnel adjusting the calculation to increase or decrease the patent term adjustment based upon either an application for patent term adjustment pursuant to 37 CFR 1.705(b) or a request for reconsideration of the patent term adjustment under 37 CFR 1.705(d). In addition, the USPTO may reduce the PTA determination in response to a letter of good faith and candor regarding PTA advising the USPTO that the USPTO may have granted more PTA than applicant/patentee is entitled.	Number
  bDelayQuantity	This entry reflects adjustments to the term of the patent based upon the patent failing to issue within three years of the actual filing date of the application in the United States. See 35 U.S.C. § 154(b) and implementing regulations 37 CFR 1.702(b) & 1.703(b). "B" delay is always calculated at the time that the issue notification letter is generated and an issue date has been established.	Number
  nonOverlappingDayQuantity	This entry reflects the overall summation of the USPTO delays minus any overlapping days. Particularly, it includes the following: ("A" delays + "B" delays + "C" delays) - (the number of calendar days overlapping between "A" delays and "B" delays + the number of calendar days overlapping between "A" delays and "C" delays). This entry does not reflect the number of days of applicant delays pursuant to 35 U.S.C. § 154(b)(2)(C) and 37 CFR 1.704(b) and 37 CFR 1.704(c)(1)-(11).	Number
  ipOfficeDayDelayQuantity	IP office delay summation	Number
  aDelayQuantity	This entry reflects adjustments to the term of the patent based upon USPTO delays pursuant to 35 U.S.C. § 154(b)(1)(A)(i)-(iv) and the implementing regulations 37 CFR 1.702(a) & 37 CFR 1.703(a). An "A" delay may occur prior to the notice of allowance and be included in the PTA determination accompanying the notice of allowance or may occur after the entry or mailing of the notice of allowance and be included in the PTA determination in the issue notification letter.	Number
patentTermAdjustmentHistoryDataBag	The recordation of patent case actions that are involved in the patent term adjustment calculation.	N/A
  originatingEventSequenceNumber	The sequence of the patent case action that started the time period for the Patent Case Action/Extension.	Number
  eventSequenceNumber	The sequence in which the actions for a patent case are to be displayed.	Number
  eventDescriptionText	A text field that denotes the use or function of the activity.	String
  eventDate	The date of the legal status change event.	Date
  ipOfficeDayDelayQuantity	IP office delay summation	Number
  applicantDays	Date on which the patent application was granted/issued.	Date
  ptaPteCode	PTA or PTE code	PTA
"""
