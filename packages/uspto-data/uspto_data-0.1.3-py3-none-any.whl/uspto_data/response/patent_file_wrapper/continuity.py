from typing import Dict, Any

from uspto_data.data_model import ParentContinuityBag, ChildContinuityBag, ContinuityRoot, \
    ContinuityPatentFileWrapperDataBag
from uspto_data.response import response_interface

class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_parent_continuity_bag(data: Dict[str, Any]) -> ParentContinuityBag:
        return ParentContinuityBag(
            firstInventorToFileIndicator=data.get("firstInventorToFileIndicator"),
            parentApplicationStatusCode=data.get("parentApplicationStatusCode"),
            parentPatentNumber=data.get("parentPatentNumber"),
            parentApplicationStatusDescriptionText=data.get("parentApplicationStatusDescriptionText"),
            parentApplicationFilingDate=data.get("parentApplicationFilingDate"),
            parentApplicationNumberText=data.get("parentApplicationNumberText"),
            childApplicationNumberText=data.get("childApplicationNumberText"),
            claimParentageTypeCode=data.get("claimParentageTypeCode"),
            claimParentageTypeCodeDescription=data.get("claimParentageTypeCodeDescription"),
        )

    @staticmethod
    def parse_child_continuity_bag(data: Dict[str, Any]) -> ChildContinuityBag:
        return ChildContinuityBag(
            childApplicationStatusCode=data.get("childApplicationStatusCode"),
            parentApplicationNumberText=data.get("parentApplicationNumberText"),
            childApplicationNumberText=data.get("childApplicationNumberText"),
            childApplicationStatusDescriptionText=data.get("childApplicationStatusDescriptionText"),
            childApplicationFilingDate=data.get("childApplicationFilingDate"),
            firstInventorToFileIndicator=data.get("firstInventorToFileIndicator"),
            childPatentNumber=data.get("childPatentNumber"),
            claimParentageTypeCode=data.get("claimParentageTypeCode"),
            claimParentageTypeCodeDescription=data.get("claimParentageTypeCodeDescription"),
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> ContinuityPatentFileWrapperDataBag:
        parent_continuity_bags = [
            ResponseParser.parse_parent_continuity_bag(parent)
            for parent in data.get("parentContinuityBag", [])
        ]
        child_continuity_bags = [
            ResponseParser.parse_child_continuity_bag(child)
            for child in data.get("childContinuityBag", [])
        ]
        return ContinuityPatentFileWrapperDataBag(
            parentContinuityBag=parent_continuity_bags,
            childContinuityBag=child_continuity_bags,
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> ContinuityRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return ContinuityRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> ContinuityRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/continuity"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'patentFileWrapperDataBag': [{'applicationNumberText': '14104993', 'parentContinuityBag': [{'firstInventorToFileIndicator': True, 'parentApplicationStatusCode': 159, 'parentPatentNumber': '8968299', 'parentApplicationStatusDescriptionText': 'Patent Expired Due to NonPayment of Maintenance Fees Under 37 CFR 1.362', 'parentApplicationFilingDate': '2012-05-23', 'parentApplicationNumberText': '123123133', 'childApplicationNumberText': 'string', 'claimParentageTypeCode': 'CODE', 'claimParentageTypeCodeDescription': 'some description'}], 'childContinuityBag': [{'childApplicationStatusCode': 150, 'parentApplicationNumberText': '14104993', 'childApplicationNumberText': '14853719', 'childApplicationStatusDescriptionText': 'Patented Case', 'childApplicationFilingDate': '2015-09-14', 'firstInventorToFileIndicator': False, 'childPatentNumber': '9704967', 'claimParentageTypeCode': 'DIV', 'claimParentageTypeCodeDescription': 'some desc'}]}], 'requestIdentifier': 'df5b5478-ad3e-4ad2-b3bc-611838ccb56c'}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
