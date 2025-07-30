# ENDPOINT
endpoint = "/api/v1/patent/applications/search"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "14104993",
      "nationalStageIndicator": True,
      "smallEntityStatusIndicator": True,
      "publicationDateBag": [
        {
          "publicationDate": "2014-06-19T00:00:00.000Z",
          "publicationCategory": [
            "Granted/Issued",
            "Pre-Grant Publications - PGPub"
          ]
        }
      ],
      "docketNumber": "12GR10425US01/859063.688",
      "firstInventorToFileIndicator": "Y",
      "firstApplicantName": "STMicroelectronics S.A.",
      "firstInventorName": "Pascal Chevalier",
      "applicationConfirmationNumber": "1061",
      "applicationStatusDate": "2016-05-18T00:00:00.000Z",
      "applicationStatusDescriptionText": "Patented Case",
      "filingDate": "2012-12-19T00:00:00.000Z",
      "effectiveFilingDate": "2013-12-12T00:00:00.000Z",
      "grantDate": "2016-06-07T00:00:00.000Z",
      "groupArtUnitNumber": 2895,
      "applicationTypeCode": "UTL",
      "applicationTypeLabelName": "Utility",
      "applicationTypeCategory": "electronics",
      "inventionTitle": "HETEROJUNCTION BIPOLAR TRANSISTOR",
      "patentNumber": "9362380",
      "applicationStatusCode": 150,
      "businessEntityStatusCategory": "Undiscounted",
      "earliestPublicationNumber": "US 2014-0167116 A1",
      "earliestPublicationDate": "2014-06-19T00:00:00.000Z",
      "publicationSequenceNumberBag": [
        "61006"
      ],
      "wipoReferenceNumber": "WO 2009/064413",
      "pctPublicationDate": "2016-12-16T00:00:00.000Z",
      "internationalRegistrationPublicationDate": "2016-12-16T00:00:00.000Z",
      "internationalRegistrationNumber": "DM/091304",
      "examinerNameText": "HUI TSAI JEY",
      "class": "257",
      "subclass": "197000",
      "class/subclass": "257/197000",
      "correspondenceAddressBag": [
        {
          "nameLineOneText": "Seed IP Law Group LLP/ST (EP ORIGINATING)",
          "nameLineTwoText": "Attn- IP Docket",
          "addressLineOneText": "701 FIFTH AVENUE, SUITE 5400",
          "addressLineTwoText": "Suite 501",
          "geographicRegionName": "WASHINGTON",
          "geographicRegionCode": "WA",
          "postalCode": "98104-7092",
          "cityName": "SEATTLE",
          "countryCode": "US",
          "countryName": "USA",
          "postalAddressCategory": "commercial"
        }
      ],
      "customerNumber": 38106,
      "cpcClassificationBag": [
        "H01L29/66325",
        "H01L27/0623",
        "H01L29/7378",
        "H01L21/8249",
        "H01L29/737",
        "H01L29/66242"
      ],
      "applicantBag": [
        {
          "firstName": "John",
          "middleName": "P",
          "lastName": "Smith",
          "preferredName": "John Smith",
          "namePrefix": "Mr.",
          "nameSuffix": "Jr.",
          "countryCode": "US",
          "correspondenceAddressBag": [
            {
              "nameLineOneText": "STMicroelectronics S.A.",
              "nameLineTwoText": "Name Line Two",
              "addressLineOneText": "Address Line 1",
              "addressLineTwoText": "Address Line 2",
              "geographicRegionName": "MN",
              "geographicRegionCode": "Region Code",
              "postalCode": "10012",
              "cityName": "Montrouge",
              "countryCode": "FR",
              "countryName": "FRANCE",
              "postalAddressCategory": "commercial"
            }
          ],
          "applicant": "John Smith"
        }
      ],
      "inventorBag": [
        {
          "firstName": "John",
          "middleName": "K",
          "lastName": "Smith",
          "namePrefix": "Mr.",
          "nameSuffix": "Sr.",
          "preferredName": "John Smith",
          "countryCode": "US",
          "inventorNameText": "Pascal Chevalier",
          "correspondenceAddressBag": [
            {
              "nameLineOneText": "Pascal  Chevalier",
              "nameLineTwoText": "Name Two",
              "addressLineOneText": "197 Chemin de la Meuniere",
              "addressLineTwoText": "Line Two",
              "geographicRegionName": "Region Name",
              "geographicRegionCode": "FR",
              "postalCode": "20125",
              "cityName": "Chapareillan",
              "countryCode": "FR",
              "countryName": "FRANCE",
              "postalAddressCategory": "commercial"
            }
          ]
        }
      ],
      "assignmentBag": [
        {
          "reelNumber": "60620",
          "frameNumber": "769",
          "reelNumber/frameNumber": "60620/769",
          "pageNumber": 16,
          "assignmentReceivedDate": "2022-07-11T00:00:00.000Z",
          "assignmentRecordedDate": "2022-07-11T00:00:00.000Z",
          "assignmentMailedDate": "2022-07-28T00:00:00.000Z",
          "conveyanceText": "ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).",
          "assignorBag": [
            {
              "assignorName": "STMICROELECTRONICS SA",
              "executionDate": "2022-06-30T00:00:00.000Z"
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
      ],
      "recordAttorney": {
        "customerNumber": [
          {
            "patronIdentifier": "string",
            "organizationStandardName": "string",
            "powerOfAttorneyAddressBag": [
              {
                "nameLineOneText": "Seed IP Law Group LLP/ST (EP ORIGINATING)",
                "addressLineOneText": "701 FIFTH AVENUE, SUITE 5400",
                "addressLineTwoText": "Sample Line Two",
                "geographicRegionName": "ST",
                "geographicRegionCode": "string",
                "postalCode": "98104-7092",
                "cityName": "SEATTLE",
                "countryCode": "US",
                "countryName": "UNITED STATES"
              }
            ],
            "telecommunicationAddressBag": [
              {
                "telecommunicationNumber": "string",
                "extensionNumber": "string",
                "usageTypeCategory": "string"
              }
            ]
          }
        ],
        "attorneyBag": [
          {
            "firstName": "DANIEL",
            "lastName": "O'BRIEN",
            "registrationNumber": "65545",
            "activeIndicator": "ACTIVE",
            "telecommunicationAddressBag": [
              {
                "telecommunicationNumber": "206-622-4900",
                "extensionNumber": "243",
                "usageTypeCategory": "TEL"
              }
            ]
          }
        ]
      },
      "foreignPriorityBag": [
        {
          "countryName": "FRANCE",
          "filingDate": "2012-12-19T00:00:00.000Z",
          "priorityNumberText": "1262321"
        }
      ],
      "continuityBag": [
        {
          "prentContinuityBag": [
            {
              "aiaIndicator": True,
              "applicationStatusCode": 159,
              "patentNumber": "8968299",
              "applicationStatusDescriptionText": "Patent Expired Due to NonPayment of Maintenance Fees Under 37 CFR 1.362",
              "filingDate": "2012-05-23T00:00:00.000Z",
              "parentApplicationNumberText": "123123133",
              "childApplicationNumberText": "string",
              "claimParentageTypeCode": "CODE",
              "claimParentageTypeCodeDescription": "some description"
            }
          ],
          "childContinuityBag": [
            {
              "applicationStatusCode": 150,
              "parentApplicationNumberText": "14104993",
              "childApplicationNumberText": "14853719",
              "applicationStatusDescriptionText": "Patented Case",
              "filingDate": "2015-09-14T00:00:00.000Z",
              "aiaIndicator": False,
              "patentNumber": "9704967",
              "claimParentageTypeCode": "DIV",
              "claimParentageTypeCodeDescription": "some desc"
            }
          ]
        }
      ],
      "patentTermAdjustmentData": {
        "aDelayQuantity": 0,
        "adjustmentTotalQuantity": 0,
        "applicantDayDelayQuantity": 28,
        "bDelayQuantity": 0,
        "cDelayQuantity": 0,
        "filingDate": "2013-12-12T00:00:00.000Z",
        "grantDate": "2016-06-07T00:00:00.000Z",
        "nonOverlappingDayQuantity": 0,
        "overlappingDayQuantity": 0,
        "ipOfficeDayDelayQuantity": 0,
        "patentTermAdjustmentHistoryDataBag": [
          {
            "actionDate": "2016-06-07T00:00:00.000Z",
            "applicantDays": 4,
            "caseActionDescriptionText": "Patent Issue Date Used in PTA Calculation",
            "caseActionSequenceNumber": 65,
            "ipOfficeDayDelayQuantity": 0,
            "startSequenceNumber": 0
          }
        ]
      },
      "eventDataBag": [
        {
          "eventCode": "ELC_RVW",
          "eventDescriptionText": "Electronic Review",
          "eventDate": "2018-10-18T00:00:00.000Z"
        }
      ],
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
      },
      "lastIngestionTime": "2024-09-15T21:19:01"
    }
  ],
  "facets": [
    {
      "applicationStatusCode": [
        {
          "value": "Utility",
          "count": 44673
        }
      ]
    }
  ],
  "requestIdentifier": "df5b5478-ad3e-4ad2-b3bc-611838ccb56c"
}

documentation = """
Conduct a search of all patent application bibliographic/front page and patent relevant data fields. This data is refreshed daily.

Use this endpoint if you are interested in searching across multiple patents or applications. For example, you want to return all patents and applications that match your search term, such as Utility or Design. You can also use multiple search terms, such as “Patented AND Abandoned.” You can use any combination of the 100+ data attributes available and documented below.

Note: The other endpoints (such as Application Data, Continuity, etc.) should be used when you're using a specific application number to find more detailed information. For example, you want to return all the relevant application data about Application #14412875 or all continuity data for Application #10588979.

Other details for using the Search endpoint:

If you don’t specify the field in which you want us to look for this search term, we will look for it across all application data (inventionTitle, patentNumber, applicationTypeLabelName, correspondenceAddressBag etc.) and return any matching patents or applications.

If you don’t specify which attributes you would like to see in the response related to the search term(s), it returns all data attributes.

All search syntaxes are applicable to this endpoint, meaning any number of combinations is possible. Some example requests are below, but for more information, view the Simplified Syntax documentation that is linked in the Open Data Portal API page. You can also test the API right away in Swagger UI.

You can download the JSON Schema file to parse the JSON responses returned by the APIs.

GET /patent/applications/search

Returns a list of all patents and applications that match your search term.

Note: API Key is required. Obtain an API key.

POST See Swagger documentation

Returns a list of all patents and applications that match your search term.

Note: API Key is required. Obtain an API key.

"""

response_info = """
Successful request.

Data Property	Description	Type
PatentFileWrapperDataBag	Patent File Wrapper data.	N/A
  applicationNumberText	The unique number assigned by the USPTO to a patent application when it is filed.	String
  nationalStageIndicator	National Stage indicator.	Boolean
  smallEntityStatusIndicator	Small entity status indicator.	Boolean
publicationDateBag	Contains the date(s) of publication.	N/A
  publicationDate	The date of publication.	Date
  publicationCategory	Publication category.	String
  docketNumber	An identifier assigned by a non-USPTO interest to an application patent case. The identifier is assigned by the person filing the application (applicant or the legal representative of the applicant) to identify the application internally on customer side. It's optional for the customer.	String
  firstInventorToFileIndicator	The first inventor to file (First Inventor to File- FITF) provision of the America Invents Act (AIA) transitions the U.S. to a first-inventor-to-file system from a first-to-invent system.	String
  firstApplicantName	Name of the Applicant with Rank One. Listed as first applicant in the patent application.	String
  firstInventorName	Name of the inventor with Rank One. Listed as first inventor in the patent application.	String
  applicationConfirmationNumber	A four-digit number that is assigned to each newly filed patent application. The confirmation number, in combination with the application number, is used to verify the accuracy of the application number placed on correspondence /filed with the office to avoid mis identification of an application due to a transposition error (misplaced digits) in the application number. The office recommends that applicants include the application's confirmation number (in addition to the application number) on all correspondence submitted to the office concerning the application.	Number
  applicationStatusDate	Application status date.	Date
  applicationStatusDescriptionText	Status of the application; values: new = new application	String
  filingDate	Date on which a patent application was filed and received in the USPTO.	Date
  effectiveFilingDate	The date according to USPTO criteria that the patent case qualified as having been 'filed'. The effective filing date is the same or later than the Filing Date. The filing date can be changed due to a subsequent action on an application	Date
  grantDate	The date a patent was granted.	Date
  groupArtUnitNumber	A working unit responsible for a cluster of related patent art. Generally, staffed by one supervisory patent examiner (SPE) and a number of patent examiners who determine patentability on applications for a patent. Group Art Units are currently identified by a four digit number, i.e., 1642.	String
  applicationTypeCode	The specific value that indicates if the received patent application is considered a domestic application at the National Stage or is submitted as a Patent Cooperative Treaty (PCT) application.	Number
  applicationTypeLabelName	The label for the application type.	String
  applicationTypeCategory	The category of the application	String
  inventionTitle	Title of invention/application: The clear and concise technical description of the invention as provided by the patent applicant.	String
  patentNumber	The unique number assigned by the USPTO to a granted/issued patent. It is also the document number in the USTPO-published Redbook and the Official Gazette. This number can be for an originally-issued patent or a re-issued patent. It will not be for a Re-exam Certificate, a Correction Certificate, a SIR, or a notice of a request for a Re-exam or a Reissue. This number is equivalent to WIPO ST.9 as INID 11. 5012717.	String
  applicationStatusCode	This data element classifies the application by its status relative to the total application process.	String
  businessEntityStatusCategory	Status of business The large-or-small-entity payment status of the APPLICATION PATENT CASE at the time of the small entity status event and thereafter until the occurrence of a later small entity status event for the APPLICATION PATENT CASE. entity being established for the purpose of paying a fee such as a filing fee and a maintenance fee	String
  earliestPublicationNumber	Earliest publication number.	String
  earliestPublicationDate	Earliest publication date.	Date
publicationSequenceNumberBag	Contains a number assigned to the publication of patent applications filed on or after November 29, 2000. It includes the year, followed by a seven digit number, followed by a kind code. Example: 200011234567A1.	String
  wipoReferenceNumber	The unique identifier assigned to the publication of an international patent application in the PCT Gazette by the International Bureau (IB) of the World Intellectual Property Organization (WIPO).	String
  wipoPublicationDate	The date that the international patent application was published in the PCT Gazette by the International Bureau (IB) of the World Intellectual Property Organization (WIPO).	Date
  internationalRegistrationPublicationDate	The date of publication by the International Bureau of an international registration of an industrial design.	Date
  internationalRegistrationNumber	The number assigned by the International Bureau to an international registration upon registering the industrial design in the International Register	String
  examinerNameText	Name of patent examiner, who is fully authorized to sign office actions making patentability determinations (i.e., has “signatory authority”.)	String
  class	The second hierarchical level in the classification scheme.	String
  subclass	The third highest hierarchical level in the classification scheme.	String
  class/subclass	The second hierarchical level in the classification scheme/The third highest hierarchical level in the classification scheme.	String
correspondenceAddressBag	All address lines associated with applicant or inventor correspondence, depending on which bag it falls in.	N/A
  nameLineOneText	First line of name associated with correspondence address.	String
  nameLineTwoText	Second line of name associated with correspondence address, if applicable.	String
  addressLineOneText	First line of address associated with correspondence address.	String
  addressLineTwoText	Second line of address associated with correspondence address, if applicable.	String
  geographicRegionName	Geographic Region Name, e.g., state.	String
  geographicRegionCode	Geographic region code.	String
  postalCode	Postal Code.	String
  cityName	City Name.	String
  countryCode	Country code.	String
  countryName	Country name.	String
  postalAddressCategory	Postal address category.	String
customerNumber	Correspondence Address of the application inherited from the Customer.	Number
cpcClassificationBag	All the CPCs associated to application.	String
applicantBag	All applicants associated to application.	N/A
  firstName	First Name.	String
  middleName	Middle name.	String
  lastName	Last Name.	String
  preferredName	Preferred name.	String
  namePrefix	Name prefix.	String
  nameSuffix	Name suffix.	String
  countryCode	Country code.	String
correspondenceAddressBag	All address lines associated with applicant or inventor correspondence, depending on which bag it falls in.	N/A
  nameLineOneText	First line of name associated with correspondence address.	String
  nameLineTwoText	Second line of name associated with correspondence address, if applicable.	String
  addressLineOneText	First line of address associated with correspondence address.	String
  addressLineTwoText	Second line of address associated with correspondence address, if applicable.	String
  geographicRegionName	Geographic Region Name, e.g., state.	String
  geographicRegionCode	Geographic region code.	String
  postalCode	Postal Code.	String
  cityName	City Name.	String
  countryCode	Country code.	String
  countryName	Country name.	String
  postalAddressCategory	Postal address category.	String
  applicant	The name of the applicant	String
inventorBag	All the inventors associated to application.	N/A
  firstName	First Name.	String
  middleName	Middle name.	String
  lastName	Last Name.	String
  preferredName	Preferred name.	String
  namePrefix	Name prefix.	String
  nameSuffix	Name suffix.	String
  countryCode	Country code.	String
  inventorNameText	Inventor Name.	String
correspondenceAddressBag	All address lines associated with applicant or inventor correspondence, depending on which bag it falls in.	N/A
  nameLineOneText	First line of name associated with correspondence address.	String
  nameLineTwoText	Second line of name associated with correspondence address, if applicable.	String
  addressLineOneText	First line of address associated with correspondence address.	String
  addressLineTwoText	Second line of address associated with correspondence address, if applicable.	String
  geographicRegionName	Geographic Region Name, e.g., state.	String
  geographicRegionCode	Geographic region code.	String
  postalCode	Postal Code.	String
  cityName	City Name.	String
  countryCode	Country code.	String
  countryName	Country name.	String
  postalAddressCategory	Postal address category.	String
assignmentBag	The collection of assignment data	N/A
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
assigneeAddress	Assignee address data.	N/A
  addressLineOneText	First line of address.	String
  addressLineTwoText	Second line of address.	String
  cityName	City	String
  geographicRegionName	Geographic region name.	String
  geographicRegionCode	Geographic region code.	String
  countryName	Country name.	String
  postalCode	Postal code.	String
correspondenceAddressBag	Correspondence data collection	N/A
  correspondentNameText	The name of the correspondent	String
  addressLineOneText	Address line one.	String
  addressLineTwoText	Address line two.	String
  addressLineThreeText	Address line three, if existing	String
  addressLineFourText	Address line four, if existing	String
recordAttorney	Details of the attorney or agent associated with an application/patent.	N/A
customerNumber	Customer data.	N/A
  patronIdentifier	The unique identifier of the patron	String
  organizationStandardName	Organization standard name	String
powerOfAttorneyAddressBag	Power of attorney address data collection.	N/A
  nameLineOneText	First line of name associated with attorney/agent correspondence address.	String
  addressLineOneText	First line of the address	String
  addressLineTwoText	Second line of the address	String
  geographicRegionName	Geographic region name	String
  geographicRegionCode	Geographic region code	String
  postalCode	Postal code	String
  cityName	City name	String
  countryCode	Country code	String
  countryName	Country name	String
telecommunicationAddressBag	List of telecommunication addresses, such as the phone number(s) associated with the aforementioned attorney or agent.	N/A
  telecommunicationNumber	Telecommunication number, such as the phone number associated with the aforementioned attorney or agent.	String
  extensionNumber	Telephone extension number.	String
  usageTypeCategory	Usage type category, such as the type of phone number associated with the aforementioned attorney or agent.	String
attorneyBag	Data on file for all attorneys or agents associated with the application.	N/A
  firstName	First Name.	String
  lastName	Last Name.	String
  registrationNumber	Registration number.	Number
  activeIndicator	Status of whether attorney is active or inactive.	Boolean
telecommunicationAddressBag	List of telecommunication addresses, such as the phone number(s) associated with the aforementioned attorney or agent.	N/A
  telecommunicationNumber	Telecommunication number, such as the phone number associated with the aforementioned attorney or agent.	String
  extensionNumber	Telephone extension number.	Number
  usageTypeCategory	Usage type category, such as the type of phone number associated with the aforementioned attorney or agent.	String
foreignPriorityBag	Contains information about relevant foreign priority.	N/A
  countryName	The complete, non abbreviated name of a nation designated for a country according to the International Organization for Standardization (ISO) under International Standard 3166-1.	String
  filingDate	The date on which a priority claim was filed.	Date
  priorityNumberText	This represents the filing identifier assigned by the country processing the priority claim. Format varies by country.	N/A
continuityBag	All continuity data related to an application.	N/A
parentContinuityBag	All continuity details related to the parent application.	N/A
  aiaIndicator	America Invents Act (AIA) indicator, which indicates first inventor to file.	Boolean
  applicationStatusCode	This data element classifies the application by its status relative to the total application process.	Number
  patentNumber	The number that uniquely identifies an issued patent. It is also the document number in the USTPO-published Redbook and the Official Gazette. This number can be for an originally-issued patent or a re-issued patent. It will not be for a Re-exam Certificate, a Correction Certificate, a SIR, or a notice of a request for a Re-exam or a Reissue. This number is equivalent to WIPO ST.9 as INID 11. 5012717.	String
  applicationStatusDescriptionText	Status of the parent or child application, depending on which bag it falls under; values: new = new application, patented case, patent expired...	String
  filingDate	Date on which a patent application was filed and received in the USPTO.	Date
  parentApplicationNumberText	Application number of the parent application, which is the unique value assigned by the USPTO to a patent application upon receipt.	String
  childApplicationNumberText	Application number of the child application, which is the unique value assigned by the USPTO to a patent application upon receipt.	String
  claimParentageTypeCode	Claim parentage type code.	String
  claimParentageTypeCodeDescription	Claim Parentage Type Code Description	String
childContinuityBag	All continuity details related to the child application	N/A
  applicationStatusCode	Application status code.	String
  parentApplicationNumberText	Parent application number for this child application.	String
  childApplicationNumberText	Application number of the child application, which is the unique value assigned by the USPTO to a patent application upon receipt.	String
  applicationStatusDescriptionText	Status of the parent or child application, depending on which bag it falls under; values: new = new application, patented case, patent expired...	String
  filingDate	Date on which a patent application was filed and received in the USPTO.	Date
  aiaIndicator	America Invents Act (AIA) indicator, which indicates first inventor to file.	Boolean
  patentNumber	The number that uniquely identifies an issued patent. It is also the document number in the USTPO-published Redbook and the Official Gazette. This number can be for an originally-issued patent or a re-issued patent. It will not be for a Re-exam Certificate, a Correction Certificate, a SIR, or a notice of a request for a Re-exam or a Reissue. This number is equivalent to WIPO ST.9 as INID 11. 5012717.	String
  claimParentageTypeCode	Claim parentage type code.	String
  claimParentageTypeCodeDescription	Description of claim parentage type	String
patentTermAdjustmentData	Patent term adjustment data.	N/A
    aDelayQuantity	This entry reflects adjustments to the term of the patent based upon USPTO delays pursuant to 35 U.S.C. § 154(b)(1)(A)(i)-(iv) and the implementing regulations 37 CFR 1.702(a) & 37 CFR 1.703(a). An "A" delay may occur prior to the notice of allowance and be included in the PTA determination accompanying the notice of allowance or may occur after the entry or mailing of the notice of allowance and be included in the PTA determination in the issue notification letter.	Number
    adjustmentTotalQuantity	This entry reflects the summation of the following entries: NONOVERLAPPING USPTO DELAYS (+/or – USPTO MANUAL ADJUSTMENTS) – APPLICANT DELAYS. It is noted that the TOTAL PTA CALCULATION determined at the time of the notice of allowance will not reflect PALM entries that are entered after the entry or mailing of the notice of allowance.	Number
    applicantDayDelayQuantity	This entry reflects adjustments of the patent term due to the Applicant's failure to engage in reasonable efforts to conclude prosecution of the application for the cumulative period in excess of three months. See 35 U.S.C. § 154(b)(2)(C)(ii) and implementing regulation 37 CFR 1.704(b). The entry also reflects additional Applicant's failure to engage in reasonable efforts to conclude prosecution of the application. See 35 U.S.C. § 154(b)(2)(C)(iii) and implementing regulations 37 CFR 1.704(c)(1)-(11).	Number
    bDelayQuantity	This entry reflects adjustments to the term of the patent based upon the patent failing to issue within three years of the actual filing date of the application in the United States. See 35 U.S.C. § 154(b) and implementing regulations 37 CFR 1.702(b) & 1.703(b). "B" delay is always calculated at the time that the issue notification letter is generated and an issue date has been established.	Number
    cDelayQuantity	This entry reflects adjustments to the term of the patent based upon USPTO delays pursuant to 35 U.S.C. § 154(C)(i)-(iii) and implementing regulations 37 CFR 1.702 (c)-(e) & 1.703(c)-(e). These delays include delays caused by interference proceedings, secrecy orders, and successful appellate reviews.	Number
    filingDate	The date assigned by the USPTO that identifies when a patent application meets certain criteria to qualify as having been "filed."	Date
    grantDate	Date on which the patent application was granted/issued.	Date
    nonOverlappingDayQuantity	This entry reflects the overall summation of the USPTO delays minus any overlapping days. Particularly, it includes the following: ("A" delays + "B" delays + "C" delays) - (the number of calendar days overlapping between "A" delays and "B" delays + the number of calendar days overlapping between "A" delays and "C" delays). This entry does not reflect the number of days of applicant delays pursuant to 35 U.S.C. § 154(b)(2)(C) and 37 CFR 1.704(b) and 37 CFR 1.704(c)(1)-(11).	Number
    overlappingDayQuantity	Patent term adjustment overlapping days quantity number that reflects the calculation of overlapping delays consistent with the federal circuit's interpretation.	Number
    ipOfficeDayDelayQuantity	This entry reflects the UPSTO personnel adjusting the calculation to increase or decrease the patent term adjustment based upon either an application for patent term adjustment pursuant to 37 CFR 1.705(b) or a request for reconsideration of the patent term adjustment under 37 CFR 1.705(d). In addition, the USPTO may reduce the PTA determination in response to a letter of good faith and candor regarding PTA advising the USPTO that the USPTO may have granted more PTA than applicant/patentee is entitled.	Number
    patentTermAdjustmentHistoryDataBag	The recordation of patent case actions that are involved in the patent term adjustment calculation.	N/A
      actionDate	The date that the symbol was assigned to the patent document.	Date
      applicantDays	This entry reflects adjustments of the patent term due to the Applicant's failure to engage in reasonable efforts to conclude prosecution of the application for the cumulative period in excess of three months. See 35 U.S.C. § 154(b)(2)(C)(ii) and implementing regulation 37 CFR 1.704(b). The entry also reflects additional Applicant's failure to engage in reasonable efforts to conclude prosecution of the application. See 35 U.S.C. § 154(b)(2)(C)(iii) and implementing regulations 37 CFR 1.704(c)(1)-(11)	Number
      caseActionDescriptionText	Case action description.	String
      caseActionSequenceNumber	Case action sequence number.	Number
      ipOfficeDayDelayQuantity	Number of days the UPSTO personnel adjusting the calculation to increase or decrease the patent term adjustment based upon a request for reconsideration of the patent term adjustment.	Number
      startSequenceNumber	Start sequence number.	Number
eventDataBag	Details of the contents of all transactions on an application/patent.	N/A
  eventCode	The unique reference value (number and letters) for an application/patent transaction.	String
  eventDescriptionText	Description of the Transaction's code.	String
  eventDate	The date the patent case action was recorded.	Date
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
lastIngestionTime	Date time when application was last modified.	Date
"""
