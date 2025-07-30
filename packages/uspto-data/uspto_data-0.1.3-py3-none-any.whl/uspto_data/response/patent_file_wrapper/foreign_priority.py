from typing import Dict, Any

from uspto_data.data_model import ForeignPriorityBag, ForeignPriorityRoot, ForeignPriorityPatentFileWrapperDataBag
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_foreign_priority_bag(data: Dict[str, Any]) -> ForeignPriorityBag:
        return ForeignPriorityBag(
            ipOfficeName=data.get("ipOfficeName"),
            filingDate=data.get("filingDate"),
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> ForeignPriorityPatentFileWrapperDataBag:
        foreign_priority_bags = [
            ResponseParser.parse_foreign_priority_bag(priority)
            for priority in data.get("foreignPriorityBag", [])
        ]
        return ForeignPriorityPatentFileWrapperDataBag(
            foreignPriorityBag=foreign_priority_bags,
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> ForeignPriorityRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return ForeignPriorityRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> ForeignPriorityRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/foreign-priority"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'patentFileWrapperDataBag': [{'applicationNumberText': '12620694', 'foreignPriorityBag': [{'ipOfficeName': 'FRANCE', 'filingDate': '2012-12-19', 'applicationNumberText': '08 020 164.3'}]}], 'requestIdentifier': 'df5b5478-ad3e-4ad2-b3bc-611838ccb56c'}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
