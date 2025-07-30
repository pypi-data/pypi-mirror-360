from dataclasses import dataclass, field
from typing import List, Optional

from uspto_data.response import response_interface


@dataclass
class FileDataBag:
    fileName: Optional[str] = None
    fileSize: Optional[int] = None
    fileDataFromDate: Optional[str] = None
    fileDataToDate: Optional[str] = None
    fileTypeText: Optional[str] = None
    fileDownloadURI: Optional[str] = None
    fileReleaseDate: Optional[str] = None
    fileDate: Optional[str] = None
    fileLastModified: Optional[str] = None


@dataclass
class ProductFileBag:
    fileDataBag: List[FileDataBag] = field(default_factory=list)
    count: Optional[int] = None


@dataclass
class BulkDataProductBag:
    productFileBag: ProductFileBag
    productIdentifier: Optional[str] = None
    productDescriptionText: Optional[str] = None
    productTitleText: Optional[str] = None
    productFrequencyText: Optional[str] = None
    daysOfWeekText: Optional[str] = None
    productLabelArrayText: Optional[List[str]] = field(default_factory=list)
    productFromDate: Optional[str] = None
    productToDate: Optional[str] = None
    productTotalFileSize: Optional[int] = None
    productFileTotalQuantity: Optional[int] = None
    modifiedDateTime: Optional[str] = None
    mimeTypeIdentifierArrayText: Optional[List[str]] = field(default_factory=list)


@dataclass
class ProductsRoot:
    bulkDataProductBag: List[BulkDataProductBag] = field(default_factory=list)
    count: Optional[int] = None


class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_file_data_bag(data) -> List[FileDataBag]:
        return [FileDataBag(**file_data) for file_data in data]

    @staticmethod
    def parse_product_file_bag(data) -> ProductFileBag:
        file_data_bag = data.get("fileDataBag", [])
        return ProductFileBag(
            fileDataBag=ResponseParser.parse_file_data_bag(file_data_bag),
            count=data.get("count")
        )

    @staticmethod
    def parse_bulk_data_product_bag(data) -> List[BulkDataProductBag]:
        bulk_data = []
        for item in data:
            product_file_bag_data = item.get("productFileBag", {})
            product_file_bag = ResponseParser.parse_product_file_bag(product_file_bag_data)
            bulk_data.append(
                BulkDataProductBag(
                    productFileBag=product_file_bag,
                    productIdentifier=item.get("productIdentifier"),
                    productDescriptionText=item.get("productDescriptionText"),
                    productTitleText=item.get("productTitleText"),
                    productFrequencyText=item.get("productFrequencyText"),
                    daysOfWeekText=item.get("daysOfWeekText"),
                    productLabelArrayText=item.get("productLabelArrayText", []),
                    productFromDate=item.get("productFromDate"),
                    productToDate=item.get("productToDate"),
                    productTotalFileSize=item.get("productTotalFileSize"),
                    productFileTotalQuantity=item.get("productFileTotalQuantity"),
                    modifiedDateTime=item.get("modifiedDateTime"),
                    mimeTypeIdentifierArrayText=item.get("mimeTypeIdentifierArrayText", []),
                )
            )
        return bulk_data

    @staticmethod
    def parse_response(json_data) -> ProductsRoot:
        bulk_data_product_bag = ResponseParser.parse_bulk_data_product_bag(json_data.get("bulkDataProductBag", []))
        count = json_data.get("count")
        return ProductsRoot(
            bulkDataProductBag=bulk_data_product_bag,
            count=count,
        )


endpoint = "/datasets/products/{productIdentifier}"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 1, 'bulkDataProductBag': [{'productIdentifier': 'PTFWPRE', 'productDescriptionText': 'Patent File Wrapper Entire Dataset', 'productTitleText': 'Patent File Wrapper Entire Dataset', 'productFrequencyText': 'WEEKLY', 'daysOfWeekText': 'SUNDAY', 'productLabelArrayText': ['PATENT'], 'productFromDate': '2001-01-01', 'productToDate': '2024-05-13', 'productTotalFileSize': 28866492413, 'productFileTotalQuantity': 3, 'modifiedDateTime': '2024-05-13 02:29:00', 'mimeTypeIdentifierArrayText': ['JSON'], 'productFileBag': {'count': 3, 'fileDataBag': [{'fileName': '2001-2010-patent-filewrapper-full-json.zip', 'fileSize': 9981249979, 'fileDataFromDate': '2001-01-01', 'fileDataToDate': '2010-12-31', 'fileTypeText': 'Data', 'fileDownloadURI': 'https://data.uspto.gov/files/PTFWPRE/2001-2010-patent-filewrapper-full-json.zip', 'fileReleaseDate': '2024-05-12 21:58:00', 'fileDate': '2024-12-02 07:18:00', 'fileLastModified': '2024-12-17 19:49:00'}, {'fileName': '2011-2020-patent-filewrapper-full-json.zip', 'fileSize': 15506284270, 'fileDataFromDate': '2011-01-01', 'fileDataToDate': '2020-12-31', 'fileTypeText': 'Data', 'fileDownloadURI': 'https://data.uspto.gov/files/PTFWPRE/2011-2020-patent-filewrapper-full-json.zip', 'fileReleaseDate': '2024-05-13 01:33:00', 'fileDate': '2024-12-02 07:18:00', 'fileLastModified': '2024-12-17 19:49:00'}, {'fileName': '2021-2024-patent-filewrapper-full-json.zip', 'fileSize': 3378958164, 'fileDataFromDate': '2021-01-01', 'fileDataToDate': '2024-05-07', 'fileTypeText': 'Data', 'fileDownloadURI': 'https://data.uspto.gov/files/PTFWPRE/2021-2024-patent-filewrapper-full-json.zip', 'fileReleaseDate': '2024-05-13 02:29:00', 'fileDate': '2024-12-02 07:18:00', 'fileLastModified': '2024-12-17 19:49:00'}]}}]}


# Example usage
import json
from dataclasses import asdict

