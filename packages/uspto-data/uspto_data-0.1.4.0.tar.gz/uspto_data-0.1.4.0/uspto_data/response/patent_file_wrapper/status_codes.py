from typing import Dict, Any

from uspto_data.data_model import StatusCodeBag, StatusCodesRoot
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_status_code_bag(data: Dict[str, Any]) -> StatusCodeBag:
        return StatusCodeBag(
            applicationStatusCode=data.get("applicationStatusCode"),
            applicationStatusDescriptionText=data.get("applicationStatusDescriptionText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> StatusCodesRoot:
        status_code_bags = [
            ResponseParser.parse_status_code_bag(code)
            for code in data.get("statusCodeBag", [])
        ]
        return StatusCodesRoot(
            statusCodeBag=status_code_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> StatusCodesRoot:
        return ResponseParser.parse_root(response)


endpoint = "/patent/status-codes"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'statusCodeBag': [{'applicationStatusCode': 3, 'applicationStatusDescriptionText': 'Proceedings Terminated'}], 'requestIdentifier': 'df5b5478-ad3e-4ad2-b3bc-611838ccb56c'}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
