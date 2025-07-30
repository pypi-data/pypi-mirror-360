endpoint = "/api/v1/patent/applications/{applicationNumberText}/meta-data"

example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "14104993",
      "applicationMetaData": {
        "nationalStageIndicator": True,
        "entityStatusData": {
          "smallEntityStatusIndicator": True,
          "businessEntityStatusCategory": "Undiscounted"
        },
        "publicationDateBag": [
          "2014-06-19"
        ],
        "publicationSequenceNumberBag": [
          "167116"
        ],
        "publicationCategoryBag": [
          [
            "Granted/Issued",
            "Pre-Grant Publications - PGPub"
          ]
        ],
        "docketNumber": "12GR10425US01/859063.688",
        "firstInventorToFileIndicator": "Y",
        "firstApplicantName": "STMicroelectronics S.A.",
        "firstInventorName": "Pascal Chevalier",
        "applicationConfirmationNumber": "1061",
        "applicationStatusDate": "2016-05-18",
        "applicationStatusDescriptionText": "Patented Case",
        "filingDate": "2012-12-19",
        "effectiveFilingDate": "2013-12-12",
        "grantDate": "2016-06-07",
        "groupArtUnitNumber": "TTAB",
        "applicationTypeCode": "UTL",
        "applicationTypeLabelName": "Utility",
        "applicationTypeCategory": "electronics",
        "inventionTitle": "HETEROJUNCTION BIPOLAR TRANSISTOR",
        "patentNumber": "9362380",
        "applicationStatusCode": 150,
        "earliestPublicationNumber": "US 2014-0167116 A1",
        "earliestPublicationDate": "2014-06-19",
        "pctPublicationNumber": "WO 2009/064413",
        "pctPublicationDate": "2016-12-16",
        "internationalRegistrationPublicationDate": "2016-12-16",
        "internationalRegistrationNumber": "DM/091304",
        "examinerNameText": "HUI TSAI JEY",
        "class": "257",
        "subclass": "197000",
        "class/subclass": "257/197000",
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
            "applicantNameText": "John Smith",
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
            ]
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
        ]
      }
    }
  ],
  "requestIdentifier": "0ff4c603-a290-4659-8092-f68b408150c4"
}

documentation = """
The Application Data section contains key bibliographic information found on the front page of granted patents and published patent applications. Use this endpoint when you want application data for a specific patent application whose application number you know. You can test APIs right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/meta-data

e.g. /api/v1/patent/applications/16330077/application-data

Returns application data for application number

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
PatentFileWrapperDataBag	Patent File Wrapper data.	N/A
  applicationNumberText	The unique value assigned by the PTO to a patent application upon receipt	String
entityStatusData	Entity status data	Entity status
  smallEntityStatusIndicator	Small entity status indicator	boolean
  businessEntityStatusCategory	Status of business The large-or-small-entity payment status of the APPLICATION PATENT CASE at the time of the small entity status event and thereafter until the occurrence of a later small entity status event for the APPLICATION PATENT CASE. entity being established for the purpose of paying a fee such as a filing fee and a maintenance fee	String
publicationDateBag	Publication dates	Array of dates
publicationSequenceNumberBag	Publication sequence number	N/A
publicationCategoryBag	One or more of the publication category	String
  docketNumber	Docket number	String
  firstInventorToFileIndicator	First inventor to file indicator	String
  firstApplicantName	First applicant name	String
  firstInventorName	First inventory name	String
  applicationConfirmationNumber	The application's confirmation number	String
  applicationStatusDate	The date of the application status	Date
  applicationStatusDescriptionText	status of the application; values: new = new application	String
  filingDate	The date the application is filed	Date
  effectiveFilingDate	Effective filing date	Date
  grantDate	Grant date	String
  groupArtUnitNumber	A working unit responsible for a cluster of related patent art. Generally, staffed by one supervisory patent examiner (SPE) and a number o patent examiners who determine patentability on applications for a patent. Group Art Units are currently identified by a four digit number, i.e., 1644.	String
  applicationTypeCode	The specific value that indicates if the received patent application is considered a domestic application at the National Stage or is submitted as a Patent Cooperative Treaty (PCT) application.	String
  applicationTypeLabelName	Application type label name	String
  applicationTypeCategory	Application type category	String
  inventionTitle	Invention Title	String
  patentNumber	The number that uniquely identifies an issued patent. It is also the document number in USTPO published Redbook and the Official Gazette. This number can be for an originally-issued patent or a re-issued patent. It will not be for a Re-exam Certificate, a Correction Certificate, a SIR, or a notice of a request for a Re-exam or a Reissue. This number is equivalent to WIPO ST.9 as INID 11. 5012717	String
  applicationStatusCode	Application status code	Number
  earliestPublicationNumber	Earliest publication number	String
  earliestPublicationDate	The first publication date	Date
  pctPublicationNumber	PCT publication number	String
  pctPublicationDate	PCT publication date	String
  internationalRegistrationPublicationDate	The date of publication by the International Bureau of an international registration of an industrial design	String
  internationalRegistrationNumber	The number assigned by the International Bureau to an international registration upon registering the industrial design in the International Register	String
  examinerNameText	Examiner's name	String
  class	Class	String
  subclass	Subclass	String
  class/subclass	Class/Subclass	String
  customerNumber	Correspondence Address of the application inherited from the Customer	String
cpcClassificationBag	CPC classification data collection	N/A
applicantBag	List of applicants	N/A
  applicantNameText	Applicant name	String
  firstName	First name of applicant	String
  middleName	Middle name of applicant	String
  lastName	Last name of application	String
  preferredName	Preferred name of applicant	String
  namePrefix	Name prefix	String
  nameSuffix	Name suffix	String
  countryCode	Country code	String
correspondenceAddressBag	Correspondence address data	N/A
  nameLineOneText	Name first line	String
  nameLineTwoText	Name second line	String
  addressLineOneText	First line of the correspondence	String
  addressLineTwoText	Second line of the correspondence	String
  geographicRegionName	Geographic region name	String
  geographicRegionCode	Geographic region code	String
  postalCode	Postal code	String
  cityName	City name	String
  countryCode	Country code	String
  countryName	Country Name	String
  postalAddressCategory	Postal category such as 'Residential' or 'Commercial'	String
inventorBag	All the inventors associated to application.	N/A
  firstName	First name of inventor	String
  middleName	Middle name of inventor	String
  lastName	Last name of inventor	String
  namePrefix	Name prefix	String
  nameSuffix	Name suffix	String
  preferredName	Preferred name of inventor	String
  countryCode	Country code	String
  inventorNameText	Inventor full name	String
correspondenceAddressBag	Correspondence address data	N/A
  nameLineOneText	Name line one	String
  nameLineTwoText	Name line two	String
  addressLineOneText	Address line one	String
  addressLineTwoText	Address line two	String
  geographicRegionName	Geographic region name	String
  geographicRegionCode	Geographic region code	String
  postalCode	Postal code	String
  cityName	City name	String
  countryCode	Country code	String
  countryName	Country name	String
  postalAddressCategory	Postal category such as 'Residential' or 'Commercial'	String
"""