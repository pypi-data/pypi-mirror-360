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

@dataclass
class BulkDataProductBag:
    productFileBag: ProductFileBag
    productIdentifier: Optional[str] = None
    productDescriptionText: Optional[str] = None
    productTitleText: Optional[str] = None
    productFrequencyText: Optional[str] = None
    daysOfWeekText: Optional[str] = None
    productLabelArrayText: Optional[List[str]] = field(default_factory=list)
    productDataSetArrayText: Optional[List[str]] = field(default_factory=list)
    productDataSetCategoryArrayText: Optional[List[str]] = field(default_factory=list)
    productFromDate: Optional[str] = None
    productToDate: Optional[str] = None
    productTotalFileSize: Optional[int] = None
    productFileTotalQuantity: Optional[int] = None
    modifiedDateTime: Optional[str] = None
    mimeTypeIdentifierArrayText: Optional[List[str]] = field(default_factory=list)

@dataclass
class ProductLabelBag:
    value: Optional[str] = None
    count: Optional[int] = None

@dataclass
class ProductDataSetBag:
    value: Optional[str] = None
    count: Optional[int] = None

@dataclass
class ProductCategoryBag:
    value: Optional[str] = None
    count: Optional[int] = None

@dataclass
class ProductMimeTypeBag:
    value: Optional[str] = None
    count: Optional[int] = None

@dataclass
class Facets:
    productLabelBag: List[ProductLabelBag] = field(default_factory=list)
    productDataSetBag: List[ProductDataSetBag] = field(default_factory=list)
    productCategoryBag: List[ProductCategoryBag] = field(default_factory=list)
    productMimeTypeBag: List[ProductMimeTypeBag] = field(default_factory=list)

@dataclass
class BulkSearchRoot:
    bulkDataProductBag: List[BulkDataProductBag] = field(default_factory=list)
    facets: Facets = field(default_factory=Facets)
    count: Optional[int] = None

class ResponseParser(response_interface.ResponseParser):
    @staticmethod
    def parse_file_data_bag(data) -> List[FileDataBag]:
        return [FileDataBag(**file_data) for file_data in data]

    @staticmethod
    def parse_product_file_bag(data) -> ProductFileBag:
        file_data_bag = data.get("fileDataBag", [])
        return ProductFileBag(fileDataBag=ResponseParser.parse_file_data_bag(file_data_bag))

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
                    productDataSetArrayText=item.get("productDataSetArrayText", []),
                    productDataSetCategoryArrayText=item.get("productDataSetCategoryArrayText", []),
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
    def parse_facets(data) -> Facets:
        return Facets(
            productLabelBag=[ProductLabelBag(**bag) for bag in data.get("productLabelBag", [])],
            productDataSetBag=[ProductDataSetBag(**bag) for bag in data.get("productDataSetBag", [])],
            productCategoryBag=[ProductCategoryBag(**bag) for bag in data.get("productCategoryBag", [])],
            productMimeTypeBag=[ProductMimeTypeBag(**bag) for bag in data.get("productMimeTypeBag", [])],
        )

    @staticmethod
    def parse_response(json_data) -> BulkSearchRoot:
        bulk_data_product_bag = ResponseParser.parse_bulk_data_product_bag(json_data.get("bulkDataProductBag", []))
        facets = ResponseParser.parse_facets(json_data.get("facets", {}))
        count = json_data.get("count")
        return BulkSearchRoot(
            bulkDataProductBag=bulk_data_product_bag,
            facets=facets,
            count=count,
        )

endpoint = "/datasets/products/search"

#  EXAMPLE JSON RESPONSE

example_json = {'count': 3, 'bulkDataProductBag': [{'productIdentifier': 'PTFWPRE', 'productDescriptionText': 'Patent File Wrapper Entire Dataset', 'productTitleText': 'Patent File Wrapper Entire Dataset', 'productFrequencyText': 'WEEKLY', 'daysOfWeekText': 'SUNDAY', 'productLabelArrayText': ['PATENT', 'RESEARCH'], 'productDataSetArrayText': ['Research'], 'productDataSetCategoryArrayText': ['Patent applications'], 'productFromDate': '2021-01-01', 'productToDate': '2030-12-31', 'productTotalFileSize': 10430070, 'productFileTotalQuantity': 1, 'modifiedDateTime': '2024-04-16 18:39:00', 'mimeTypeIdentifierArrayText': ['json'], 'productFileBag': {'fileDataBag': [{'fileName': '2021-2023-pairbulk-full-20240114-json.zip', 'fileSize': 10430070, 'fileDataFromDate': '2021-01-01', 'fileDataToDate': '2030-12-31', 'fileTypeText': 'Data', 'fileDownloadURI': 'https://data.uspto.gov/files/PTFWPRE/pairbulk-delta-20240129-json.zip', 'fileReleaseDate': '2021-01-01', 'fileDate': '2024-11-24', 'fileLastModified': '2024-12-17 19:49:00'}]}}, {'productIdentifier': 'PTFWPRD', 'productDescriptionText': 'Patent File Wrapper Delta Dataset', 'productTitleText': 'Patent File Wrapper Delta Dataset', 'productFrequencyText': 'DAILY', 'productFromDate': '2023-04-15', 'productToDate': '2024-04-17', 'productTotalFileSize': 32156499361, 'productFileTotalQuantity': 3, 'modifiedDateTime': '2024-04-16 19:42:00', 'mimeTypeIdentifierArrayText': [], 'productFileBag': {'fileDataBag': [{'fileName': 'e-OG20230910_1514-3.zip', 'fileSize': 10430090, 'fileDataFromDate': '2023-04-15', 'fileDataToDate': '2023-04-16', 'fileTypeText': 'Data', 'fileDownloadURI': 'https://data.uspto.gov/files/PTFWPRD/e-OG20230910_1514-3.zip', 'fileReleaseDate': '2023-04-15', 'fileLastModified': '2024-12-17 19:49:00'}, {'fileName': 'e-OG20230910_1514-3.zip', 'fileSize': 10430010, 'fileDataFromDate': '2023-04-15', 'fileDataToDate': '2023-04-16', 'fileTypeText': 'Data', 'fileDownloadURI': 'https://data.uspto.gov/files/PTFWPRD/e-OG20240417_1514-3.zip', 'fileReleaseDate': '2023-04-15', 'fileLastModified': '2024-12-17 19:49:00'}, {'fileName': 'pairbulk-delta-20240417.json.gz', 'fileSize': 2060438119, 'fileDataFromDate': '2024-04-17', 'fileDataToDate': '2024-04-17', 'fileTypeText': 'Data', 'fileDownloadURI': 'https://data.uspto.govs3://odp-dev-dh-web/bulk-data/files/PTFWPRD/pairbulk-delta-20240417.json.gz', 'fileReleaseDate': '2024-04-17', 'fileLastModified': '2024-12-17 19:49:00'}]}}, {'productIdentifier': 'PTNT', 'productDescriptionText': 'Patent File Another Entire Dataset', 'productTitleText': 'Patent File Another Entire Dataset', 'productFrequencyText': 'DAILY', 'productLabelArrayText': [], 'productTotalFileSize': 32156499361, 'productFileTotalQuantity': 3, 'modifiedDateTime': '2024-04-17 13:55:00', 'mimeTypeIdentifierArrayText': ['xml']}], 'facets': {'productLabelBag': [{'value': 'PATENT', 'count': 1}, {'value': 'RESEARCH', 'count': 1}], 'productDataSetBag': [{'value': 'Research', 'count': 1}], 'productCategoryBag': [{'value': 'Patent applications', 'count': 1}], 'productMimeTypeBag': [{'value': 'PDF', 'count': 1}, {'value': 'XML', 'count': 4}]}}


# if __name__ == "__main__":
#     parsed_response = ResponseParser.parse_response(example_json)
#     print(json.dumps(asdict(parsed_response), indent=2))
