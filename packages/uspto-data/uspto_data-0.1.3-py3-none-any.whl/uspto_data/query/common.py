def get_dependencies_from_xml(claim_element):
    """
    Extract claim references from a claim element.

    Args:
        claim_element: The XML element of the claim

    Returns:
        list: A list of strings containing the referenced claim numbers (without leading zeros)
    """
    # Find all claim-ref elements
    claim_refs = claim_element.findall(".//claim-ref")

    # Extract the idref attribute and convert to simple numbers
    dependency_numbers = []
    for ref in claim_refs:
        idref = ref.get("idref")
        if idref and idref.startswith("CLM-"):
            # Extract the number portion and remove leading zeros
            num = idref.split("-")[1].lstrip("0")
            if num:  # Check if num is not empty
                dependency_numbers.append(num)

    return dependency_numbers