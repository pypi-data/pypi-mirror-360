import os
import re
from typing import Optional, Any, Dict, Union, List

from uspto_data.query.builder import QueryBuilder
from uspto_data.query.publication_content import USPublicationContent
from uspto_data.uspto_client import USPTOClient, get_default_client
from uspto_data.util.event_util import get_last_event, office_actions, parse_prosecution_history, get_events_by_code


class USPublication:
    def __init__(self, publication_number: str, api_key: str = None, uspto_client: Optional[Any] = None, auto_load: bool = False):
        """
        Initialize the USPublication object with a patent number and a USPTOClient instance.

        Args:
            publication_number (str): The unique patent number.
            uspto_client (Any): An instance of the USPTOClient for making API calls.
        """
        self.publication_number = publication_number.replace("/", "").replace(",", "").replace("US", "")
        pattern = r'[A-Z]\d{1,2}$'  # Kind code at the end of the string
        self.publication_number = re.sub(pattern, "", self.publication_number).strip()
        if len(self.publication_number) == 10:
            self.publication_number = self.publication_number[:4] + "0" + self.publication_number[-6:]
        self.url = pdf_url = f"https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/{self.publication_number}"
        self.uspto_client = uspto_client if uspto_client else (USPTOClient(api_key=api_key) if api_key else get_default_client())
        self.application_number = None
        self.content = None
        self.xml_content = None
        self.patent_info = None
        self.other_patent_info = None
        self.product_info = []
        auto_load and self.load()

    def load(self) -> Any:
        """
        Helper function to fetch patent data from USPTO API.

        :param publication_number: The unique patent number.
        :return: API response containing patent details.
        """
        if not self.publication_number:
            raise ValueError("Publication number not set.")
        query_builder = QueryBuilder()
        payload_data = query_builder.set_query(f'applicationMetaData.earliestPublicationNumber:*{self.publication_number}*').build()
        patent_search_result = self.uspto_client.call_api("patent/applications/search", payload_data=payload_data)
        if (bag := patent_search_result.patentFileWrapperDataBag) and len(bag) == 1:
            self.patent_info = patent_search_result.patentFileWrapperDataBag[0]
        elif bag and len(bag) > 1:
            self.patent_info = patent_search_result.patentFileWrapperDataBag.pop(0)
            self.other_patent_info = patent_search_result.patentFileWrapperDataBag
        if (bag := patent_search_result.patentFileWrapperDataBag) and len(bag) > 0 and patent_search_result.patentFileWrapperDataBag[0]:
            self.application_number = patent_search_result.patentFileWrapperDataBag[0].applicationNumberText

    def get_xml_name_and_path(self) -> Optional[Union[str, str]]:
        """
        Retrieve the XML file path for the patent's full text using USPTOClient and QueryBuilder.

        Returns:
            str: The XML file path if found, or None if not available.
        """
        # Assuming the response contains 'grantDocumentMetaData' with a field for 'fileLocationURI'
        if not self.patent_info:
            self.load()
        try:
            if (
                (bag := self.patent_info)
                and (meta := getattr(bag, "pgpubDocumentMetaData", None))
                and (uri := getattr(meta, "fileLocationURI"))
            ):
                full_xml_path = uri
                xml_file_name = getattr(meta, "xmlFileName", None)
                return full_xml_path, xml_file_name
        except (IndexError, KeyError):
            raise FileNotFoundError("No xml path found.")
        return None, None

    def save_full_text(self) -> Optional[str]:
        """
        Retrieve the full text of the patent by using the XML file path.

        Returns:
            str: The full text content of the patent if available, or None if not.
        """
        xml_file_path, xml_file_name = self.get_xml_name_and_path()
        if not xml_file_path:
            return None
        # Make a request to fetch the XML content using the file path
        save_path = f"/temp/{xml_file_name}"
        self.uspto_client.get_file(xml_file_path, save_path)
        return save_path

    def get_published_content(self) -> USPublicationContent | None:
        """
        Retrieve the full text of the patent by using the XML file path.

        Returns:
            str: The full text content of the patent if available, or None if not.
        """
        save_path = self.save_full_text()
        # Read and return the content of the XML file
        try:
            with open(save_path, "r", encoding="utf-8") as xml_file:
                xml_content = xml_file.read()
            self.xml_content = xml_content
            self.content = USPublicationContent(xml_content)
            return self.content
        except FileNotFoundError:
            return None

    def get_full_text(self) -> USPublicationContent | None:
        """
        Retrieve the full text of the patent by using the XML file path.

        Returns:
            str: The full text content of the patent if available, or None if not.
        """
        self.content or self.get_published_content()
        return self.content.get_full_text()

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed metadata about the patent using USPTOClient and QueryBuilder.

        Returns:
            Dict[str, Any]: Metadata details about the patent.
        """
        query_builder = QueryBuilder()
        query = query_builder.set_query(f'patentNumber:"{self.publication_number}"').build()
        response = self.uspto_client.search(query)
        # Extract metadata (customize as per the actual response structure)
        try:
            return response.get('results', [{}])[0]
        except (IndexError, KeyError):
            return None

    def get_product_info(self) -> Optional[List]:
        """
        Retrieve the XML file path for the patent's full text using USPTOClient and QueryBuilder.

        Returns:
            str: The XML file path if found, or None if not available.
        """
        # Assuming the response contains 'grantDocumentMetaData' with a field for 'fileLocationURI'
        if not self.patent_info:
            self.load()
        try:
            if (
                (bag := self.patent_info)
                and (meta := getattr(bag, "grantDocumentMetaData", None))
                and (product_id := getattr(meta, "productIdentifier"))
                and (zip_file_name := getattr(meta, "zipFileName"))
            ):
                self.product_info.append({
                    "productIdentifier": product_id,
                    "zipFileName": zip_file_name,
                    "productType": "patent"
                })
            if (
                (bag := self.patent_info)
                and (meta := getattr(bag, "pgpubDocumentMetaData", None))
                and (product_id := getattr(meta, "productIdentifier"))
                and (zip_file_name := getattr(meta, "zipFileName"))
            ):
                self.product_info.append({
                    "productIdentifier": product_id,
                    "zipFileName": zip_file_name,
                    "productType": "publication"
                })
        except (IndexError, KeyError):
            raise FileNotFoundError("No xml path found.")
        return self.product_info

    def filing_date(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.filingDate

    def name(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.firstInventorName

    def title(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.inventionTitle

    def patentNumber(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.patentNumber

    def grantDate(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.grantDate

    def docketNumber(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.docketNumber

    def get_last_event(self):
        return get_last_event(self.patent_info.eventDataBag)

    def get_events_by_code(self, event_code):
        return get_events_by_code(self.patent_info.eventDataBag, event_code)

    def office_actions(self):
        return office_actions(self.patent_info.eventDataBag)

    def parse_prosecution_history(self):
        return parse_prosecution_history(self.patent_info.eventDataBag)

    def pdf(self, save_dir: str = "/temp"):
        return USPublication.download_pdf(self.publication_number, save_dir=save_dir, uspto_client=self.uspto_client)

    @staticmethod
    def download_pdf(publication_number: str, save_dir: str = "/temp", uspto_client: USPTOClient = None, api_key: str = None) -> Optional[str]:
        """
        Download the official patent PDF from USPTO using the public publication endpoint.

        Args:
            save_dir (str): Directory to save the PDF.

        Returns:
            str: Path to the downloaded PDF file, or None if failed.
        """
        if not publication_number:
            raise ValueError("Patent number is not set.")
        if not uspto_client:
            if api_key:
                uspto_client = USPTOClient(api_key=api_key)
            else:
                raise ValueError("No USPTO Client or api key found.")
        pdf_url = f"https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/{publication_number}"
        save_path = os.path.join(save_dir, f"{publication_number}.pdf")
        try:
            headers = {
                "Accept": "application/pdf"
            }
            uspto_client.get_file(pdf_url, save_path, allow_redirects=True, headers=headers)
            return save_path
        except Exception as e:
            print(f"Failed to download PDF for patent {publication_number}: {e}")
            return None

    def __getstate__(self):
        state = self.__dict__.copy()
        state['uspto_client'] = None
        return state

    def __str__(self):
        return (
            f"USPublication("
            f"publication_number={self.publication_number}, "
            f"application_number={self.application_number}, "
            f"title={self.title()}, "
            f"filing_date={self.filing_date()}, "
            f"grant_date={self.grantDate()}, "
            f"docket_number={self.docketNumber()}, "
            f"first_inventor={self.name()}, "
            f"patent_info={self.patent_info}, "
            f"other_patent_info={self.other_patent_info}, "
            f"product_info={self.product_info}"
            ")"
        )


if __name__ == "__main__":
    # uspto_client = USPTOClient()  # Initialize your USPTO client
    patent = USPublication("20230083854", auto_load=True, api_key="rzgrnyaslendzamklfgvhfptgrveet")
    local_path = patent.pdf()
    print(f"Publication stored: {str(local_path)}")
    published_content = patent.get_published_content().get_abstract()
    print(f"patent.get_abstract: {published_content}")
    # # Get XML Path
    # xml_path, xml_name = patent.get_xml_name_and_path()
    # print(f"XML Name: {xml_name}\nPath: {xml_path}")
    #
    # # Get Full Text
    # full_text = patent.save_full_text()
    # print(f"Full Text: {full_text[:500]}")  # Print first 500 characters
    #
    # # Get Metadata
    # metadata = patent.get_metadata()
    # print(f"Metadata: {metadata}")
