# ENDPOINT
endpoint = "/api/v1/patent/applications/{applicationNumberText}/attorney"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "patentFileWrapperDataBag": [
    {
      "applicationNumberText": "14104993",
      "recordAttorney": {
        "customerNumber": [
          {
            "patronIdentifier": 0,
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
                "telecomTypeCode": "string"
              }
            ]
          }
        ],
        "powerOfAttorneyBag": [
          {
            "firstName": "DANIEL",
            "middleName": "D",
            "lastName": "O'BRIEN",
            "namePrefix": "Dr",
            "nameSuffix": "Jr.",
            "preferredName": "string",
            "countryCode": "string",
            "registrationNumber": "65545",
            "activeIndicator": "ACTIVE",
            "registeredPractitionerCategory": "string",
            "attorneyAddressBag": [
              {
                "nameLineOneText": "string",
                "nameLineTwoText": "string",
                "addressLineOneText": "string",
                "addressLineTwoText": "string",
                "geographicRegionName": "string",
                "geographicRegionCode": "string",
                "postalCode": "string",
                "cityName": "string",
                "countryCode": "string",
                "countryName": "string"
              }
            ],
            "telecommunicationAddressBag": [
              {
                "telecommunicationNumber": "206-622-4900",
                "extensionNumber": "243",
                "telecomTypeCode": "TEL"
              }
            ]
          }
        ],
        "attorneyBag": [
          {
            "firstName": "DANIEL",
            "middleName": "D",
            "lastName": "O'BRIEN",
            "namePrefix": "Dr",
            "nameSuffix": "Jr.",
            "registrationNumber": "65545",
            "activeIndicator": "ACTIVE",
            "registeredPractitionerCategory": "string",
            "attorneyAddressBag": [
              {
                "nameLineOneText": "string",
                "nameLineTwoText": "string",
                "addressLineOneText": "string",
                "addressLineTwoText": "string",
                "geographicRegionName": "string",
                "geographicRegionCode": "string",
                "postalCode": "string",
                "cityName": "string",
                "countryCode": "string",
                "countryName": "string"
              }
            ],
            "telecommunicationAddressBag": [
              {
                "telecommunicationNumber": "206-622-4900",
                "extensionNumber": "243",
                "telecomTypeCode": "TEL"
              }
            ]
          }
        ]
      }
    }
  ],
  "requestIdentifier": "df5b5478-ad3e-4ad2-b3bc-611838ccb56c"
}

documentation = """
The Address and Attorney/Agent Information section provides additional information concerning the attorney/agent related to a patent, including the associated attorney/agent's address. Use this endpoint when you want address and attorney/agent information related to a specific patent application whose application number you know. You can test APIs right away in Swagger UI.

This dataset includes published patent applications and issued patent data filed after January 1, 2001. This data is refreshed daily.

GET /api/v1/patent/applications/{applicationNumberText}/attorney

Returns attorney/agent data for supplied application number.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
recordAttorney	Details of the attorney or agent associated with an application/patent.	N/A
  customerNumber	Customer number	String
  patronIdentifier	Patron identifier	Number
  organizationStandardName	Organization standard name	String
powerOfAttorneyAddressBag	Collection of power of attorney address	N/A
  nameLineOneText	First line of name associated with attorney/agent correspondence address.	String
  nameLineTwoText	Second line of name associated with attorney/agent correspondence address.	String
  addressLineOneText	First line of address associated with attorney/agent correspondence address.	String
  addressLineTwoText	Second line of address associated with attorney/agent correspondence address.	String
  geographicRegionName	Geographic region name, e.g., state or province.	String
  geographicRegionCode	Geographic region code.	String
  postalCode	Postal code.	String
  cityName	City name.	String
  countryCode	Country code.	String
  countryName	Country name.	String
telecommunicationAddressBag	List of telecommunication addresses, such as the phone number(s) associated with the aforementioned attorney or agent.	N/A
  telecommunicationNumber	Telecommunication number, such as the phone number associated with the aforementioned attorney or agent.	String
  extensionNumber	Telecommunication extension	String
  telecomTypeCode	Telecommunication type code e.g: PHONE, FAX	String
powerOfAttorneyBag	Collection of power of attorney data	N/A
  nameLineOneText	First line of name associated with attorney/agent correspondence address.	String
  nameLineTwoText	Second line of name associated with attorney/agent correspondence address.	String
powerOfAttorneyBag	Power of attorney address data	N/A
  firstName	First name	String
  middleName	Middle name	String
  lastName	Last name	String
  namePrefix	Name prefix	String
  nameSuffix	Name suffix	String
  preferredName	Preferred name	String
  countryCode	Country code	String
  registrationNumber	Registration number	String
  activeIndicator	Active indicator	String
  registeredPractitionerCategory	Practitioner category	String
attorneyAddressBag	Attorney address bag	String
  nameLineOneText	First line of name associated with attorney/agent correspondence address.	String
  nameLineTwoText	Second line of name associated with attorney/agent correspondence address.	String
  addressLineOneText	First line of address associated with attorney/agent correspondence address.	String
  addressLineTwoText	Second line of address associated with attorney/agent correspondence address.	String
  geographicRegionName	Geographic region name, e.g., state or province.	String
  geographicRegionCode	Geographic region code.	String
  postalCode	Postal code.	String
  cityName	City name.	String
  countryCode	Country code.	String
  countryName	Country name.	String
telecommunicationAddressBag	List of telecommunication addresses, such as the phone number(s) associated with the aforementioned attorney or agent.	N/A
  telecommunicationNumber	Telecommunication number	String
  extensionNumber	Telecommunication extension	String
  telecomTypeCode	Telecommunication type code e.g: PHONE, FAX	String
attorneyBag	Power of attorney address data	N/A
  firstName	First name	String
  middleName	Middle name	String
  lastName	Last name	String
  namePrefix	Name prefix	String
  nameSuffix	Name suffix	String
  registrationNumber	Registration number	String
  activeIndicator	Active indicator	String
  registeredPractitionerCategory	Practitioner category	String
attorneyAddressBag	All the elements of the address that is on file for the attorney or agent associated with the application.	String
  nameLineOneText	First line of name associated with attorney/agent correspondence address.	String
  nameLineTwoText	Second line of name associated with attorney/agent correspondence address.	String
  addressLineOneText	First line of address associated with attorney/agent correspondence address.	String
  addressLineTwoText	Second line of address associated with attorney/agent correspondence address.	String
  geographicRegionName	Geographic region name, e.g., state or province.	String
  geographicRegionCode	Geographic region code.	String
  postalCode	Postal code.	String
  cityName	City name.	String
  countryCode	Country code.	String
  countryName	Country name.	String
telecommunicationAddressBag	List of telecommunication addresses, such as the phone number(s) associated with the aforementioned attorney or agent.	N/A
  telecommunicationNumber	Telecommunication number	String
  extensionNumber	Telecommunication extension	String
  telecomTypeCode	Telecommunication type code e.g: PHONE, FAX	String
"""