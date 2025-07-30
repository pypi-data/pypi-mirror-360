from typing import Dict, Any

from uspto_data.data_model import EntityStatusData, CorrespondenceAddressBag, ApplicantBag, EventDataBag, InventorBag, \
    GrantDocumentMetaData, PgPubDocumentMetaData, ApplicationMetaData, PatentFileWrapperDataBag, AppDataRoot
from uspto_data.response.patent_file_wrapper.pta import ResponseParser as AdjustmentResponseParser
from uspto_data.response.patent_file_wrapper.assignments import ResponseParser as AssignmentsResponseParser
from uspto_data.response.patent_file_wrapper.attorney import ResponseParser as AttorneyResponseParser
from uspto_data.response.patent_file_wrapper.foreign_priority import ResponseParser as ForeignPriorityResponseParser
from uspto_data.response.patent_file_wrapper.continuity import ResponseParser as ContinuityResponseParser
from uspto_data.response.patent_file_wrapper.ref.application import example_json_2

# Parsing Helper Functions
class ResponseParser:
    @staticmethod
    def parse_entity_status_data(data: Dict[str, Any]) -> EntityStatusData:
        return EntityStatusData(
            smallEntityStatusIndicator=data.get("smallEntityStatusIndicator"),
            businessEntityStatusCategory=data.get("businessEntityStatusCategory"),
        )


    @staticmethod
    def parse_correspondence_address_bag(data: Dict[str, Any]) -> CorrespondenceAddressBag:
        return CorrespondenceAddressBag(
            nameLineOneText=data.get("nameLineOneText"),
            nameLineTwoText=data.get("nameLineTwoText"),
            addressLineOneText=data.get("addressLineOneText"),
            addressLineTwoText=data.get("addressLineTwoText"),
            geographicRegionName=data.get("geographicRegionName"),
            geographicRegionCode=data.get("geographicRegionCode"),
            postalCode=data.get("postalCode"),
            cityName=data.get("cityName"),
            countryCode=data.get("countryCode"),
            countryName=data.get("countryName"),
            postalAddressCategory=data.get("postalAddressCategory"),
        )


    @staticmethod
    def parse_applicant_bag(data: Dict[str, Any]) -> ApplicantBag:
        correspondence_addresses = [
            ResponseParser.parse_correspondence_address_bag(addr)
            for addr in data.get("correspondenceAddressBag", [])
        ]
        return ApplicantBag(
            applicantNameText=data.get("applicantNameText"),
            firstName=data.get("firstName"),
            middleName=data.get("middleName"),
            lastName=data.get("lastName"),
            preferredName=data.get("preferredName"),
            namePrefix=data.get("namePrefix"),
            nameSuffix=data.get("nameSuffix"),
            countryCode=data.get("countryCode"),
            correspondenceAddressBag=correspondence_addresses,
        )

    @staticmethod
    def parse_event_data_bag(data: Dict[str, Any]) -> EventDataBag:
        return EventDataBag(
            eventCode=data.get("eventCode"),
            eventDescriptionText=data.get("eventDescriptionText"),
            eventDate=data.get("eventDate"),
        )

    @staticmethod
    def parse_inventor_bag(data: Dict[str, Any]) -> InventorBag:
        correspondence_addresses = [
            ResponseParser.parse_correspondence_address_bag(addr)
            for addr in data.get("correspondenceAddressBag", [])
        ]
        return InventorBag(
            firstName=data.get("firstName"),
            middleName=data.get("middleName"),
            lastName=data.get("lastName"),
            namePrefix=data.get("namePrefix"),
            nameSuffix=data.get("nameSuffix"),
            preferredName=data.get("preferredName"),
            countryCode=data.get("countryCode"),
            inventorNameText=data.get("inventorNameText"),
            correspondenceAddressBag=correspondence_addresses,
        )

    @staticmethod
    def parse_grant_document_bag(data) -> GrantDocumentMetaData:
        return GrantDocumentMetaData(
            productIdentifier=data.get("productIdentifier"),
            zipFileName=data.get("zipFileName"),
            fileCreateDateTime=data.get("fileCreateDateTime"),
            xmlFileName=data.get("xmlFileName"),
            fileLocationURI=data.get("fileLocationURI")
        )

    @staticmethod
    def parse_pgpub_document_metadata(data) -> PgPubDocumentMetaData:
        return PgPubDocumentMetaData(
            productIdentifier=data.get("productIdentifier"),
            zipFileName=data.get("zipFileName"),
            fileCreateDateTime=data.get("fileCreateDateTime"),
            xmlFileName=data.get("xmlFileName"),
            fileLocationURI=data.get("fileLocationURI")
        )

    @staticmethod
    def parse_application_meta_data(data):
        return ApplicationMetaData(
            nationalStageIndicator=data.get("nationalStageIndicator"),
            entityStatusData=ResponseParser.parse_entity_status_data(data.get("entityStatusData", {})),
            publicationDateBag=data.get("publicationDateBag", []),
            publicationSequenceNumberBag=data.get("publicationSequenceNumberBag", []),
            publicationCategoryBag=data.get("publicationCategoryBag", []),
            docketNumber=data.get("docketNumber"),
            firstInventorToFileIndicator=data.get("firstInventorToFileIndicator"),
            firstApplicantName=data.get("firstApplicantName"),
            firstInventorName=data.get("firstInventorName"),
            applicationConfirmationNumber=data.get("applicationConfirmationNumber"),
            applicationStatusDate=data.get("applicationStatusDate"),
            applicationStatusDescriptionText=data.get("applicationStatusDescriptionText"),
            filingDate=data.get("filingDate"),
            effectiveFilingDate=data.get("effectiveFilingDate"),
            grantDate=data.get("grantDate"),
            groupArtUnitNumber=data.get("groupArtUnitNumber"),
            applicationTypeCode=data.get("applicationTypeCode"),
            applicationTypeLabelName=data.get("applicationTypeLabelName"),
            applicationTypeCategory=data.get("applicationTypeCategory"),
            inventionTitle=data.get("inventionTitle"),
            patentNumber=data.get("patentNumber"),
            applicationStatusCode=data.get("applicationStatusCode"),
            earliestPublicationNumber=data.get("earliestPublicationNumber"),
            earliestPublicationDate=data.get("earliestPublicationDate"),
            pctPublicationNumber=data.get("pctPublicationNumber"),
            pctPublicationDate=data.get("pctPublicationDate"),
            internationalRegistrationPublicationDate=data.get("internationalRegistrationPublicationDate"),
            internationalRegistrationNumber=data.get("internationalRegistrationNumber"),
            examinerNameText=data.get("examinerNameText"),
            class_=data.get("class"),
            subclass=data.get("subclass"),
            class_subclass=data.get("class/subclass"),
            customerNumber=data.get("customerNumber"),
            cpcClassificationBag=data.get("cpcClassificationBag", []),
            applicantBag=[
                ResponseParser.parse_applicant_bag(inventor)
                for inventor in data.get("applicantBag", [])
            ],
            inventorBag=[
                ResponseParser.parse_inventor_bag(inventor)
                for inventor in data.get("inventorBag", [])
            ],
        )

    @staticmethod
    def parse_patent_file_wrapper_data_bag(data: Dict[str, Any]) -> PatentFileWrapperDataBag:
        return PatentFileWrapperDataBag(
            applicationNumberText=data.get("applicationNumberText"),
            applicationMetaData=ResponseParser.parse_application_meta_data(data.get("applicationMetaData", {})),
            correspondenceAddressBag=[
                ResponseParser.parse_correspondence_address_bag(correspondence_address)
                for correspondence_address in data.get("correspondenceAddressBag", [])
            ],
            assignmentBag=[
                AssignmentsResponseParser.parse_assignment_bag(assignment)
                for assignment in data.get("assignmentBag", [])
            ],
            recordAttorney=AttorneyResponseParser.parse_record_attorney(data.get("recordAttorney", {})),
            foreignPriorityBag=[
                ForeignPriorityResponseParser.parse_foreign_priority_bag(foreign_priority_item)
                for foreign_priority_item in data.get("foreignPriorityBag", [])
            ],
            parentContinuityBag=[
                ContinuityResponseParser.parse_parent_continuity_bag(parent)
                for parent in data.get("parentContinuityBag", {})
            ],
            childContinuityBag=[
                ContinuityResponseParser.parse_child_continuity_bag(child)
                for child in data.get("childContinuityBag", {})
            ],
            patentTermAdjustmentData=AdjustmentResponseParser.parse_patent_term_adjustment_data(data.get("patentTermAdjustmentData", {})),
            eventDataBag=[
                ResponseParser.parse_event_data_bag(event)
                for event in data.get("eventDataBag", [])
            ],
            pgpubDocumentMetaData=ResponseParser.parse_pgpub_document_metadata(data.get("pgpubDocumentMetaData", {})),
            grantDocumentMetaData=ResponseParser.parse_grant_document_bag(data.get("grantDocumentMetaData", {})),
            lastIngestionTime=data.get("lastIngestionTime", None),
        )

    @staticmethod
    def parse_root(data: Dict[str, Any]) -> AppDataRoot:
        return AppDataRoot(
            count=data.get("count"),
            patentFileWrapperDataBag=[
                ResponseParser.parse_patent_file_wrapper_data_bag(wrapper)
                for wrapper in data.get("patentFileWrapperDataBag", [])
            ],
        )

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> AppDataRoot:
        return ResponseParser.parse_root(response)


# Example of usage:
if __name__ == "__main__":
    # Replace this with actual data loading if necessary
    parsed_data = ResponseParser.parse_root(example_json_2)
    print(parsed_data)
