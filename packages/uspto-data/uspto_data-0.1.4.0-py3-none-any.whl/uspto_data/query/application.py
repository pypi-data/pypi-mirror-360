from typing import Optional, Any, Dict, Union, List

from uspto_data.data_model import DocumentBag
from uspto_data.query.builder import QueryBuilder
from uspto_data.query.patent_content import USPatentContent
from uspto_data.query.publication import USPublication
from uspto_data.uspto_client import USPTOClient, get_default_client
from uspto_data.util.event_util import get_events_by_code, office_actions, parse_prosecution_history, get_last_event


class USApplication:
    def __init__(self, application_number: str, api_key: str = None, uspto_client: Optional[Any] = None, auto_load: bool = False,
                 auto_load_docs: bool = False):
        """
        Initialize the USApplication object with a patent number and a USPTOClient instance.

        Args:
            application_number (str): The unique patent number.
            uspto_client (Any): An instance of the USPTOClient for making API calls.
        """
        self.application_number = application_number.replace("/", "").replace(",", "")
        self.uspto_client = uspto_client if uspto_client else (USPTOClient(api_key=api_key) if api_key else get_default_client())
        self.docketNumber = None
        self.content = None
        self.patent_info = None
        self.other_patent_info = None
        self.prosecution_docs = []
        self.product_info = []
        auto_load and self.load()
        auto_load_docs and self.get_prosectuion_history()

    def load(self) -> Any:
        """
        Helper function to fetch patent data from USPTO API.

        :param application_number: The unique patent application number (US Serial No.).
        :return: API response containing patent details.
        """
        if not self.application_number:
            raise ValueError("Publication number not set.")
        patent_search_result = self.uspto_client.call_api("patent/applications/{applicationNumberText}", url_params={
            "applicationNumberText": self.application_number})
        if (bag := patent_search_result.patentFileWrapperDataBag) and len(bag) == 1:
            self.patent_info = patent_search_result.patentFileWrapperDataBag[0]
        elif bag and len(bag) > 1:
            self.patent_info = patent_search_result.patentFileWrapperDataBag.pop(0)
            self.other_patent_info = patent_search_result.patentFileWrapperDataBag
        if (bag := patent_search_result.patentFileWrapperDataBag) and len(bag) > 0 and patent_search_result.patentFileWrapperDataBag[0]:
            self.application_number = patent_search_result.patentFileWrapperDataBag[0].applicationNumberText
        meta = getattr(self.patent_info, "applicationMetaData", None)
        if meta and hasattr(meta, "docketNumber"):
            self.docket_number = meta.docketNumber

    def get_prosectuion_history(self):
        """
        Function to fetch prosecution (File Wrapper) documents data from USPTO API.

        :param application_number: The unique patent application number (US Serial No.).
        :return: API response containing patent details.
        """
        if self.prosecution_docs:
            return self.prosecution_docs
        if not self.application_number:
            raise ValueError("Publication number not set.")
        if not self.patent_info:
            self.load()
        document_search_result = self.uspto_client.call_api("patent/applications/{applicationNumberText}/documents", url_params={
            "applicationNumberText": self.application_number})
        self.prosecution_docs = document_search_result.documentBag
        return self.prosecution_docs

    def get_all_documents(self) -> List[DocumentBag]:
        """
        Retrieves all document metadata associated with the application.

        Returns:
            List[DocumentBag]: List of DocumentBag objects.
        """
        if not self.prosecution_docs:
            self.get_prosectuion_history()
        return self.prosecution_docs if self.prosecution_docs else []

    def get_first_document(self) -> Optional[DocumentBag]:
        """
        Retrieves the first document in the prosecution history.

        Returns:
            Optional[DocumentBag]: First document metadata or None if no documents exist.
        """
        docs = self.get_all_documents()
        return docs[0] if docs else None

    def get_document_by_doc_id(self, id: str) -> DocumentBag:
        """
        Retrieves documents that match the given document identifiers.

        Args:
            id (List[str]): List of document codes to filter by.

        Returns:
            List[DocumentBag]: List of document metadata matching the input codes.
        """
        docs = self.get_all_documents()
        for doc in docs:
            if doc.documentIdentifier == id:
                return doc
        return DocumentBag(
            documentIdentifier=id,
            downloadOptionBag=[]
        )

    def get_document_by_code(self, code: str) -> DocumentBag:
        """
        Retrieves documents that match the given document codes.

        Args:
            code (str): USPTO document code to filter by.

        Returns:
            DocumentBag: USPTO document metadata matching the input code.
        """
        docs = self.get_all_documents()
        for doc in docs:
            if doc.documentIdentifier == code:
                return doc
        return None

    def get_documents_by_code(self, codes: List[str]) -> List[DocumentBag]:
        """
        Retrieves documents that match the given document codes.

        Args:
            codes (List[str]): List of document codes to filter by.

        Returns:
            List[DocumentBag]: List of document metadata matching the input codes.
        """
        docs = self.get_all_documents()
        return [doc for doc in docs if doc.documentCode in codes]

    def get_document_name(self, document_id: str) -> Optional[str]:
        """
        Retrieves the name/description of a document given its identifier.

        Args:
            document_id (str): The document identifier.

        Returns:
            Optional[str]: The document name/description or None if not found.
        """
        docs = self.get_all_documents()
        for doc in docs:
            if doc.documentIdentifier == document_id:
                return doc.documentCodeDescriptionText
        return None

    def get_document_code(self, document_id: str) -> Optional[str]:
        """
        Retrieves the document code for a given document identifier.

        Args:
            document_id (str): The document identifier.

        Returns:
            Optional[str]: The document code or None if not found.
        """
        docs = self.get_all_documents()
        for doc in docs:
            if doc.documentIdentifier == document_id:
                return doc.documentCode
        return None

    def get_download_uri(self, document_id: str, mime_type: str = "PDF") -> Optional[str]:
        """
        Retrieves the download URI for a specific document based on MIME type.

        Args:
            document_id (str): The document identifier.
            mime_type (str): The MIME type of the document (e.g., 'PDF', 'XML').

        Returns:
            Optional[str]: The download URI or None if not found.
        """
        docs = self.prosecution_docs if self.prosecution_docs else self.get_all_documents()
        for doc in docs:
            if doc.documentIdentifier == document_id:
                for download_option in doc.downloadOptionBag:
                    if download_option.mimeTypeIdentifier == mime_type:
                        return download_option.downloadUrl if download_option.downloadUrl else download_option.downloadURI
        return None

    def download_document(self, document_id: str, mime_type: str = "PDF") -> Optional[str]:
        """
        Downloads a document and saves it locally, and returns the local save path.

        Args:
            document_id (str): The document identifier.
            mime_type (str): The MIME type of the document (e.g., 'PDF', 'XML').

        Returns:
            Optional[str]: The local file path if downloaded successfully, otherwise None.
        """
        download_uri = self.get_download_uri(document_id, mime_type)
        if not download_uri:
            return None

        file_path = f"/temp/{document_id}.{mime_type.lower()}"
        self.uspto_client.get_file(download_uri, file_path)
        return file_path

    def download_documents(self, documents: List[DocumentBag], mime_type: str = "PDF") -> List[str]:
        """
        Downloads multiple documents from a list of DocumentBag objects.

        Args:
            documents (List[DocumentBag]): List of DocumentBag objects containing download information.
            mime_type (str): The preferred MIME type for download (default: 'PDF').

        Returns:
            List[str]: List of file paths where documents are saved.
        """
        download_paths = []
        for document in documents:
            document_id = document.documentIdentifier
            file_path = self.download_document(document_id, mime_type)
            if file_path:
                download_paths.append(file_path)
        return download_paths

    def application_part_forms(self):
        """Access all application part forms (that are an 'Application in Part' category), except for documents forming the technical specification"""
        national_stage_codes = {"371P"}
        transmittal_codes = {"ADS", "LET.", "TR.PROV"}
        oath_codes = {"OATH"}
        statement_codes = {"R.55.78.STMT"}
        non_english_codes = {"SPECNO", "FR TRANS"}
        foreign_priority_codes = {"FRPR.IC", "FRPR.IC.TXT"}
        hague_codes = {"HAGUE.ANX", "REQ.HAGUE"}
        fee_codes = {"WFEE"}
        miscellaenous_codes = {"PC/I"}
        doc_codes = list(national_stage_codes | transmittal_codes | oath_codes
                                               | statement_codes
                                               | non_english_codes | foreign_priority_codes | hague_codes
                                               | fee_codes | miscellaenous_codes)
        affidavit_docs = self.affidavits()
        ids_docs = self.ids()
        ads_docs = self.ads()
        return self.get_documents_by_code(doc_codes) + affidavit_docs + ids_docs + ads_docs

    def application_data_sheets(self, include_transmittals=True):
        """Returns all Application Datasheets (ADS)."""
        codes = ["ADS"]
        include_transmittals and codes.append("TRNA")
        return self.get_documents_by_code(codes)

    def ads(self):
        """Returns all Application Datasheets (ADS)."""
        return self.application_data_sheets()

    def oaths_and_declarations(self):
        """Returns all Oath or Declaration documents."""
        return self.get_documents_by_code(["OATH"])

    def pre_exam_formalities(self):
        return self.get_documents_by_code(["PEFN"])

    def ids_documents(self):
        """Returns all Information Disclosure Statements (IDS)."""
        return self.get_documents_by_code(["IDS"])

    def ids(self):
        """Returns all Information Disclosure Statements (IDS)."""
        return self.ids_documents()

    def affidavits(self):
        disclaimer_codes = {"DIST", "STAT.DISCLMR"}
        affidavit_codes = {"AF/D.130A", "AF/D.130B", "AF/D.131", "AF/D.132", "AF/D.OTHER"}
        return self.get_documents_by_code(list(disclaimer_codes | affidavit_codes))

    def rce(self):
        """Returns RCE, CPA, and continuation filings."""
        return self.get_documents_by_code(["RCEX", "AMSB", "ACPA", "DCPA"])

    def pre_appeal(self):
        """Returns Pre-Appeal documents."""
        return self.get_documents_by_code(["AP.PRE.REQ", "AP.PRE.DEF", "AP.PRE.DEC"])

    def appeal(self):
        """Returns Appeal documents."""
        return self.get_documents_by_code(["AP.PRE.REQ", "AP.B", "AP/A", "AP/W", "APAF", "APCH", "APOH", "APPH", "APRB",
                                           "APWH", "BDRR", "PET.41.3", "WFEE.APPEAL", "N/AP", "SAPB"])

    def appeal_briefs(self):
        """Returns all appeal briefs filed during prosecution."""
        return self.get_documents_by_code(["AP.B", "APRB", "SAPB", "APEA", "APE2", "APBD", "APRB", "APNR"])

    def appeal_hearing_requests(self):
        """Returns requests related to appeal hearings."""
        return self.get_documents_by_code(["APOH", "APPD", "APPG", "APPH", "APCH", "APNH", "APHT", "APRH", "APRTH", "APRVH", "APWH"])

    def appeal_decisions(self):
        """Returns decisions and reconsideration requests from the BPAI."""
        return self.get_documents_by_code(["APOR", "APORSW", "APD1", "APD2", "APD3", "APDA", "APDN", "APDP", "APDR", "APDS", "APDS.NGR", "APDT", "APPR", "APSD"])

    def issue_info(self):
        """Returns Issue Fee Payment documents."""
        return self.get_documents_by_code(["IFEE", "ISSUE.NTF", "ISSUE.WD.NTC", "N416", "PETWDISS"])

    def issue_fee(self):
        """Returns Issue Fee Payment documents."""
        return self.get_documents_by_code(["IFEE"])

    def notice_of_allowance(self):
        """Returns Notice of Allowance documents."""
        return self.get_documents_by_code(["NOA", "C680"])

    def post_allowance_documents(self):
        """Returns post-allowance communications like disclaimers and corrections."""
        post_issuance_docs = self.post_issuance_docs()
        return post_issuance_docs + self.get_documents_by_code(["A.NA", "C680", "REQ.SML.ISS", "PETWDISS"])

    def post_issuance_docs(self):
        """Returns post-issuance communications, like requests for certificate of correction."""
        return self.get_documents_by_code(["C694", "COCIN"])

    def petitions(self):
        petition_codes = {"EXPD.LICENSE", "PET.41.3", "PET.AUTO", "PET.COLOR ", "PET.DEC.AUTO", "E.RECORD.COR", "PET.OP ", "PET.OP.AGE  ", "PET.PCT     ", "PET.POA.WDRW", "PET.PTA", "PET.SPRE", "PET.SPRE.ACX", "PET.STATUS", "PETWDISS", "PPH.PET.652 ", "RCONVP", "CERT.AC.HM.R", "PET.CSP", "PET.CS.JPO", "PET.CS.KIPO", "PET.HAGUE ", "PET.IMMUNO"}
        return self.get_documents_by_code(list(petition_codes))

    def pta_calculations(self):
        petition_codes = {"TERM.REQ", "TERM.REQ.ITM", "TERM.WAIVE", "TERM.WD", "PTA.IDS", "PET.PTA"}
        return self.get_documents_by_code(list(petition_codes))

    def certificates_of_correction(self):
        """Returns documents related to certificates of correction."""
        return self.get_documents_by_code(["COCIN", "COCOUT", "COCOUT.PLC", "COCOUT.SUPP", "COCX", "COCAIP"])

    def office_actions(self, include_advisory=True, include_notice_of_allowance=True, include_miscellaneous_actions=True):
        """Returns only Office Actions and optionally advisory actions."""
        office_action_codes = {"CTNF", "CTFR"}
        advisory_codes = {"CTAV", "SADV"} if include_advisory else set()
        ex_parte_quayle_codes = {"CTEQ"}
        notice_of_allowance_codes = {"NOA"} if include_advisory else set()
        miscellaneous_actions = {"CTMS"} if include_miscellaneous_actions else set()
        return self.get_documents_by_code(list(office_action_codes | advisory_codes |
                                               notice_of_allowance_codes | miscellaneous_actions))

    def restrictions(self):
        """Returns only restrictions or elections in the patent application."""
        office_action_codes = {"CTRS"}
        return self.get_documents_by_code(list(office_action_codes))

    def non_final_rejections(self):
        """Returns only Non-final Office Actions."""
        non_final_rejection_codes = {"CTNF"}
        return self.get_documents_by_code(list(non_final_rejection_codes))

    def final_rejections(self, include_advisory=True):
        """Returns only Final Office Actions and optionally advisory actions."""
        final_rejection_codes = {"CTFR"}
        advisory_codes = {"CTAV"} if include_advisory else set()
        return self.get_documents_by_code(list(final_rejection_codes | advisory_codes))

    def responses(self):
        """Returns responses to Office Actions."""
        remark_codes = {"REM"}
        after_final_codes = {"A.NE", "AMSB", "ANE.I"}
        after_non_final_codes = {"A..."}
        after_allowance_codes = {"A.NA"}
        quayle_response_codes = {"A.QU"}
        deficient_reply_codes = {"A.I", "A.LA"}
        supplemental_response = {"SA..", "SAFR"}
        pre_exam_response_codes = {"PEFR"}
        restriction_response_codes = {"ELC."}
        after_notice_of_appeal_codes = {"AP/A", "BD.A"}
        response_codes = remark_codes | after_final_codes | after_non_final_codes | after_allowance_codes
        response_codes |= quayle_response_codes | deficient_reply_codes | supplemental_response
        response_codes |= pre_exam_response_codes | restriction_response_codes
        return self.get_documents_by_code(list(response_codes))

    def restriction_responses(self):
        """Returns only responses to Resrtiction/election actions."""
        response_codes = {"ELC."}
        return self.get_documents_by_code(list(response_codes))

    def preliminary_amendments(self):
        """Returns only preliminary amendments."""
        prelim_amendment_codes = {"A.PE"}
        return self.get_documents_by_code(list(prelim_amendment_codes))

    def other_spec_docs(self):
        appendix_codes = {"APPENDIX"}
        specialty_spec_docs = {"APPENDIX", "COMPUTER", "SEQ.TXT", "SEQLIST", "TABLE"}
        return self.get_documents_by_code(list(appendix_codes | specialty_spec_docs))

    def specification_documents(self):
        """Returns claims, specifications, and drawings in one function."""
        return self.get_documents_by_code(["CLM", "SPEC", "SPECNO", "DRW", "DRW.NONBW"])

    def specifications(self):
        """Returns all specification-related documents."""
        return self.get_documents_by_code(["SPEC", "SPECNO"])

    def drawings(self):
        """Returns all drawings-related documents."""
        return self.get_documents_by_code(["DRW", "DRW.NONBW"])

    def claims(self):
        """Returns all claims-related documents."""
        return self.get_documents_by_code(["CLM", "CLM.NE", "CLM.CSP"])

    def submitted_evidence(self):
        """Returns IDS, foreign references, and third-party documents."""
        return self.get_documents_by_code(["IDS", "IDS.3P", "FOR", "NPL"])

    def examiner_amendments(self):
        """Returns examiner amendment documents."""
        return self.get_documents_by_code(["EX.A"])

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
                and (meta := getattr(bag, "grantDocumentMetaData", None))
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

    def get_patent(self) -> USPatentContent | None:
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
            self.content = USPatentContent(xml_content)
            return self.content
        except FileNotFoundError:
            return None

    def get_full_text(self) -> USPatentContent | None:
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
        query = query_builder.set_query(f'patentNumber:"{self.application_number}"').build()
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

    def publicationNumber(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.earliestPublicationNumber

    def grantDate(self):
        self.patent_info or self.load()
        return self.patent_info.applicationMetaData.grantDate

    def get_last_event(self):
        return get_last_event(self.patent_info.eventDataBag)

    def get_events_by_code(self, event_code):
        return get_events_by_code(self.patent_info.eventDataBag, event_code)

    def office_action_events(self):
        return office_actions(self.patent_info.eventDataBag)

    def parse_prosecution_history(self):
        return parse_prosecution_history(self.patent_info.eventDataBag)

    def __getstate__(self):
        state = self.__dict__.copy()
        state['uspto_client'] = None
        return state

    def __str__(self):
        return (
            f"USApplication("
            f"application_number={self.application_number}, "
            f"patent_number={self.patentNumber()}, "
            f"publication_number={self.publicationNumber()}, "
            f"title={self.title()}, "
            f"filing_date={self.filing_date()}, "
            f"grant_date={self.grantDate()}, "
            f"docket_number={self.docketNumber}, "
            f"first_inventor={self.name()}, "
            f"patent_info={self.patent_info}, "
            f"other_patent_info={self.other_patent_info}, "
            f"product_info={self.product_info}"
            ")"
        )


if __name__ == "__main__":
    # Initialize application instance
    us_application = USApplication("17122216", api_key="rzgrnyaslendzamklfgvhfptgrveet", auto_load_docs=True)

    # Office Actions
    office_actions = us_application.office_actions()
    first_doc = office_actions.pop()
    paths = us_application.download_documents(office_actions)
    print(f"Office Actions: {len(office_actions)}")

    # Appeal Briefs
    appeal_briefs = us_application.appeal_briefs()
    print(f"Appeal Briefs: {len(appeal_briefs)}")

    # Appeal Hearing Requests
    appeal_hearing_requests = us_application.appeal_hearing_requests()
    print(f"Appeal Hearing Requests: {len(appeal_hearing_requests)}")

    # Appeal Decisions
    appeal_decisions = us_application.appeal_decisions()
    print(f"Appeal Decisions: {len(appeal_decisions)}")

    # Issue Fee Payment
    issue_fee_payment = us_application.issue_fee()
    print(f"Issue Fee Payment: {len(issue_fee_payment)}")

    # Notice of Allowance
    notice_of_allowance = us_application.notice_of_allowance()
    print(f"Notice of Allowance: {len(notice_of_allowance)}")

    # Post Allowance Documents
    post_allowance_docs = us_application.post_allowance_documents()
    print(f"Post Allowance Documents: {len(post_allowance_docs)}")

    # Application Disclosure
    disclosure_docs = us_application.specification_documents()
    print(f"Application Disclosure Docs: {len(disclosure_docs)}")

    # Continued Prosecution Filings
    continuation_docs = us_application.continued_prosecution_filings()
    print(f"Continued Prosecution Filings: {len(continuation_docs)}")

    # Submitted Evidence
    evidence_docs = us_application.submitted_evidence()
    print(f"Submitted Evidence: {len(evidence_docs)}")

    # Oaths and Declarations
    oaths_docs = us_application.oaths_and_declarations()
    print(f"Oaths and Declarations: {len(oaths_docs)}")

    # uspto_client = USPTOClient()  # Initialize your USPTO client
    # patent = USApplication("17123456")
    # docs = patent.get_prosectuion_history()
    # filingDate = patent.filing_date()
    # published_content = USPublication(patent.publicationNumber()).get_published_content().get_abstract()
    # print(f"patent.get_abstract: {published_content}")
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
