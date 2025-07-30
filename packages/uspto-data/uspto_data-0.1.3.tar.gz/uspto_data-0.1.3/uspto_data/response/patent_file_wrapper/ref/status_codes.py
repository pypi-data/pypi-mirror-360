# ENDPOINT
endpoint = "/patent/status-codes"
# JSON RESPONSE SAMPLE
example_json = {
  "count": 1,
  "statusCodeBag": [
    {
      "applicationStatusCode": 3,
      "applicationStatusDescriptionText": "Proceedings Terminated"
    }
  ],
  "requestIdentifier": "df5b5478-ad3e-4ad2-b3bc-611838ccb56c"
}

documentation = """
Conduct a search of all patent status codes and description Use this endpoint if you are interested in fetching/searching patents status codes or status code description. For example, you want to return all patents status code description that match your search term, such as Rejection or Abandonment. You can also use multiple search terms, such as “Payment AND Received” .

Other details for using the Search endpoint:

If you don’t specify the field in which you want us to look for this search term, we will look for it across all data fields () and return any matching status codes and corresponding description.
All search syntaxes are applicable to this endpoint, meaning any number of combinations is possible. Some example requests are below, but for more information, view the Simplified Syntax documentation that is linked in the Open Data Portal API page. You can also test the API right away in Swagger UI.

GET /patent/status-codes

Returns a list of all patents status codes and its corresponding description.

Note: API Key is required. Obtain an API key.

POST See Swagger documentation

Returns a list of all patents and applications that match your search term.

Note: API Key is required. Obtain an API key.
"""

response_info = """
Data Property	Description	Type
statusCodeBag	Status code bag.	N/A
  applicationStatusCode	Status codes.	Number
  applicationStatusDescriptionText	Application status code description.	String
"""