from uspto_data.response.patent_file_wrapper import search, application, application_metadata, assignments, pta, \
    continuity, transactions, documents, foreign_priority, associated_documents, status_codes
from uspto_data.response.patent_file_wrapper import attorney

urls = [
    ("patent/applications/search", ["GET", "POST"], search.ResponseParser),
    ("patent/applications/{applicationNumberText}", ["GET"], application.ResponseParser),
    ("patent/applications/{applicationNumberText}/meta-data", ["GET"], application_metadata.ResponseParser),
    ("patent/applications/{applicationNumberText}/continuity", ["GET"], continuity.ResponseParser),
    ("patent/applications/{applicationNumberText}/documents", ["GET"], documents.ResponseParser),
    ("patent/applications/{applicationNumberText}/transactions", ["GET"], transactions.ResponseParser),
    ("patent/applications/{applicationNumberText}/adjustment", ["GET"], pta.ResponseParser),
    ("patent/applications/{applicationNumberText}/attorney", ["GET"], attorney.ResponseParser),
    ("patent/applications/{applicationNumberText}/assignment", ["GET"], assignments.ResponseParser),
    ("patent/applications/{applicationNumberText}/foreign-priority", ["GET"], foreign_priority.ResponseParser),
    ("patent/applications/{applicationNumberText}/associated-documents", ["GET"], associated_documents.ResponseParser),
    ("patent/status-codes", ["GET", "POST"], status_codes.ResponseParser),
]

documentation_urls = [
    "/apis/patent-file-wrapper/search",
    "/apis/patent-file-wrapper/application-data",
    "/apis/patent-file-wrapper/continuity",
    "/apis/patent-file-wrapper/documents",
    "/apis/patent-file-wrapper/transactions",
    "/apis/patent-file-wrapper/patent-term-adjustment",
    "/apis/patent-file-wrapper/address",
    "/apis/patent-file-wrapper/assignments",
    "/apis/patent-file-wrapper/foreign-priority",
    "/apis/patent-file-wrapper/associated-documents",
    "/apis/patent-file-wrapper/status-codes"
]
