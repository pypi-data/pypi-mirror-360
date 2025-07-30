# Final fix: Ensuring that the dataclasses are generated correctly.
from pathlib import Path
from typing import Dict, Any

def map_json_type_to_python(json_type: str) -> str:
    """Map JSON types to Python types."""
    mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List",
        "object": "Any"
    }
    return mapping.get(json_type, "Any")


import re


def to_pascal_case(name: str) -> str:
    """Convert snake_case or camelCase names to PascalCase for class names."""
    return ''.join(word.capitalize() for word in re.split(r'_|(?=[A-Z])', name))


def sanitize_field_name(name: str) -> str:
    reserved_keywords = {"class": "className", "subclass": "subClass", "class/subclass": "classSubclass"}
    return reserved_keywords.get(name, name.replace("/", "_"))



def generate_classes_from_schema(schema: Dict[str, Any]) -> str:
    class_definitions = {}

    def process_object(name: str, properties: Dict[str, Any]) -> str:
        class_name = to_pascal_case(name)
        if class_name in class_definitions:
            return class_definitions[class_name]

        class_code = f"@dataclass\nclass {class_name}:\n"
        body_lines = []

        for prop_name, prop_info in properties.items():
            json_type = prop_info.get("type", "Any")
            safe_name = sanitize_field_name(prop_name)

            if json_type == "array":
                if isinstance(prop_info.get("items"), dict) and prop_info["items"].get("type") == "object":
                    item_class_name = to_pascal_case(prop_name)
                    class_definitions[item_class_name] = process_object(item_class_name, prop_info["items"]["properties"])
                    body_lines.append(f"    {safe_name}: List[{item_class_name}] = field(default_factory=list)")
                else:
                    if isinstance(prop_info["items"], list):
                        item_type = map_json_type_to_python(prop_info["items"][0].get("type", "Any"))
                    else:
                        if isinstance(prop_info.get("items"), list):
                            if len(prop_info["items"]) > 0 and isinstance(prop_info["items"][0], dict):
                                item_type = map_json_type_to_python(prop_info["items"][0].get("type", "Any"))
                            else:
                                item_type = "Any"  # Fallback
                        else:
                            item_type = map_json_type_to_python(prop_info["items"].get("type", "Any"))

                    body_lines.append(f"    {safe_name}: List[{item_type}] = field(default_factory=list)")

            elif json_type == "object":
                nested_class_name = to_pascal_case(prop_name)
                class_definitions[nested_class_name] = process_object(nested_class_name, prop_info["properties"])
                body_lines.append(f"    {safe_name}: Optional[{nested_class_name}] = None")

            else:
                python_type = map_json_type_to_python(json_type)
                body_lines.append(f"    {safe_name}: Optional[{python_type}] = None")

        if not body_lines:
            body_lines.append("    pass")

        class_code += "\n".join(body_lines) + "\n"
        class_definitions[class_name] = class_code
        return class_code

    for main_key, main_value in schema["properties"].items():
        class_name = to_pascal_case(main_key)
        if main_value["type"] == "object":
            class_definitions[class_name] = process_object(class_name, main_value["properties"])
        elif main_value["type"] == "array" and "items" in main_value:
            if isinstance(main_value["items"], dict) and main_value["items"].get("type") == "object":
                item_class_name = to_pascal_case(main_key)
                class_definitions[item_class_name] = process_object(item_class_name, main_value["items"]["properties"])
            elif isinstance(main_value["items"], dict) and main_value["items"].get("type") == "object":
                item_class_name = to_pascal_case(main_key)
                class_definitions[item_class_name] = process_object(item_class_name, main_value["items"]["properties"])

    return "\n\n".join(class_definitions.values())


# Example JSON schema loading and dataclass generation
example_json_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "count": {
      "type": "integer"
    },
    "patentFileWrapperDataBag": {
      "type": "array",
      "items": [
        {
          "type": "object",
          "properties": {
            "applicationNumberText": {
              "type": "string"
            },
            "applicationMetaData": {
              "type": "object",
              "properties": {
                "nationalStageIndicator": {
                  "type": "boolean"
                },
                "entityStatusData": {
                  "type": "object",
                  "properties": {
                    "smallEntityStatusIndicator": {
                      "type": "boolean"
                    },
                    "businessEntityStatusCategory": {
                      "type": "string"
                    }
                  }
                },
                "publicationDateBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "string"
                    }
                  ]
                },
                "publicationSequenceNumberBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "string"
                    }
                  ]
                },
                "publicationCategoryBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "string"
                    }
                  ]
                },
                "docketNumber": {
                  "type": "string"
                },
                "firstInventorToFileIndicator": {
                  "type": "string"
                },
                "firstApplicantName": {
                  "type": "string"
                },
                "firstInventorName": {
                  "type": "string"
                },
                "applicationConfirmationNumber": {
                  "type": "integer"
                },
                "applicationStatusDate": {
                  "type": "string"
                },
                "applicationStatusDescriptionText": {
                  "type": "string"
                },
                "filingDate": {
                  "type": "string"
                },
                "effectiveFilingDate": {
                  "type": "string"
                },
                "grantDate": {
                  "type": "string"
                },
                "groupArtUnitNumber": {
                  "type": "string"
                },
                "applicationTypeCode": {
                  "type": "string"
                },
                "applicationTypeLabelName": {
                  "type": "string"
                },
                "applicationTypeCategory": {
                  "type": "string"
                },
                "inventionTitle": {
                  "type": "string"
                },
                "patentNumber": {
                  "type": "string"
                },
                "applicationStatusCode": {
                  "type": "integer"
                },
                "earliestPublicationNumber": {
                  "type": "string"
                },
                "earliestPublicationDate": {
                  "type": "string"
                },
                "pctPublicationNumber": {
                  "type": "string"
                },
                "pctPublicationDate": {
                  "type": "string"
                },
                "internationalRegistrationPublicationDate": {
                  "type": "string"
                },
                "internationalRegistrationNumber": {
                  "type": "string"
                },
                "examinerNameText": {
                  "type": "string"
                },
                "class": {
                  "type": "string"
                },
                "subclass": {
                  "type": "string"
                },
                "class/subclass": {
                  "type": "string"
                },
                "customerNumber": {
                  "type": "integer"
                },
                "cpcClassificationBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    }
                  ]
                },
                "applicantBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "object",
                      "properties": {
                        "applicantNameText": {
                          "type": "string"
                        },
                        "firstName": {
                          "type": "string"
                        },
                        "middleName": {
                          "type": "string"
                        },
                        "lastName": {
                          "type": "string"
                        },
                        "preferredName": {
                          "type": "string"
                        },
                        "namePrefix": {
                          "type": "string"
                        },
                        "nameSuffix": {
                          "type": "string"
                        },
                        "countryCode": {
                          "type": "string"
                        },
                        "correspondenceAddressBag": {
                          "type": "array",
                          "items": [
                            {
                              "type": "object",
                              "properties": {
                                "nameLineOneText": {
                                  "type": "string"
                                },
                                "nameLineTwoText": {
                                  "type": "string"
                                },
                                "addressLineOneText": {
                                  "type": "string"
                                },
                                "addressLineTwoText": {
                                  "type": "string"
                                },
                                "geographicRegionName": {
                                  "type": "string"
                                },
                                "geographicRegionCode": {
                                  "type": "string"
                                },
                                "postalCode": {
                                  "type": "string"
                                },
                                "cityName": {
                                  "type": "string"
                                },
                                "countryCode": {
                                  "type": "string"
                                },
                                "countryName": {
                                  "type": "string"
                                },
                                "postalAddressCategory": {
                                  "type": "string"
                                }
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                },
                "inventorBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "object",
                      "properties": {
                        "firstName": {
                          "type": "string"
                        },
                        "middleName": {
                          "type": "string"
                        },
                        "lastName": {
                          "type": "string"
                        },
                        "namePrefix": {
                          "type": "string"
                        },
                        "nameSuffix": {
                          "type": "string"
                        },
                        "preferredName": {
                          "type": "string"
                        },
                        "countryCode": {
                          "type": "string"
                        },
                        "inventorNameText": {
                          "type": "string"
                        },
                        "correspondenceAddressBag": {
                          "type": "array",
                          "items": [
                            {
                              "type": "object",
                              "properties": {
                                "nameLineOneText": {
                                  "type": "string"
                                },
                                "nameLineTwoText": {
                                  "type": "string"
                                },
                                "addressLineOneText": {
                                  "type": "string"
                                },
                                "addressLineTwoText": {
                                  "type": "string"
                                },
                                "geographicRegionName": {
                                  "type": "string"
                                },
                                "geographicRegionCode": {
                                  "type": "string"
                                },
                                "postalCode": {
                                  "type": "string"
                                },
                                "cityName": {
                                  "type": "string"
                                },
                                "countryCode": {
                                  "type": "string"
                                },
                                "countryName": {
                                  "type": "string"
                                },
                                "postalAddressCategory": {
                                  "type": "string"
                                }
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                }
              }
            },
            "correspondenceAddressBag": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "nameLineOneText": {
                      "type": "string"
                    },
                    "nameLineTwoText": {
                      "type": "string"
                    },
                    "addressLineOneText": {
                      "type": "string"
                    },
                    "addressLineTwoText": {
                      "type": "string"
                    },
                    "geographicRegionName": {
                      "type": "string"
                    },
                    "geographicRegionCode": {
                      "type": "string"
                    },
                    "postalCode": {
                      "type": "string"
                    },
                    "cityName": {
                      "type": "string"
                    },
                    "countryCode": {
                      "type": "string"
                    },
                    "countryName": {
                      "type": "string"
                    },
                    "postalAddressCategory": {
                      "type": "string"
                    }
                  }
                }
              ]
            },
            "assignmentBag": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "reelNumber": {
                      "type": "integer"
                    },
                    "frameNumber": {
                      "type": "integer"
                    },
                    "reelNumber/frameNumber": {
                      "type": "string"
                    },
                    "pageNumber": {
                      "type": "integer"
                    },
                    "assignmentReceivedDate": {
                      "type": "string"
                    },
                    "assignmentRecordedDate": {
                      "type": "string"
                    },
                    "assignmentMailedDate": {
                      "type": "string"
                    },
                    "conveyanceText": {
                      "type": "string"
                    },
                    "assignorBag": {
                      "type": "array",
                      "items": [
                        {
                          "type": "object",
                          "properties": {
                            "assignorName": {
                              "type": "string"
                            },
                            "executionDate": {
                              "type": "string"
                            }
                          }
                        }
                      ]
                    },
                    "assigneeBag": {
                      "type": "array",
                      "items": [
                        {
                          "type": "object",
                          "properties": {
                            "assigneeNameText": {
                              "type": "string"
                            },
                            "assigneeAddress": {
                              "type": "object",
                              "properties": {
                                "addressLineOneText": {
                                  "type": "string"
                                },
                                "addressLineTwoText": {
                                  "type": "string"
                                },
                                "cityName": {
                                  "type": "string"
                                },
                                "geographicRegionName": {
                                  "type": "string"
                                },
                                "geographicRegionCode": {
                                  "type": "string"
                                },
                                "countryName": {
                                  "type": "string"
                                },
                                "postalCode": {
                                  "type": "string"
                                }
                              }
                            }
                          }
                        }
                      ]
                    },
                    "correspondenceAddressBag": {
                      "type": "array",
                      "items": [
                        {
                          "type": "object",
                          "properties": {
                            "correspondentNameText": {
                              "type": "string"
                            },
                            "addressLineOneText": {
                              "type": "string"
                            },
                            "addressLineTwoText": {
                              "type": "string"
                            },
                            "addressLineThreeText": {
                              "type": "string"
                            },
                            "addressLineFourText": {
                              "type": "string"
                            }
                          }
                        }
                      ]
                    }
                  }
                }
              ]
            },
            "recordAttorney": {
              "type": "object",
              "properties": {
                "customerNumber": {
                  "type": "object",
                  "properties": {
                    "patronIdentifier": {
                      "type": "integer"
                    },
                    "organizationStandardName": {
                      "type": "string"
                    },
                    "powerOfAttorneyAddressBag": {
                      "type": "array",
                      "items": [
                        {
                          "type": "object",
                          "properties": {
                            "nameLineOneText": {
                              "type": "string"
                            },
                            "addressLineOneText": {
                              "type": "string"
                            },
                            "addressLineTwoText": {
                              "type": "string"
                            },
                            "geographicRegionName": {
                              "type": "string"
                            },
                            "geographicRegionCode": {
                              "type": "string"
                            },
                            "postalCode": {
                              "type": "string"
                            },
                            "cityName": {
                              "type": "string"
                            },
                            "countryCode": {
                              "type": "string"
                            },
                            "countryName": {
                              "type": "string"
                            }
                          }
                        }
                      ]
                    },
                    "telecommunicationAddressBag": {
                      "type": "array",
                      "items": [
                        {
                          "type": "object",
                          "properties": {
                            "telecommunicationNumber": {
                              "type": "string"
                            },
                            "extensionNumber": {
                              "type": "string"
                            },
                            "telecomTypeCode": {
                              "type": "string"
                            }
                          }
                        }
                      ]
                    }
                  }
                },
                "powerOfAttorneyBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "object",
                      "properties": {
                        "firstName": {
                          "type": "string"
                        },
                        "middleName": {
                          "type": "string"
                        },
                        "lastName": {
                          "type": "string"
                        },
                        "namePrefix": {
                          "type": "string"
                        },
                        "nameSuffix": {
                          "type": "string"
                        },
                        "preferredName": {
                          "type": "string"
                        },
                        "countryCode": {
                          "type": "string"
                        },
                        "registrationNumber": {
                          "type": "string"
                        },
                        "activeIndicator": {
                          "type": "string"
                        },
                        "registeredPractitionerCategory": {
                          "type": "string"
                        },
                        "attorneyAddressBag": {
                          "type": "array",
                          "items": [
                            {
                              "type": "object",
                              "properties": {
                                "nameLineOneText": {
                                  "type": "string"
                                },
                                "nameLineTwoText": {
                                  "type": "string"
                                },
                                "addressLineOneText": {
                                  "type": "string"
                                },
                                "addressLineTwoText": {
                                  "type": "string"
                                },
                                "geographicRegionName": {
                                  "type": "string"
                                },
                                "geographicRegionCode": {
                                  "type": "string"
                                },
                                "postalCode": {
                                  "type": "string"
                                },
                                "cityName": {
                                  "type": "string"
                                },
                                "countryCode": {
                                  "type": "string"
                                },
                                "countryName": {
                                  "type": "string"
                                }
                              }
                            }
                          ]
                        },
                        "telecommunicationAddressBag": {
                          "type": "array",
                          "items": [
                            {
                              "type": "object",
                              "properties": {
                                "telecommunicationNumber": {
                                  "type": "string"
                                },
                                "extensionNumber": {
                                  "type": "string"
                                },
                                "telecomTypeCode": {
                                  "type": "string"
                                }
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                },
                "attorneyBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "object",
                      "properties": {
                        "firstName": {
                          "type": "string"
                        },
                        "middleName": {
                          "type": "string"
                        },
                        "lastName": {
                          "type": "string"
                        },
                        "namePrefix": {
                          "type": "string"
                        },
                        "nameSuffix": {
                          "type": "string"
                        },
                        "registrationNumber": {
                          "type": "string"
                        },
                        "activeIndicator": {
                          "type": "string"
                        },
                        "registeredPractitionerCategory": {
                          "type": "string"
                        },
                        "attorneyAddressBag": {
                          "type": "array",
                          "items": [
                            {
                              "type": "object",
                              "properties": {
                                "nameLineOneText": {
                                  "type": "string"
                                },
                                "nameLineTwoText": {
                                  "type": "string"
                                },
                                "addressLineOneText": {
                                  "type": "string"
                                },
                                "addressLineTwoText": {
                                  "type": "string"
                                },
                                "geographicRegionName": {
                                  "type": "string"
                                },
                                "geographicRegionCode": {
                                  "type": "string"
                                },
                                "postalCode": {
                                  "type": "string"
                                },
                                "cityName": {
                                  "type": "string"
                                },
                                "countryCode": {
                                  "type": "string"
                                },
                                "countryName": {
                                  "type": "string"
                                }
                              }
                            }
                          ]
                        },
                        "telecommunicationAddressBag": {
                          "type": "array",
                          "items": [
                            {
                              "type": "object",
                              "properties": {
                                "telecommunicationNumber": {
                                  "type": "string"
                                },
                                "extensionNumber": {
                                  "type": "string"
                                },
                                "telecomTypeCode": {
                                  "type": "string"
                                }
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                }
              }
            },
            "foreignPriorityBag": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "ipOfficeName": {
                      "type": "string"
                    },
                    "filingDate": {
                      "type": "string"
                    },
                    "applicationNumberText": {
                      "type": "string"
                    }
                  }
                }
              ]
            },
            "parentContinuityBag": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "firstInventorToFileIndicator": {
                      "type": "boolean"
                    },
                    "parentApplicationStatusCode": {
                      "type": "integer"
                    },
                    "parentPatentNumber": {
                      "type": "string"
                    },
                    "parentApplicationStatusDescriptionText": {
                      "type": "string"
                    },
                    "parentApplicationFilingDate": {
                      "type": "string"
                    },
                    "parentApplicationNumberText": {
                      "type": "string"
                    },
                    "childApplicationNumberText": {
                      "type": "string"
                    },
                    "claimParentageTypeCode": {
                      "type": "string"
                    },
                    "claimParentageTypeCodeDescription": {
                      "type": "string"
                    }
                  }
                }
              ]
            },
            "childContinuityBag": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "childApplicationStatusCode": {
                      "type": "integer"
                    },
                    "parentApplicationNumberText": {
                      "type": "string"
                    },
                    "childApplicationNumberText": {
                      "type": "string"
                    },
                    "childApplicationStatusDescriptionText": {
                      "type": "string"
                    },
                    "childApplicationFilingDate": {
                      "type": "string"
                    },
                    "firstInventorToFileIndicator": {
                      "type": "boolean"
                    },
                    "childPatentNumber": {
                      "type": "string"
                    },
                    "claimParentageTypeCode": {
                      "type": "string"
                    },
                    "claimParentageTypeCodeDescription": {
                      "type": "string"
                    }
                  }
                }
              ]
            },
            "patentTermAdjustmentData": {
              "type": "object",
              "properties": {
                "aDelayQuantity": {
                  "type": "number"
                },
                "adjustmentTotalQuantity": {
                  "type": "number"
                },
                "applicantDayDelayQuantity": {
                  "type": "number"
                },
                "bDelayQuantity": {
                  "type": "number"
                },
                "cDelayQuantity": {
                  "type": "number"
                },
                "filingDate": {
                  "type": "string"
                },
                "grantDate": {
                  "type": "string"
                },
                "nonOverlappingDayQuantity": {
                  "type": "number"
                },
                "overlappingDayQuantity": {
                  "type": "number"
                },
                "ipOfficeDayDelayQuantity": {
                  "type": "number"
                },
                "patentTermAdjustmentHistoryDataBag": {
                  "type": "array",
                  "items": [
                    {
                      "type": "object",
                      "properties": {
                        "eventDate": {
                          "type": "string"
                        },
                        "applicantDayDelayQuantity": {
                          "type": "number"
                        },
                        "eventDescriptionText": {
                          "type": "string"
                        },
                        "eventSequenceNumber": {
                          "type": "number"
                        },
                        "ipOfficeDayDelayQuantity": {
                          "type": "number"
                        },
                        "originatingEventSequenceNumber": {
                          "type": "number"
                        },
                        "ptaPteCode": {
                          "type": "string"
                        }
                      }
                    }
                  ]
                }
              }
            },
            "eventDataBag": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "eventCode": {
                      "type": "string"
                    },
                    "eventDescriptionText": {
                      "type": "string"
                    },
                    "eventDate": {
                      "type": "string"
                    }
                  }
                }
              ]
            },
            "pgpubDocumentMetaData": {
              "type": "object",
              "properties": {
                "zipFileName": {
                  "type": "string"
                },
                "productIdentifier": {
                  "type": "string"
                },
                "fileLocationURI": {
                  "type": "string"
                },
                "fileCreateDateTime": {
                  "type": "string"
                },
                "xmlFileName": {
                  "type": "string"
                }
              }
            },
            "grantDocumentMetaData": {
              "type": "object",
              "properties": {
                "zipFileName": {
                  "type": "string"
                },
                "productIdentifier": {
                  "type": "string"
                },
                "fileLocationURI": {
                  "type": "string"
                },
                "fileCreateDateTime": {
                  "type": "string"
                },
                "xmlFileName": {
                  "type": "string"
                }
              }
            },
            "lastIngestionTime": {
              "type": "string"
            }
          }
        }
      ]
    }
  }
}

# Generate the Python dataclass code
dataclass_code = generate_classes_from_schema(example_json_schema)

# Save the generated code to a Python file
output_path = Path("generated_classes.py")
output_path.write_text(f"from dataclasses import dataclass, field\nfrom typing import List, Optional, Any\n\n{dataclass_code}")

# dataclass_code  # Display the generated code for review!
