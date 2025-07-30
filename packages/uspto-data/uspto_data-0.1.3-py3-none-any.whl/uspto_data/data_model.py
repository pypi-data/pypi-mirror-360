from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CorrespondenceAddressBag:
    correspondentNameText: Optional[str] = None
    cityName: Optional[str] = None
    geographicRegionName: Optional[str] = None
    geographicRegionCode: Optional[str] = None
    countryCode: Optional[str] = None
    postalCode: Optional[str] = None
    postalAddressCategory: Optional[str] = None
    nameLineOneText: Optional[str] = None
    nameLineTwoText: Optional[str] = None
    countryName: Optional[str] = None
    addressLineOneText: Optional[str] = None
    addressLineTwoText: Optional[str] = None
    addressLineThreeText: Optional[str] = None
    addressLineFourText: Optional[str] = None


@dataclass
class AssignorBag:
    assignorName: Optional[str] = None
    executionDate: Optional[str] = None


@dataclass
class AssigneeAddress:
    addressLineOneText: Optional[str] = None
    addressLineTwoText: Optional[str] = None
    cityName: Optional[str] = None
    geographicRegionName: Optional[str] = None
    geographicRegionCode: Optional[str] = None
    countryName: Optional[str] = None
    postalCode: Optional[str] = None


@dataclass
class AssigneeBag:
    assigneeAddress: AssigneeAddress
    assigneeNameText: Optional[str] = None


@dataclass
class AssignmentBag:
    assignorBag: List[AssignorBag]
    assigneeBag: List[AssigneeBag]
    correspondenceAddressBag: List[CorrespondenceAddressBag]
    reelNumber_frameNumber: Optional[str] = field(metadata={'alias': 'reelNumber/frameNumber'})
    reelNumber: Optional[str] = None
    frameNumber: Optional[str] = None
    pageNumber: Optional[int] = None
    assignmentReceivedDate: Optional[str] = None
    assignmentRecordedDate: Optional[str] = None
    assignmentMailedDate: Optional[str] = None
    conveyanceText: Optional[str] = None


@dataclass
class PatentTermAdjustmentHistoryDataBag:
    eventDescriptionText: Optional[str] = None
    eventSequenceNumber: Optional[float] = None
    originatingEventSequenceNumber: Optional[float] = None
    ptaPteCode: Optional[str] = None
    eventDate: Optional[str] = None


@dataclass
class InventorBag:
    correspondenceAddressBag: List[CorrespondenceAddressBag]
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    namePrefix: Optional[str] = None
    nameSuffix: Optional[str] = None
    preferredName: Optional[str] = None
    countryCode: Optional[str] = None
    inventorNameText: Optional[str] = None


@dataclass
class ApplicantBag:
    correspondenceAddressBag: List[CorrespondenceAddressBag]
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    preferredName: Optional[str] = None
    namePrefix: Optional[str] = None
    nameSuffix: Optional[str] = None
    countryCode: Optional[str] = None
    applicantNameText: Optional[str] = None
    applicant: Optional[str] = None


@dataclass
class ForeignPriorityBag:
    filingDate: Optional[str] = None
    applicationNumberText: Optional[str] = None
    ipOfficeName: Optional[str] = None


@dataclass
class PgPubDocumentMetaData:
    productIdentifier: Optional[str] = None
    zipFileName: Optional[str] = None
    fileCreateDateTime: Optional[str] = None
    xmlFileName: Optional[str] = None
    fileLocationURI: Optional[str] = None


@dataclass
class GrantDocumentMetaData:
    productIdentifier: Optional[str] = None
    zipFileName: Optional[str] = None
    fileCreateDateTime: Optional[str] = None
    xmlFileName: Optional[str] = None
    fileLocationURI: Optional[str] = None


@dataclass
class PowerOfAttorneyAddressBag:
    nameLineOneText: Optional[str] = None
    addressLineOneText: Optional[str] = None
    addressLineTwoText: Optional[str] = None
    geographicRegionName: Optional[str] = None
    geographicRegionCode: Optional[str] = None
    postalCode: Optional[str] = None
    cityName: Optional[str] = None
    countryCode: Optional[str] = None
    countryName: Optional[str] = None


@dataclass
class TelecommunicationAddressBag:
    telecommunicationNumber: Optional[str] = None
    extensionNumber: Optional[str] = None
    usageTypeCategory: Optional[str] = None
    telecomTypeCode: Optional[str] = None


@dataclass
class CustomerNumber:
    patronIdentifier: Optional[str] = None
    organizationStandardName: Optional[str] = None
    powerOfAttorneyAddressBag: List[PowerOfAttorneyAddressBag] = field(default_factory=list)
    telecommunicationAddressBag: List[TelecommunicationAddressBag] = field(default_factory=list)


@dataclass
class AttorneyAddressBag:
    nameLineOneText: Optional[str] = None
    nameLineTwoText: Optional[str] = None
    addressLineOneText: Optional[str] = None
    addressLineTwoText: Optional[str] = None
    geographicRegionName: Optional[str] = None
    geographicRegionCode: Optional[str] = None
    postalCode: Optional[str] = None
    cityName: Optional[str] = None
    countryCode: Optional[str] = None
    countryName: Optional[str] = None


@dataclass
class AttorneyBag:
    attorneyAddressBag: List[AttorneyAddressBag]
    telecommunicationAddressBag: List[TelecommunicationAddressBag]
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    namePrefix: Optional[str] = None
    nameSuffix: Optional[str] = None
    registrationNumber: Optional[str] = None
    activeIndicator: Optional[str] = None
    registeredPractitionerCategory: Optional[str] = None


@dataclass
class EntityStatusData:
    smallEntityStatusIndicator: Optional[bool] = None
    businessEntityStatusCategory: Optional[str] = None


@dataclass
class ApplicationMetaData:
    nationalStageIndicator: Optional[bool] = None
    entityStatusData: EntityStatusData = None
    publicationDateBag: List[str] = field(default_factory=list)
    publicationSequenceNumberBag: List[str] = field(default_factory=list)
    publicationCategoryBag: List[str] = field(default_factory=list)
    docketNumber: Optional[str] = None
    firstInventorToFileIndicator: Optional[str] = None
    firstApplicantName: Optional[str] = None
    firstInventorName: Optional[str] = None
    applicationConfirmationNumber: Optional[int] = None
    applicationStatusDate: Optional[str] = None
    applicationStatusDescriptionText: Optional[str] = None
    filingDate: Optional[str] = None
    effectiveFilingDate: Optional[str] = None
    grantDate: Optional[str] = None
    groupArtUnitNumber: Optional[str] = None
    applicationTypeCode: Optional[str] = None
    applicationTypeLabelName: Optional[str] = None
    applicationTypeCategory: Optional[str] = None
    inventionTitle: Optional[str] = None
    patentNumber: Optional[str] = None
    applicationStatusCode: Optional[int] = None
    earliestPublicationNumber: Optional[str] = None
    earliestPublicationDate: Optional[str] = None
    pctPublicationNumber: Optional[str] = None
    pctPublicationDate: Optional[str] = None
    internationalRegistrationPublicationDate: Optional[str] = None
    internationalRegistrationNumber: Optional[str] = None
    examinerNameText: Optional[str] = None
    class_: Optional[str] = None
    subclass: Optional[str] = None
    class_subclass: Optional[str] = None
    customerNumber: Optional[int] = None
    cpcClassificationBag: List[str] = field(default_factory=list)
    applicantBag: List[ApplicantBag] = field(default_factory=list)
    inventorBag: List[InventorBag] = field(default_factory=list)

@dataclass
class AppMetaPatentFileWrapperDataBag:
    applicationMetaData: ApplicationMetaData
    applicationNumberText: Optional[str] = None


@dataclass
class AppMetaDataRoot:
    patentFileWrapperDataBag: List[AppMetaPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class AssignmentCorrespondenceAddressBag:
    correspondentNameText: Optional[str] = None
    addressLineOneText: Optional[str] = None
    addressLineTwoText: Optional[str] = None
    addressLineThreeText: Optional[str] = None
    addressLineFourText: Optional[str] = None


@dataclass
class AssignmentsPatentFileWrapperDataBag:
    assignmentBag: AssignmentBag


@dataclass
class AssignmentsRoot:
    patentFileWrapperDataBag: List[AssignmentsPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class AssociatedDocsPatentFileWrapperDataBag:
    pgpubDocumentMetaData: PgPubDocumentMetaData
    grantDocumentMetaData: GrantDocumentMetaData
    applicationNumberText: Optional[str] = None


@dataclass
class AssociatedDocsRoot:
    patentFileWrapperDataBag: List[AssociatedDocsPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class PowerOfAttorneyBag:
    attorneyAddressBag: List[AttorneyAddressBag]
    telecommunicationAddressBag: List[TelecommunicationAddressBag]
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    namePrefix: Optional[str] = None
    nameSuffix: Optional[str] = None
    preferredName: Optional[str] = None
    countryCode: Optional[str] = None
    registrationNumber: Optional[str] = None
    activeIndicator: Optional[str] = None
    registeredPractitionerCategory: Optional[str] = None


@dataclass
class RecordAttorney:
    powerOfAttorneyBag: List[PowerOfAttorneyBag]
    customerNumber: List[CustomerNumber] = field(default_factory=list)
    attorneyBag: List[AttorneyBag] = field(default_factory=list)


@dataclass
class AttorneyRecordAttorney:
    powerOfAttorneyBag: List[PowerOfAttorneyBag]
    customerNumber: List[CustomerNumber] = field(default_factory=list)
    attorneyBag: List[AttorneyBag] = field(default_factory=list)


@dataclass
class AttorneyPatentFileWrapperDataBag:
    recordAttorney: AttorneyRecordAttorney
    applicationNumberText: Optional[str] = None


@dataclass
class AttorneyRoot:
    patentFileWrapperDataBag: List[AttorneyPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class ParentContinuityBag:
    firstInventorToFileIndicator: Optional[bool] = None
    parentApplicationStatusCode: Optional[int] = None
    parentPatentNumber: Optional[str] = None
    parentApplicationStatusDescriptionText: Optional[str] = None
    parentApplicationFilingDate: Optional[str] = None
    parentApplicationNumberText: Optional[str] = None
    childApplicationNumberText: Optional[str] = None
    claimParentageTypeCode: Optional[str] = None
    claimParentageTypeCodeDescription: Optional[str] = None


@dataclass
class ChildContinuityBag:
    childApplicationStatusCode: Optional[int] = None
    parentApplicationNumberText: Optional[str] = None
    childApplicationNumberText: Optional[str] = None
    childApplicationStatusDescriptionText: Optional[str] = None
    childApplicationFilingDate: Optional[str] = None
    firstInventorToFileIndicator: Optional[bool] = None
    childPatentNumber: Optional[str] = None
    claimParentageTypeCode: Optional[str] = None
    claimParentageTypeCodeDescription: Optional[str] = None


@dataclass
class ContinuityPatentFileWrapperDataBag:
    parentContinuityBag: List[ParentContinuityBag]
    childContinuityBag: List[ChildContinuityBag]
    applicationNumberText: Optional[str] = None


@dataclass
class ContinuityRoot:
    patentFileWrapperDataBag: List[ContinuityPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class DownloadOptionBag:
    mimeTypeIdentifier: Optional[str] = None
    downloadURI: Optional[str] = None
    downloadUrl: Optional[str] = None
    pageTotalQuantity: Optional[int] = None


@dataclass
class DocumentBag:
    downloadOptionBag: List[DownloadOptionBag]
    applicationNumberText: Optional[str] = None
    officialDate: Optional[str] = None
    documentIdentifier: Optional[str] = None
    documentCode: Optional[str] = None
    documentCodeDescriptionText: Optional[str] = None
    documentDirectionCategory: Optional[str] = None

    @classmethod
    def from_flat_dict(cls, data: dict) -> 'DocumentBag':
        option = DownloadOptionBag(
            downloadUrl=data.get("pdfUrl"),
            downloadURI=data.get("pdfUrl"),  # or another field if different
            mimeTypeIdentifier="application/pdf",  # or infer/detect if needed
            pageTotalQuantity=None  # populate if data has it
        )

        return cls(
            downloadOptionBag=[option],
            officialDate=data.get("date"),
            documentIdentifier=data.get("docId"),
            documentCodeDescriptionText=data.get("description")
        )

@dataclass
class DocumentsRoot:
    documentBag: List[DocumentBag]


@dataclass
class ForeignPriorityPatentFileWrapperDataBag:
    foreignPriorityBag: List[ForeignPriorityBag]
    applicationNumberText: Optional[str] = None


@dataclass
class ForeignPriorityRoot:
    patentFileWrapperDataBag: List[ForeignPriorityPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class PatentTermAdjustmentHistoryDataBag:
    eventDate: Optional[str] = None
    applicantDayDelayQuantity: Optional[int] = None
    eventDescriptionText: Optional[str] = None
    eventSequenceNumber: Optional[int] = None
    ipOfficeDayDelayQuantity: Optional[int] = None
    originatingEventSequenceNumber: Optional[int] = None
    ptaPteCode: Optional[str] = None


@dataclass
class PatentTermAdjustmentData:
    patentTermAdjustmentHistoryDataBag: List[PatentTermAdjustmentHistoryDataBag]
    aDelayQuantity: Optional[int] = None
    adjustmentTotalQuantity: Optional[int] = None
    applicantDayDelayQuantity: Optional[int] = None
    bDelayQuantity: Optional[int] = None
    cDelayQuantity: Optional[int] = None
    filingDate: Optional[str] = None
    grantDate: Optional[str] = None
    nonOverlappingDayQuantity: Optional[int] = None
    overlappingDayQuantity: Optional[int] = None
    ipOfficeDayDelayQuantity: Optional[int] = None


@dataclass
class PatentTermAdjustmentPatentFileWrapperDataBag:
    patentTermAdjustmentData: PatentTermAdjustmentData
    applicationNumberText: Optional[str] = None


@dataclass
class PatentTermAdjustmentRoot:
    patentFileWrapperDataBag: List[PatentTermAdjustmentPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class ApplicationStatusCode:
    value: Optional[str] = None
    count: Optional[int] = None


@dataclass
class Facets:
    applicationStatusCode: List[ApplicationStatusCode]


@dataclass
class StatusCodeBag:
    applicationStatusCode: Optional[int] = None
    applicationStatusDescriptionText: Optional[str] = None


@dataclass
class StatusCodesRoot:
    statusCodeBag: List[StatusCodeBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class EventDataBag:
    eventCode: Optional[str] = None
    eventDescriptionText: Optional[str] = None
    eventDate: Optional[str] = None


@dataclass
class TransactionsPatentFileWrapperDataBag:
    eventDataBag: List[EventDataBag]
    applicationNumberText: Optional[str] = None


@dataclass
class TransactionsRoot:
    patentFileWrapperDataBag: List[TransactionsPatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class PatentFileWrapperDataBag:
    applicationNumberText: Optional[str] = None
    applicationMetaData: ApplicationMetaData = None
    correspondenceAddressBag: List[CorrespondenceAddressBag] = field(default_factory=list)
    assignmentBag: List[AssignmentBag] = field(default_factory=list)
    recordAttorney: RecordAttorney = None
    foreignPriorityBag: List[ForeignPriorityBag] = field(default_factory=list)
    parentContinuityBag: List[ParentContinuityBag] = field(default_factory=list)
    childContinuityBag: List[ChildContinuityBag] = field(default_factory=list)
    patentTermAdjustmentData: PatentTermAdjustmentData = None
    eventDataBag: List[EventDataBag] = field(default_factory=list)
    pgpubDocumentMetaData: PgPubDocumentMetaData = None
    grantDocumentMetaData: GrantDocumentMetaData = None
    lastIngestionTime: Optional[str] = None


@dataclass
class AppDataRoot:
    patentFileWrapperDataBag: List[PatentFileWrapperDataBag]
    count: Optional[int] = None
    requestIdentifier: Optional[str] = None


@dataclass
class SearchRoot:
    patentFileWrapperDataBag: List[PatentFileWrapperDataBag]
    facets: List[Facets]
    count: Optional[int] = None
