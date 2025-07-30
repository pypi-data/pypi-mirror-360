from typing import Dict, Any

from uspto_data.data_model import DownloadOptionBag, DocumentBag, DocumentsRoot
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_download_option_bag(data: Dict[str, Any]) -> DownloadOptionBag:
        return DownloadOptionBag(
            mimeTypeIdentifier=data.get("mimeTypeIdentifier"),
            downloadURI=data.get("downloadURI"),
            downloadUrl=data.get("downloadUrl", ""),
            pageTotalQuantity=data.get("pageTotalQuantity"),
        )

    @staticmethod
    def parse_document_bag(data: Dict[str, Any]) -> DocumentBag:
        download_option_bags = [
            ResponseParser.parse_download_option_bag(option)
            for option in data.get("downloadOptionBag", [])
        ]
        return DocumentBag(
            downloadOptionBag=download_option_bags,
            applicationNumberText=data.get("applicationNumberText"),
            officialDate=data.get("officialDate"),
            documentIdentifier=data.get("documentIdentifier"),
            documentCode=data.get("documentCode"),
            documentCodeDescriptionText=data.get("documentCodeDescriptionText"),
            documentDirectionCategory=data.get("documentDirectionCategory"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> DocumentsRoot:
        document_bags = [
            ResponseParser.parse_document_bag(document)
            for document in data.get("documentBag", [])
        ]
        return DocumentsRoot(
            documentBag=document_bags,
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> DocumentsRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/document"

#  EXAMPLE JSON RESPONSE

example_json = {'documentBag': [{'applicationNumberText': '16123123', 'officialDate': '2020-08-31T01:20:29.000-0400', 'documentIdentifier': 'LDXBTPQ7XBLUEX3', 'documentCode': 'WFEE', 'documentCodeDescriptionText': 'Fee Worksheet (SB06)', 'documentDirectionCategory': 'INTERNAL', 'downloadOptionBag': [{'mimeTypeIdentifier': 'PDF', 'downloadURI': 'https://beta-api.uspto.gov/api/v1/patent/application/documents/16123123/LDXBTPQ7XBLUEX3.pdf', 'pageTotalQuantity': 2}]}]}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
