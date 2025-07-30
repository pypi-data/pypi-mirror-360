from typing import Dict, Any

from uspto_data.data_model import PgPubDocumentMetaData, GrantDocumentMetaData, AssociatedDocsPatentFileWrapperDataBag, \
    AssociatedDocsRoot
from uspto_data.response import response_interface


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_pgpub_document_meta_data(data: Dict[str, Any]) -> PgPubDocumentMetaData:
        return PgPubDocumentMetaData(
            zipFileName=data.get("zipFileName"),
            productIdentifier=data.get("productIdentifier"),
            fileLocationURI=data.get("fileLocationURI"),
            fileCreateDateTime=data.get("fileCreateDateTime"),
            xmlFileName=data.get("xmlFileName"),
        )

    @staticmethod
    def parse_grant_document_meta_data(data: Dict[str, Any]) -> GrantDocumentMetaData:
        return GrantDocumentMetaData(
            zipFileName=data.get("zipFileName"),
            productIdentifier=data.get("productIdentifier"),
            fileLocationURI=data.get("fileLocationURI"),
            fileCreateDateTime=data.get("fileCreateDateTime"),
            xmlFileName=data.get("xmlFileName"),
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> AssociatedDocsPatentFileWrapperDataBag:
        pgpub_meta_data = ResponseParser.parse_pgpub_document_meta_data(data.get("pgpubDocumentMetaData", {}))
        grant_meta_data = ResponseParser.parse_grant_document_meta_data(data.get("grantDocumentMetaData", {}))
        return AssociatedDocsPatentFileWrapperDataBag(
            pgpubDocumentMetaData=pgpub_meta_data,
            grantDocumentMetaData=grant_meta_data,
            applicationNumberText=data.get("applicationNumberText"),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> AssociatedDocsRoot:
        patent_file_wrapper_data_bags = [
            ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
            for wrapper in data.get("patentFileWrapperDataBag", [])
        ]
        return AssociatedDocsRoot(
            patentFileWrapperDataBag=patent_file_wrapper_data_bags,
            count=data.get("count"),
            requestIdentifier=data.get("requestIdentifier"),
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> AssociatedDocsRoot:
        return ResponseParser.parse_root(response)


endpoint = "/api/v1/patent/applications/{applicationNumberText}/associated-documents"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'patentFileWrapperDataBag': [{'applicationNumberText': '14104993', 'pgpubDocumentMetaData': {'zipFileName': 'ipa240801.zip', 'productIdentifier': 'APPXML', 'fileLocationURI': 'https://bulkdata.uspto.gov/data/patent/application/redbook/fulltext/2024/ipa240104.zip', 'fileCreateDateTime': '2024-08-09:11:30:00', 'xmlFileName': 'ipa240801.xml'}, 'grantDocumentMetaData': {'zipFileName': 'ipg240102.zip', 'productIdentifier': 'PTGRXML', 'fileLocationURI': 'https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2016/ipg160405.zip', 'fileCreateDateTime': '2024-08-09:11:30:00', 'xmlFileName': 'ipg160405.xml'}}], 'requestIdentifier': '0ff4c603-a290-4659-8092-f68b408150c4'}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
