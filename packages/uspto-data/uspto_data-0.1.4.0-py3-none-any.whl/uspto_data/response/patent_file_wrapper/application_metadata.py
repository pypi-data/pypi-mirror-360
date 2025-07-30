import json
from dataclasses import asdict
from typing import Dict, Any

from uspto_data.data_model import EntityStatusData, CorrespondenceAddressBag, ApplicantBag, InventorBag, \
    ApplicationMetaData, AppMetaPatentFileWrapperDataBag as PatentFileWrapperDataBag, AppMetaDataRoot
from uspto_data.response import response_interface

class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_entity_status_data(data: Dict[str, Any]) -> EntityStatusData:
        return EntityStatusData(
            smallEntityStatusIndicator=data.get("smallEntityStatusIndicator"),
            businessEntityStatusCategory=data.get("businessEntityStatusCategory"),
        )

    @staticmethod
    def parse_correspondence_address_bag(data: Dict[str, Any]) -> CorrespondenceAddressBag:
        return CorrespondenceAddressBag(
            nameLineOneText=data.get("nameLineOneText"),
            nameLineTwoText=data.get("nameLineTwoText"),
            addressLineOneText=data.get("addressLineOneText"),
            addressLineTwoText=data.get("addressLineTwoText"),
            geographicRegionName=data.get("geographicRegionName"),
            geographicRegionCode=data.get("geographicRegionCode"),
            postalCode=data.get("postalCode"),
            cityName=data.get("cityName"),
            countryCode=data.get("countryCode"),
            countryName=data.get("countryName"),
            postalAddressCategory=data.get("postalAddressCategory"),
        )

    @staticmethod
    def parse_applicant_bag(data: Dict[str, Any]) -> ApplicantBag:
        correspondence_addresses = [
            ResponseParser.parse_correspondence_address_bag(addr)
            for addr in data.get("correspondenceAddressBag", [])
        ]
        return ApplicantBag(
            correspondenceAddressBag=correspondence_addresses,
            applicantNameText=data.get("applicantNameText"),
            firstName=data.get("firstName"),
            middleName=data.get("middleName"),
            lastName=data.get("lastName"),
            preferredName=data.get("preferredName"),
            namePrefix=data.get("namePrefix"),
            nameSuffix=data.get("nameSuffix"),
            countryCode=data.get("countryCode"),
        )

    @staticmethod
    def parse_inventor_bag(data: Dict[str, Any]) -> InventorBag:
        correspondence_addresses = [
            ResponseParser.parse_correspondence_address_bag(addr)
            for addr in data.get("correspondenceAddressBag", [])
        ]
        return InventorBag(
            correspondenceAddressBag=correspondence_addresses,
            firstName=data.get("firstName"),
            middleName=data.get("middleName"),
            lastName=data.get("lastName"),
            namePrefix=data.get("namePrefix"),
            nameSuffix=data.get("nameSuffix"),
            preferredName=data.get("preferredName"),
            countryCode=data.get("countryCode"),
            inventorNameText=data.get("inventorNameText"),
        )

    @staticmethod
    def parse_application_metadata(data: Dict[str, Any]) -> ApplicationMetaData:
        entity_status_data = ResponseParser.parse_entity_status_data(data.get("entityStatusData", {}))
        applicant_bags = [
            ResponseParser.parse_applicant_bag(applicant)
            for applicant in data.get("applicantBag", [])
        ]
        inventor_bags = [
            ResponseParser.parse_inventor_bag(inventor)
            for inventor in data.get("inventorBag", [])
        ]
        return ApplicationMetaData(
            entityStatusData=entity_status_data,
            applicantBag=applicant_bags,
            inventorBag=inventor_bags,
            nationalStageIndicator=data.get("nationalStageIndicator"),
            publicationDateBag=data.get("publicationDateBag"),
            publicationSequenceNumberBag=data.get("publicationSequenceNumberBag"),
            publicationCategoryBag=data.get("publicationCategoryBag"),
            docketNumber=data.get("docketNumber"),
            firstInventorToFileIndicator=data.get("firstInventorToFileIndicator"),
            firstApplicantName=data.get("firstApplicantName"),
            firstInventorName=data.get("firstInventorName"),
            applicationConfirmationNumber=data.get("applicationConfirmationNumber"),
            applicationStatusDate=data.get("applicationStatusDate"),
            applicationStatusDescriptionText=data.get("applicationStatusDescriptionText"),
            filingDate=data.get("filingDate"),
            effectiveFilingDate=data.get("effectiveFilingDate"),
            grantDate=data.get("grantDate"),
            groupArtUnitNumber=data.get("groupArtUnitNumber"),
            applicationTypeCode=data.get("applicationTypeCode"),
            applicationTypeLabelName=data.get("applicationTypeLabelName"),
            applicationTypeCategory=data.get("applicationTypeCategory"),
            inventionTitle=data.get("inventionTitle"),
            patentNumber=data.get("patentNumber"),
            applicationStatusCode=data.get("applicationStatusCode"),
            earliestPublicationNumber=data.get("earliestPublicationNumber"),
            earliestPublicationDate=data.get("earliestPublicationDate"),
            pctPublicationNumber=data.get("pctPublicationNumber"),
            pctPublicationDate=data.get("pctPublicationDate"),
            internationalRegistrationPublicationDate=data.get("internationalRegistrationPublicationDate"),
            internationalRegistrationNumber=data.get("internationalRegistrationNumber"),
            examinerNameText=data.get("examinerNameText"),
            subclass=data.get("subclass"),
            class_=data.get("class"),
            class_subclass=data.get("class/subclass"),
            customerNumber=data.get("customerNumber"),
            cpcClassificationBag=data.get("cpcClassificationBag"),
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> PatentFileWrapperDataBag:
        application_metadata = ResponseParser.parse_application_metadata(data.get("applicationMetaData", {}))
        return PatentFileWrapperDataBag(
            applicationMetaData=application_metadata,
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> AppMetaDataRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return AppMetaDataRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> AppMetaDataRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/meta-data"

#  EXAMPLE JSON RESPONSE
example_json = {'count': 1, 'patentFileWrapperDataBag': [{'applicationNumberText': '14104993', 'applicationMetaData': {'nationalStageIndicator': True, 'entityStatusData': {'smallEntityStatusIndicator': True, 'businessEntityStatusCategory': 'Undiscounted'}, 'publicationDateBag': ['2014-06-19'], 'publicationSequenceNumberBag': ['167116'], 'publicationCategoryBag': [['Granted/Issued', 'Pre-Grant Publications - PGPub']], 'docketNumber': '12GR10425US01/859063.688', 'firstInventorToFileIndicator': 'Y', 'firstApplicantName': 'STMicroelectronics S.A.', 'firstInventorName': 'Pascal Chevalier', 'applicationConfirmationNumber': '1061', 'applicationStatusDate': '2016-05-18', 'applicationStatusDescriptionText': 'Patented Case', 'filingDate': '2012-12-19', 'effectiveFilingDate': '2013-12-12', 'grantDate': '2016-06-07', 'groupArtUnitNumber': 'TTAB', 'applicationTypeCode': 'UTL', 'applicationTypeLabelName': 'Utility', 'applicationTypeCategory': 'electronics', 'inventionTitle': 'HETEROJUNCTION BIPOLAR TRANSISTOR', 'patentNumber': '9362380', 'applicationStatusCode': 150, 'earliestPublicationNumber': 'US 2014-0167116 A1', 'earliestPublicationDate': '2014-06-19', 'pctPublicationNumber': 'WO 2009/064413', 'pctPublicationDate': '2016-12-16', 'internationalRegistrationPublicationDate': '2016-12-16', 'internationalRegistrationNumber': 'DM/091304', 'examinerNameText': 'HUI TSAI JEY', 'class': '257', 'subclass': '197000', 'class/subclass': '257/197000', 'customerNumber': 38106, 'cpcClassificationBag': ['H01L29/66325', 'H01L27/0623', 'H01L29/7378', 'H01L21/8249', 'H01L29/737', 'H01L29/66242'], 'applicantBag': [{'applicantNameText': 'John Smith', 'firstName': 'John', 'middleName': 'P', 'lastName': 'Smith', 'preferredName': 'John Smith', 'namePrefix': 'Mr.', 'nameSuffix': 'Jr.', 'countryCode': 'US', 'correspondenceAddressBag': [{'nameLineOneText': 'STMicroelectronics S.A.', 'nameLineTwoText': 'Name Line Two', 'addressLineOneText': 'Address Line 1', 'addressLineTwoText': 'Address Line 2', 'geographicRegionName': 'MN', 'geographicRegionCode': 'Region Code', 'postalCode': '10012', 'cityName': 'Montrouge', 'countryCode': 'FR', 'countryName': 'FRANCE', 'postalAddressCategory': 'commercial'}]}], 'inventorBag': [{'firstName': 'John', 'middleName': 'K', 'lastName': 'Smith', 'namePrefix': 'Mr.', 'nameSuffix': 'Sr.', 'preferredName': 'John Smith', 'countryCode': 'US', 'inventorNameText': 'Pascal Chevalier', 'correspondenceAddressBag': [{'nameLineOneText': 'Pascal  Chevalier', 'nameLineTwoText': 'Name Two', 'addressLineOneText': '197 Chemin de la Meuniere', 'addressLineTwoText': 'Line Two', 'geographicRegionName': 'Region Name', 'geographicRegionCode': 'FR', 'postalCode': '20125', 'cityName': 'Chapareillan', 'countryCode': 'FR', 'countryName': 'FRANCE', 'postalAddressCategory': 'commercial'}]}]}}], 'requestIdentifier': '0ff4c603-a290-4659-8092-f68b408150c4'}


if __name__ == "__main__":
    parsed_response = ResponseParser.parse_response(example_json)
    print(json.dumps(asdict(parsed_response), indent=2))
