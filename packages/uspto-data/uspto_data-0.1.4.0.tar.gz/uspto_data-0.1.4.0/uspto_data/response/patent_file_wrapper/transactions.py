from typing import Dict, Any

from uspto_data.data_model import EventDataBag, TransactionsPatentFileWrapperDataBag, TransactionsRoot
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_event_data_bag(data: Dict[str, Any]) -> EventDataBag:
        return EventDataBag(
            eventCode=data.get("eventCode"),
            eventDescriptionText=data.get("eventDescriptionText"),
            eventDate=data.get("eventDate"),
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> TransactionsPatentFileWrapperDataBag:
        event_data_bags = [
            ResponseParser.parse_event_data_bag(event)
            for event in data.get("eventDataBag", [])
        ]
        return TransactionsPatentFileWrapperDataBag(
            eventDataBag=event_data_bags,
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> TransactionsRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return TransactionsRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> TransactionsRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/transactions"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'patentFileWrapperDataBag': [{'applicationNumberText': '12620694', 'eventDataBag': [{'eventCode': 'ELC_RVW', 'eventDescriptionText': 'Electronic Review', 'eventDate': '2018-10-18'}]}], 'requestIdentifier': 'df5b5478-ad3e-4ad2-b3bc-611838ccb56c'}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
