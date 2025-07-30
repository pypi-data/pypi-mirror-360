from typing import Dict, Any

from uspto_data.data_model import PatentTermAdjustmentHistoryDataBag, PatentTermAdjustmentData, \
    PatentTermAdjustmentPatentFileWrapperDataBag, PatentTermAdjustmentRoot
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_patent_term_adjustment_history_data_bag(data: Dict[str, Any]) -> PatentTermAdjustmentHistoryDataBag:
        return PatentTermAdjustmentHistoryDataBag(
            eventDate=data.get("eventDate"),
            applicantDayDelayQuantity=data.get("applicantDayDelayQuantity"),
            eventDescriptionText=data.get("eventDescriptionText"),
            eventSequenceNumber=data.get("eventSequenceNumber"),
            ipOfficeDayDelayQuantity=data.get("ipOfficeDayDelayQuantity"),
            originatingEventSequenceNumber=data.get("originatingEventSequenceNumber"),
            ptaPteCode=data.get("ptaPteCode"),
        )

    @staticmethod
    def parse_patent_term_adjustment_data(data: Dict[str, Any]) -> PatentTermAdjustmentData:
        history_data_bags = [
            ResponseParser.parse_patent_term_adjustment_history_data_bag(history)
            for history in data.get("patentTermAdjustmentHistoryDataBag", [])
        ]
        return PatentTermAdjustmentData(
            patentTermAdjustmentHistoryDataBag=history_data_bags,
            aDelayQuantity=data.get("aDelayQuantity"),
            adjustmentTotalQuantity=data.get("adjustmentTotalQuantity"),
            applicantDayDelayQuantity=data.get("applicantDayDelayQuantity"),
            bDelayQuantity=data.get("bDelayQuantity"),
            cDelayQuantity=data.get("cDelayQuantity"),
            filingDate=data.get("filingDate"),
            grantDate=data.get("grantDate"),
            nonOverlappingDayQuantity=data.get("nonOverlappingDayQuantity"),
            overlappingDayQuantity=data.get("overlappingDayQuantity"),
            ipOfficeDayDelayQuantity=data.get("ipOfficeDayDelayQuantity"),
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> PatentTermAdjustmentPatentFileWrapperDataBag:
        patent_term_adjustment_data = ResponseParser.parse_patent_term_adjustment_data(data.get("patentTermAdjustmentData", {}))
        return PatentTermAdjustmentPatentFileWrapperDataBag(
            patentTermAdjustmentData=patent_term_adjustment_data,
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> PatentTermAdjustmentRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return PatentTermAdjustmentRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> PatentTermAdjustmentRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/adjustment"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'patentFileWrapperDataBag': [{'applicationNumberText': '12620694', 'patentTermAdjustmentData': {'aDelayQuantity': 0, 'adjustmentTotalQuantity': 0, 'applicantDayDelayQuantity': 28, 'bDelayQuantity': 0, 'cDelayQuantity': 0, 'filingDate': '2013-12-12', 'grantDate': '2016-06-07', 'nonOverlappingDayQuantity': 0, 'overlappingDayQuantity': 0, 'ipOfficeDayDelayQuantity': 0, 'patentTermAdjustmentHistoryDataBag': [{'eventDate': '2016-06-07', 'applicantDayDelayQuantity': 4, 'eventDescriptionText': 'Patent Issue Date Used in PTA Calculation', 'eventSequenceNumber': 65, 'ipOfficeDayDelayQuantity': 0, 'originatingEventSequenceNumber': 0, 'ptaPteCode': 'PTA'}]}}], 'requestIdentifier': 'df5b5478-ad3e-4ad2-b3bc-611838ccb56c'}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
