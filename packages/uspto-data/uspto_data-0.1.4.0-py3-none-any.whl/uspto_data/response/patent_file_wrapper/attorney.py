from typing import Dict, Any

from uspto_data.data_model import PowerOfAttorneyAddressBag, CustomerNumber, TelecommunicationAddressBag, \
    AttorneyAddressBag, PowerOfAttorneyBag, AttorneyBag, RecordAttorney, AttorneyPatentFileWrapperDataBag, AttorneyRoot, \
    AttorneyRecordAttorney
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_power_of_attorney_address_bag(data: Dict[str, Any]) -> PowerOfAttorneyAddressBag:
        return PowerOfAttorneyAddressBag(
            nameLineOneText=data.get("nameLineOneText"),
            addressLineOneText=data.get("addressLineOneText"),
            addressLineTwoText=data.get("addressLineTwoText"),
            geographicRegionName=data.get("geographicRegionName"),
            geographicRegionCode=data.get("geographicRegionCode"),
            postalCode=data.get("postalCode"),
            cityName=data.get("cityName"),
            countryCode=data.get("countryCode"),
            countryName=data.get("countryName"),
        )

    @staticmethod
    def parse_telecommunication_address_bag(data: Dict[str, Any]) -> TelecommunicationAddressBag:
        return TelecommunicationAddressBag(
            telecommunicationNumber=data.get("telecommunicationNumber"),
            extensionNumber=data.get("extensionNumber"),
            telecomTypeCode=data.get("telecomTypeCode"),
        )

    @staticmethod
    def parse_customer_number(data: Dict[str, Any]) -> CustomerNumber:
        power_of_attorney_addresses = [
            ResponseParser.parse_power_of_attorney_address_bag(addr)
            for addr in data.get("powerOfAttorneyAddressBag", [])
        ]
        telecommunication_addresses = [
            ResponseParser.parse_telecommunication_address_bag(tel)
            for tel in data.get("telecommunicationAddressBag", [])
        ]
        return CustomerNumber(
            powerOfAttorneyAddressBag=power_of_attorney_addresses,
            telecommunicationAddressBag=telecommunication_addresses,
            patronIdentifier=data.get("patronIdentifier"),
            organizationStandardName=data.get("organizationStandardName"),
        )

    @staticmethod
    def parse_attorney_address_bag(data: Dict[str, Any]) -> AttorneyAddressBag:
        return AttorneyAddressBag(
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
        )

    @staticmethod
    def parse_power_of_attorney_bag(data: Dict[str, Any]) -> PowerOfAttorneyBag:
        attorney_addresses = [
            ResponseParser.parse_attorney_address_bag(addr)
            for addr in data.get("attorneyAddressBag", [])
        ]
        telecommunication_addresses = [
            ResponseParser.parse_telecommunication_address_bag(tel)
            for tel in data.get("telecommunicationAddressBag", [])
        ]
        return PowerOfAttorneyBag(
            attorneyAddressBag=attorney_addresses,
            telecommunicationAddressBag=telecommunication_addresses,
            firstName=data.get("firstName"),
            middleName=data.get("middleName"),
            lastName=data.get("lastName"),
            namePrefix=data.get("namePrefix"),
            nameSuffix=data.get("nameSuffix"),
            preferredName=data.get("preferredName"),
            countryCode=data.get("countryCode"),
            registrationNumber=data.get("registrationNumber"),
            activeIndicator=data.get("activeIndicator"),
            registeredPractitionerCategory=data.get("registeredPractitionerCategory"),
        )

    @staticmethod
    def parse_attorney_bag(data: Dict[str, Any]) -> AttorneyBag:
        attorney_addresses = [
            ResponseParser.parse_attorney_address_bag(addr)
            for addr in data.get("attorneyAddressBag", [])
        ]
        telecommunication_addresses = [
            ResponseParser.parse_telecommunication_address_bag(tel)
            for tel in data.get("telecommunicationAddressBag", [])
        ]
        return AttorneyBag(
            attorneyAddressBag=attorney_addresses,
            telecommunicationAddressBag=telecommunication_addresses,
            firstName=data.get("firstName"),
            middleName=data.get("middleName"),
            lastName=data.get("lastName"),
            namePrefix=data.get("namePrefix"),
            nameSuffix=data.get("nameSuffix"),
            registrationNumber=data.get("registrationNumber"),
            activeIndicator=data.get("activeIndicator"),
            registeredPractitionerCategory=data.get("registeredPractitionerCategory"),
        )

    @staticmethod
    def parse_record_attorney(data: Dict[str, Any]) -> AttorneyRecordAttorney:
        customer_numbers = [
            ResponseParser.parse_customer_number(customer)
            for customer in data.get("customerNumber", {}).get('powerOfAttorneyAddressBag', [])
        ]
        power_of_attorney_bags = [
            ResponseParser.parse_power_of_attorney_bag(power)
            for power in data.get("powerOfAttorneyBag", [])
        ]
        attorney_bags = [
            ResponseParser.parse_attorney_bag(attorney)
            for attorney in data.get("attorneyBag", [])
        ]
        return AttorneyRecordAttorney(
            customerNumber=customer_numbers,
            powerOfAttorneyBag=power_of_attorney_bags,
            attorneyBag=attorney_bags,
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> AttorneyPatentFileWrapperDataBag:
        record_attorney = ResponseParser.parse_record_attorney(data.get("recordAttorney", {}))
        return AttorneyPatentFileWrapperDataBag(
            recordAttorney=record_attorney,
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> AttorneyRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return AttorneyRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> AttorneyRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/attorney"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'patentFileWrapperDataBag': [{'applicationNumberText': '14104993', 'recordAttorney': {'customerNumber': [{'patronIdentifier': 0, 'organizationStandardName': 'string', 'powerOfAttorneyAddressBag': [{'nameLineOneText': 'Seed IP Law Group LLP/ST (EP ORIGINATING)', 'addressLineOneText': '701 FIFTH AVENUE, SUITE 5400', 'addressLineTwoText': 'Sample Line Two', 'geographicRegionName': 'ST', 'geographicRegionCode': 'string', 'postalCode': '98104-7092', 'cityName': 'SEATTLE', 'countryCode': 'US', 'countryName': 'UNITED STATES'}], 'telecommunicationAddressBag': [{'telecommunicationNumber': 'string', 'extensionNumber': 'string', 'telecomTypeCode': 'string'}]}], 'powerOfAttorneyBag': [{'firstName': 'DANIEL', 'middleName': 'D', 'lastName': "O'BRIEN", 'namePrefix': 'Dr', 'nameSuffix': 'Jr.', 'preferredName': 'string', 'countryCode': 'string', 'registrationNumber': '65545', 'activeIndicator': 'ACTIVE', 'registeredPractitionerCategory': 'string', 'attorneyAddressBag': [{'nameLineOneText': 'string', 'nameLineTwoText': 'string', 'addressLineOneText': 'string', 'addressLineTwoText': 'string', 'geographicRegionName': 'string', 'geographicRegionCode': 'string', 'postalCode': 'string', 'cityName': 'string', 'countryCode': 'string', 'countryName': 'string'}], 'telecommunicationAddressBag': [{'telecommunicationNumber': '206-622-4900', 'extensionNumber': '243', 'telecomTypeCode': 'TEL'}]}], 'attorneyBag': [{'firstName': 'DANIEL', 'middleName': 'D', 'lastName': "O'BRIEN", 'namePrefix': 'Dr', 'nameSuffix': 'Jr.', 'registrationNumber': '65545', 'activeIndicator': 'ACTIVE', 'registeredPractitionerCategory': 'string', 'attorneyAddressBag': [{'nameLineOneText': 'string', 'nameLineTwoText': 'string', 'addressLineOneText': 'string', 'addressLineTwoText': 'string', 'geographicRegionName': 'string', 'geographicRegionCode': 'string', 'postalCode': 'string', 'cityName': 'string', 'countryCode': 'string', 'countryName': 'string'}], 'telecommunicationAddressBag': [{'telecommunicationNumber': '206-622-4900', 'extensionNumber': '243', 'telecomTypeCode': 'TEL'}]}]}}], 'requestIdentifier': 'df5b5478-ad3e-4ad2-b3bc-611838ccb56c'}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
