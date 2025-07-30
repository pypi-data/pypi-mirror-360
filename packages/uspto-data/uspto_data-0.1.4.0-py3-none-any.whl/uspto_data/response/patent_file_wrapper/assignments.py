from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from uspto_data.data_model import AssignorBag, AssigneeAddress, AssignmentCorrespondenceAddressBag, AssignmentBag, \
    AssignmentsRoot, AssignmentsPatentFileWrapperDataBag, AssigneeBag
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_assignor_bag(data: Dict[str, Any]) -> AssignorBag:
        return AssignorBag(
            assignorName=data.get("assignorName"),
            executionDate=data.get("executionDate"),
        )

    @staticmethod
    def parse_assignee_address(data: Dict[str, Any]) -> AssigneeAddress:
        return AssigneeAddress(
            addressLineOneText=data.get("addressLineOneText"),
            addressLineTwoText=data.get("addressLineTwoText"),
            cityName=data.get("cityName"),
            geographicRegionName=data.get("geographicRegionName"),
            geographicRegionCode=data.get("geographicRegionCode"),
            countryName=data.get("countryName"),
            postalCode=data.get("postalCode"),
        )

    @staticmethod
    def parse_assignee_bag(data: Dict[str, Any]) -> AssigneeBag:
        assignee_address = ResponseParser.parse_assignee_address(data.get("assigneeAddress", {}))
        return AssigneeBag(
            assigneeAddress=assignee_address,
            assigneeNameText=data.get("assigneeNameText"),
        )

    @staticmethod
    def parse_correspondence_address_bag(data: Dict[str, Any]) -> AssignmentCorrespondenceAddressBag:
        return AssignmentCorrespondenceAddressBag(
            correspondentNameText=data.get("correspondentNameText"),
            addressLineOneText=data.get("addressLineOneText"),
            addressLineTwoText=data.get("addressLineTwoText"),
            addressLineThreeText=data.get("addressLineThreeText"),
            addressLineFourText=data.get("addressLineFourText"),
        )

    @staticmethod
    def parse_assignment_bag(data: Dict[str, Any]) -> AssignmentBag:
        assignor_bags = [
            ResponseParser.parse_assignor_bag(assignor)
            for assignor in data.get("assignorBag", [])
        ]
        assignee_bags = [
            ResponseParser.parse_assignee_bag(assignee)
            for assignee in data.get("assigneeBag", [])
        ]
        correspondence_address = [
            ResponseParser.parse_correspondence_address_bag(corr_addr)
            for corr_addr in data.get("correspondenceAddressBag", [])
        ]
        return AssignmentBag(
            assignorBag=assignor_bags,
            assigneeBag=assignee_bags,
            correspondenceAddressBag=correspondence_address,
            reelNumber=data.get("reelNumber"),
            frameNumber=data.get("frameNumber"),
            reelNumber_frameNumber=data.get("reelNumber/frameNumber"),
            pageNumber=data.get("pageNumber"),
            assignmentReceivedDate=data.get("assignmentReceivedDate"),
            assignmentRecordedDate=data.get("assignmentRecordedDate"),
            assignmentMailedDate=data.get("assignmentMailedDate"),
            conveyanceText=data.get("conveyanceText"),
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> AssignmentsPatentFileWrapperDataBag:
        assignment_bag = ResponseParser.parse_assignment_bag(data.get("assignmentBag", {}))
        return AssignmentsPatentFileWrapperDataBag(
            assignmentBag=assignment_bag,
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> AssignmentsRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return AssignmentsRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> AssignmentsRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/assignment"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'patentFileWrapperDataBag': [{'assignmentBag': {'reelNumber': '60620', 'frameNumber': '769', 'reelNumber/frameNumber': '60620/769', 'pageNumber': 16, 'assignmentReceivedDate': '2022-07-11', 'assignmentRecordedDate': '2022-07-11', 'assignmentMailedDate': '2022-07-28', 'conveyanceText': 'ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).', 'assignorBag': [{'assignorName': 'STMICROELECTRONICS SA', 'executionDate': '2022-06-30'}], 'assigneeBag': [{'assigneeNameText': 'STMICROELECTRONICS SA', 'assigneeAddress': {'addressLineOneText': 'CHEMIN DU CHAMP-DES-FILLES 39', 'addressLineTwoText': '1228 PLAN-LES-OUATES', 'cityName': 'GENEVA', 'geographicRegionName': 'CHX', 'geographicRegionCode': 'string', 'countryName': 'Switzerland', 'postalCode': '20123'}}], 'correspondenceAddressBag': {'correspondentNameText': 'STMICROELECTRONICS, INC.', 'addressLineOneText': '750 CANYON DRIVE', 'addressLineTwoText': 'SUITE 300', 'addressLineThreeText': 'COPPELL, TX 75019', 'addressLineFourText': 'Address Line Four'}}}], 'requestIdentifier': 'bb38eb61-f05b-42f7-a4bd-2beac9fb15de'}

# import json
# from dataclasses import asdict
# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
