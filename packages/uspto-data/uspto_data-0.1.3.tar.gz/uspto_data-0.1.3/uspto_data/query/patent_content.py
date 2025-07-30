import re
import xml.etree.ElementTree as ET

from uspto_data.query.common import get_dependencies_from_xml


class USPatentContent:
    """Class to parse and store structured U.S. Patent Grant XML content, ensuring inline XML elements are processed correctly."""

    def __init__(self, xml_content):
        self.xml = xml_content
        self.tree = ET.ElementTree(ET.fromstring(xml_content))
        self.root = self.tree.getroot()
        self.data = {}
        self.parse_data()

    def extract_text_with_inline_elements(self, element):
        """
        Extracts text from an XML element while preserving inline components like <figref>, <b>, <i>.
        Ensures all text content is preserved, including text inside and outside of nested elements.
        """
        if element is None:
            return ""

        # Initialize result with the element's direct text content (or empty string if None)
        result = element.text or ""

        # Process all child elements
        for child in element:
            # Process the child element based on its tag
            if child.tag == "figref":
                # Handle Figure References
                child_text = child.text or ""
                result += f"[Figure: {child_text.strip()}]"
            elif child.tag == "b":
                # Handle Bold Text
                child_text = child.text or ""
                result += f"**{child_text.strip()}**"
            elif child.tag == "i":
                # Handle Italic Text
                child_text = child.text or ""
                result += f"*{child_text.strip()}*"
            else:
                # Recursively process other elements
                result += self.extract_text_with_inline_elements(child)

            # Always add the tail text of the child element (text that follows the child's closing tag)
            if child.tail:
                result += child.tail

        return result

    def parse_data(self):
        """Extract key patent data based on U.S. Patent XML v4.5 documentation."""

        bib_data = self.root.find("us-bibliographic-data-grant")
        if bib_data is not None:
            pub_ref = bib_data.find("publication-reference/document-id")
            if pub_ref is None:
                pub_ref = {}
            self.data["patent_number"] = self.get_text_from_xml(pub_ref, "doc-number")
            self.data["kind"] = self.get_text_from_xml(pub_ref, "kind")
            self.data["publication_date"] = self.get_text_from_xml(pub_ref, "date")

        # **Title**
        self.data["title"] = self.get_text_from_xml(bib_data, "invention-title")

        # **Abstract**
        abstract = self.root.find("abstract")
        self.data["abstract"] = " ".join(
            [self.extract_text_with_inline_elements(p) for p in abstract.findall("p")]
        ) if abstract is not None else None

        # **Claims**
        claims = self.root.findall("claims/claim")
        self.data["claims"] = [
            {
                "claim_number": claim.get("num"),
                "text": self.extract_text_with_inline_elements(claim.find("claim-text")),
                "dependencies": get_dependencies_from_xml(claim)
            }
            for claim in claims if claim.find("claim-text") is not None
        ]

        # **Detailed Description (Structured Parsing with XML components in paragraphs)**
        self.data["description"] = self.parse_description()

    import re
    import xml.etree.ElementTree as ET

    def parse_description(self):
        """Parses the description while dynamically handling sections and headings."""

        import re
        import xml.etree.ElementTree as ET

        # Step 1: Convert <? ... ?> into proper XML elements
        xml_modified = re.sub(
            r'<\?(\w+(?:-\w+)*)\s+(.*?)\s*end="(lead|tail)"\?>',
            r'<section-marker type="\1" \2 end="\3"/>',
            self.xml
        )

        # Optional: Debugging
        with open("debug_modified.xml", "w", encoding="utf-8") as f:
            f.write(xml_modified)

        try:
            # Step 2: Parse the modified XML
            root = ET.fromstring(xml_modified)
        except ET.ParseError as e:
            print("XML Parsing Error:", e)
            raise

        # Step 3: Initialize data structures
        section_stack = []
        current_section = None
        description_data = {"sections": []}

        for elem in root.iter():
            if elem.tag == "section-marker":
                desc = elem.get("description", "Untitled Section")
                end_type = elem.get("end")

                if end_type == "lead":
                    new_section = {"title": desc, "paragraphs": []}
                    section_stack.append(new_section)
                    current_section = new_section
                elif end_type == "tail" and section_stack:
                    closed_section = section_stack.pop()
                    if closed_section["paragraphs"]:
                        description_data["sections"].append(closed_section)
                    current_section = section_stack[-1] if section_stack else None

            elif elem.tag == "heading":
                heading_text = elem.text.strip() if elem.text else "Untitled Heading"
                heading_level = elem.get("level", "unknown")
                heading_entry = {
                    "heading": heading_text,
                    "level": heading_level,
                    "text": ""
                }

                if current_section:
                    current_section["paragraphs"].append(heading_entry)
                else:
                    default_section = {
                        "title": "General",
                        "paragraphs": [heading_entry]
                    }
                    description_data["sections"].append(default_section)
                    current_section = default_section

            elif elem.tag == "p":
                # ✅ Use updated inline-safe paragraph parser
                paragraph_text = self.extract_text_with_inline_elements(elem)
                paragraph_num = elem.get("num", "Unknown")

                paragraph_entry = {"number": paragraph_num, "text": paragraph_text}

                if current_section:
                    current_section["paragraphs"].append(paragraph_entry)
                else:
                    if not description_data["sections"]:
                        description_data["sections"].append({"title": "General", "paragraphs": []})
                    description_data["sections"][0]["paragraphs"].append(paragraph_entry)

        return description_data

    def get_text_from_xml(self, element, path):
        """Helper function to retrieve text from an XML element."""
        elem = element.find(path)
        return elem.text.strip() if elem is not None and elem.text else None

    def get_title(self):
        """Retrieve the title of the patent."""
        return self.data.get("title", "")

    def get_claims(self):
        """Retrieve structured list of claims with their numbers."""
        return self.data.get("claims", [])

    def get_independent_claims(self):
        """
        Retrieve only the independent claims from the patent.
        A claim is considered independent if it doesn't reference another claim.
        Independent claims don't contain <claim-ref> tags in their text.

        Returns:
            list: List of independent claims with their numbers
        """
        all_claims = self.get_claims()
        independent_claims = []

        for claim in all_claims:
            if not claim.get("dependencies"):
                independent_claims.append(claim)

        return independent_claims

    def get_abstract(self):
        """Retrieve the abstract text of the patent."""
        return self.data.get("abstract", "")

    def get_description(self):
        """Retrieve the structured description with sections and paragraph numbers."""
        return self.data.get("description", {})

    def get_figures(self):
        """Extract figure image references from the patent XML."""
        figures = []
        drawings = self.root.find("drawings")

        if drawings is not None:
            for figure in drawings.findall("figure"):
                img = figure.find("img")
                figures.append({
                    "figure_number": figure.get("num", "Unknown"),
                    "image_file": img.get("file") if img is not None else None,
                    "width": img.get("wi") if img is not None else None,
                    "height": img.get("he") if img is not None else None,
                    "format": img.get("img-format") if img is not None else None,
                    "content_type": img.get("img-content") if img is not None else None,
                    "description": img.get("alt",
                                           "No description available") if img is not None else "No description available",
                })
        return figures

    def get_full_text(self):
        """Returns the full patent text, including abstract, description, and claims."""

        full_text_data = {
            "title": self.get_title(),
            "abstract": self.get_abstract(),
            "description": self.get_description(),
            "claims": self.get_claims(),
            "figures": self.get_figures()
        }

        def to_string():
            """Formats and returns the full patent text as a readable string."""
            text_representation = []

            # Abstract Section
            if full_text_data.get("abstract"):
                text_representation.append(f"=== ABSTRACT ===\n{full_text_data['abstract']}\n")

            # Description Section
            if full_text_data["description"]:
                text_representation.append("=== DETAILED DESCRIPTION ===")
                for section in full_text_data["description"].get("sections", []):
                    text_representation.append(f"\n## {section['title']}\n")
                    for paragraph in section["paragraphs"]:
                        text_representation.append(f"[{paragraph['number']}] {paragraph['text']}\n")

            # Claims Section
            if full_text_data["claims"]:
                text_representation.append("=== CLAIMS ===")
                for claim in full_text_data["claims"]:
                    text_representation.append(f"\nClaim {claim['claim_number']}: {claim['text']}\n")

            # Figures Section
            if full_text_data["figures"]:
                text_representation.append("=== FIGURES ===")
                for fig in full_text_data["figures"]:
                    text_representation.append(f"\nFigure {fig['figure_number']}: {fig['description']}\n")

            return "\n".join(text_representation)

        # Attach the method dynamically
        full_text_data["to_string"] = to_string

        return full_text_data

    def get_data(self):
        """Return extracted data as a structured dictionary."""
        return self.data

# Example Usage
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE us-patent-grant SYSTEM "us-patent-grant-v45-2014-04-03.dtd" [ ]>
<us-patent-grant lang="EN" dtd-version="v4.5 2014-04-03" file="US10123456-20181106.XML" status="PRODUCTION" id="us-patent-grant" country="US" date-produced="20181022" date-publ="20181106">
<us-bibliographic-data-grant>
<publication-reference>
<document-id>
<country>US</country>
<doc-number>10123456</doc-number>
<kind>B2</kind>
<date>20181106</date>
</document-id>
</publication-reference>
<application-reference appl-type="utility">
<document-id>
<country>US</country>
<doc-number>14925737</doc-number>
<date>20151028</date>
</document-id>
</application-reference>
<us-application-series-code>14</us-application-series-code>
<us-term-of-grant>
<us-term-extension>140</us-term-extension>
</us-term-of-grant>
<classifications-ipcr>
<classification-ipcr>
<ipc-version-indicator><date>20060101</date></ipc-version-indicator>
<classification-level>A</classification-level>
<section>B</section>
<class>23</class>
<subclass>P</subclass>
<main-group>15</main-group>
<subgroup>26</subgroup>
<symbol-position>F</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20181106</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
</classification-ipcr>
<classification-ipcr>
<ipc-version-indicator><date>20060101</date></ipc-version-indicator>
<classification-level>A</classification-level>
<section>H</section>
<class>05</class>
<subclass>K</subclass>
<main-group>7</main-group>
<subgroup>20</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20181106</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
</classification-ipcr>
</classifications-ipcr>
<classifications-cpc>
<main-cpc>
<classification-cpc>
<cpc-version-indicator><date>20130101</date></cpc-version-indicator>
<section>H</section>
<class>05</class>
<subclass>K</subclass>
<main-group>7</main-group>
<subgroup>2029</subgroup>
<symbol-position>F</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20181106</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
<scheme-origination-code>C</scheme-origination-code>
</classification-cpc>
</main-cpc>
<further-cpc>
<classification-cpc>
<cpc-version-indicator><date>20130101</date></cpc-version-indicator>
<section>B</section>
<class>23</class>
<subclass>P</subclass>
<main-group>15</main-group>
<subgroup>26</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20181106</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
<scheme-origination-code>C</scheme-origination-code>
</classification-cpc>
</further-cpc>
</classifications-cpc>
<invention-title id="d2e53">Phase change material heat sink using additive manufacturing and method</invention-title>
<us-references-cited>
<us-citation>
<patcit num="00001">
<document-id>
<country>US</country>
<doc-number>3519067</doc-number>
<kind>A</kind>
<name>Schmidt</name>
<date>19700700</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00002">
<document-id>
<country>US</country>
<doc-number>4259401</doc-number>
<kind>A</kind>
<name>Chahroudi et al.</name>
<date>19810300</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00003">
<document-id>
<country>US</country>
<doc-number>4928448</doc-number>
<kind>A</kind>
<name>Phillip</name>
<date>19900500</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00004">
<document-id>
<country>US</country>
<doc-number>5788178</doc-number>
<kind>A</kind>
<name>Barrett, Jr.</name>
<date>19980800</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00005">
<document-id>
<country>US</country>
<doc-number>5792390</doc-number>
<kind>A</kind>
<name>Marino</name>
<date>19980800</date>
</document-id>
</patcit>
<category>cited by examiner</category>
<classification-cpc-text>F24F 6/00</classification-cpc-text>
<classification-national><country>US</country><main-classification>215359</main-classification></classification-national>
</us-citation>
<us-citation>
<patcit num="00006">
<document-id>
<country>US</country>
<doc-number>6474593</doc-number>
<kind>B1</kind>
<name>Lipeies et al.</name>
<date>20021100</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00007">
<document-id>
<country>US</country>
<doc-number>6959753</doc-number>
<kind>B1</kind>
<name>Weber et al.</name>
<date>20051100</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00008">
<document-id>
<country>US</country>
<doc-number>7069975</doc-number>
<kind>B1</kind>
<name>Haws et al.</name>
<date>20060700</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00009">
<document-id>
<country>US</country>
<doc-number>7416017</doc-number>
<kind>B2</kind>
<name>Haws et al.</name>
<date>20080800</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00010">
<document-id>
<country>US</country>
<doc-number>7628352</doc-number>
<kind>B1</kind>
<name>Low et al.</name>
<date>20091200</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00011">
<document-id>
<country>US</country>
<doc-number>7781709</doc-number>
<kind>B1</kind>
<name>Jones et al.</name>
<date>20100800</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00012">
<document-id>
<country>US</country>
<doc-number>7810552</doc-number>
<kind>B2</kind>
<name>Slaughter</name>
<date>20101000</date>
</document-id>
</patcit>
<category>cited by examiner</category>
<classification-cpc-text>B22F 3/1055</classification-cpc-text>
<classification-national><country>US</country><main-classification>165148</main-classification></classification-national>
</us-citation>
<us-citation>
<patcit num="00013">
<document-id>
<country>US</country>
<doc-number>7834301</doc-number>
<kind>B2</kind>
<name>Clingman</name>
<date>20101100</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00014">
<document-id>
<country>US</country>
<doc-number>7891298</doc-number>
<kind>B2</kind>
<name>Minick et al.</name>
<date>20110200</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00015">
<document-id>
<country>US</country>
<doc-number>7999212</doc-number>
<kind>B1</kind>
<name>Thiesen et al.</name>
<date>20110800</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00016">
<document-id>
<country>US</country>
<doc-number>8534348</doc-number>
<kind>B2</kind>
<name>Ohsawa</name>
<date>20130900</date>
</document-id>
</patcit>
<category>cited by examiner</category>
<classification-cpc-text>B23P 15/26</classification-cpc-text>
<classification-national><country>US</country><main-classification>16510426</main-classification></classification-national>
</us-citation>
<us-citation>
<patcit num="00017">
<document-id>
<country>US</country>
<doc-number>2002/0033247</doc-number>
<kind>A1</kind>
<name>Neuschutz</name>
<date>20020300</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00018">
<document-id>
<country>US</country>
<doc-number>2009/0040726</doc-number>
<kind>A1</kind>
<name>Hoffman</name>
<date>20090200</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00019">
<document-id>
<country>US</country>
<doc-number>2010/0147152</doc-number>
<kind>A1</kind>
<name>Kosugi</name>
<date>20100600</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00020">
<document-id>
<country>US</country>
<doc-number>2011/0284188</doc-number>
<kind>A1</kind>
<name>Cai</name>
<date>20111100</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00021">
<document-id>
<country>US</country>
<doc-number>2012/0240919</doc-number>
<kind>A1</kind>
<name>Baumann</name>
<date>20120900</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00022">
<document-id>
<country>US</country>
<doc-number>2014/0030575</doc-number>
<kind>A1</kind>
<name>Kim</name>
<date>20140100</date>
</document-id>
</patcit>
<category>cited by examiner</category>
<classification-cpc-text>H05K 7/20436</classification-cpc-text>
<classification-national><country>US</country><main-classification>429120</main-classification></classification-national>
</us-citation>
<us-citation>
<patcit num="00023">
<document-id>
<country>US</country>
<doc-number>2016/0209128</doc-number>
<kind>A1</kind>
<name>Stieber</name>
<date>20160700</date>
</document-id>
</patcit>
<category>cited by examiner</category>
<classification-cpc-text>F28F 3/00</classification-cpc-text>
</us-citation>
<us-citation>
<patcit num="00024">
<document-id>
<country>EP</country>
<doc-number>0732743</doc-number>
<kind>A2</kind>
<date>19960900</date>
</document-id>
</patcit>
<category>cited by examiner</category>
<classification-cpc-text>F28D 20/02</classification-cpc-text>
</us-citation>
<us-citation>
<patcit num="00025">
<document-id>
<country>GB</country>
<doc-number>2474578</doc-number>
<kind>A</kind>
<date>20110400</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00026">
<document-id>
<country>WO</country>
<doc-number>2008/044256</doc-number>
<kind>A1</kind>
<date>20080400</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<patcit num="00027">
<document-id>
<country>WO</country>
<doc-number>2011/046940</doc-number>
<kind>A1</kind>
<date>20110400</date>
</document-id>
</patcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<nplcit num="00028">
<othercit>&#x201c;Pressure Loss and Heat Transfer through Heat Sinks produced by Selective Laser Melting&#x201d;&#x2014;Wong (pp. 1069-1070).</othercit>
</nplcit>
<category>cited by examiner</category>
</us-citation>
<us-citation>
<nplcit num="00029">
<othercit>&#x201c;3D Printing&#x201d;, Wikipedia, Oct. 28, 2015, 35 pages.</othercit>
</nplcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<nplcit num="00030">
<othercit>International Search Report and Written Opinion dated Apr. 30, 2015 in connection with International Application PCT/US2015/014045; 10 pages.</othercit>
</nplcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<nplcit num="00031">
<othercit>&#x201c;M982 Excalibur&#x201d;; retrieved from http://en.wikipedia.org/w/index.php?title=Excalibur&#x26;oldid=638243770; Dec. 15, 2014, 8 pages.</othercit>
</nplcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<nplcit num="00032">
<othercit>&#x201c;Extreme Accuracy Tasked Ordnance (EXACTO)&#x201d;; retrieved from http://www.darpa.mil/Our_Work/TTO/Programs/Extreme_Accuracy_Tasked_Ordnance_%28EXACTO%29.aspx; Jul. 2015, 2 pages.</othercit>
</nplcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<nplcit num="00033">
<othercit>&#x201c;EXACTO Demonstrates First-Ever Guided .50 Caliber Bullets&#x201d;; retrieved from http://www.darpa.mil/ NewsEvents/Releases/2014/07/10a.aspx; Jul. 10, 2014; 2 pages.</othercit>
</nplcit>
<category>cited by applicant</category>
</us-citation>
<us-citation>
<nplcit num="00034">
<othercit>&#x201c;Sandia's Self-Guided Bullet Prototype Can Hit Target a Mile Away&#x201d;; Sandia Labs News Release; Jan. 30, 2012; 3 pages.</othercit>
</nplcit>
<category>cited by applicant</category>
</us-citation>
</us-references-cited>
<number-of-claims>21</number-of-claims>
<us-exemplary-claim>1</us-exemplary-claim>
<us-field-of-classification-search>
<classification-cpc-text>H05K 7/2029</classification-cpc-text>
<classification-cpc-text>H05K 7/20309</classification-cpc-text>
<classification-cpc-text>H05K 7/20318</classification-cpc-text>
<classification-cpc-text>B23P 15/26</classification-cpc-text>
<classification-cpc-text>B23P 2700/10</classification-cpc-text>
<classification-cpc-text>B21D 53/02</classification-cpc-text>
<classification-cpc-text>B33Y 99/00</classification-cpc-text>
<classification-cpc-text>F28D 2021/0028</classification-cpc-text>
<classification-cpc-text>F28D 2021/0029</classification-cpc-text>
<classification-cpc-text>Y10T 29/49366</classification-cpc-text>
<classification-cpc-text>Y10T 29/49368</classification-cpc-text>
<classification-cpc-text>B29C 73/06</classification-cpc-text>
<classification-cpc-text>B29C 73/063</classification-cpc-text>
</us-field-of-classification-search>
<figures>
<number-of-drawing-sheets>4</number-of-drawing-sheets>
<number-of-figures>9</number-of-figures>
</figures>
<us-related-documents>
<related-publication>
<document-id>
<country>US</country>
<doc-number>20170127557</doc-number>
<kind>A1</kind>
<date>20170504</date>
</document-id>
</related-publication>
</us-related-documents>
<us-parties>
<us-applicants>
<us-applicant sequence="001" app-type="applicant" designation="us-only" applicant-authority-category="assignee">
<addressbook>
<orgname>Raytheon Company</orgname>
<address>
<city>Waltham</city>
<state>MA</state>
<country>US</country>
</address>
</addressbook>
<residence>
<country>US</country>
</residence>
</us-applicant>
</us-applicants>
<inventors>
<inventor sequence="001" designation="us-only">
<addressbook>
<last-name>Evans</last-name>
<first-name>Jeremy T.</first-name>
<address>
<city>Tucson</city>
<state>AZ</state>
<country>US</country>
</address>
</addressbook>
</inventor>
<inventor sequence="002" designation="us-only">
<addressbook>
<last-name>Wood</last-name>
<first-name>Adam C.</first-name>
<address>
<city>Oro Valley</city>
<state>AZ</state>
<country>US</country>
</address>
</addressbook>
</inventor>
<inventor sequence="003" designation="us-only">
<addressbook>
<last-name>Boyack</last-name>
<first-name>Chad E.</first-name>
<address>
<city>Tucson</city>
<state>AZ</state>
<country>US</country>
</address>
</addressbook>
</inventor>
<inventor sequence="004" designation="us-only">
<addressbook>
<last-name>Piekarski</last-name>
<first-name>Richard</first-name>
<address>
<city>Tucson</city>
<state>AZ</state>
<country>US</country>
</address>
</addressbook>
</inventor>
</inventors>
</us-parties>
<assignees>
<assignee>
<addressbook>
<orgname>Raytheon Company</orgname>
<role>02</role>
<address>
<city>Waltham</city>
<state>MA</state>
<country>US</country>
</address>
</addressbook>
</assignee>
</assignees>
<examiners>
<primary-examiner>
<last-name>Vaughan</last-name>
<first-name>Jason L</first-name>
<department>3726</department>
</primary-examiner>
<assistant-examiner>
<last-name>Meneghini</last-name>
<first-name>Amanda</first-name>
</assistant-examiner>
</examiners>
</us-bibliographic-data-grant>
<abstract id="abstract">
<p id="p-0001" num="0000">A heat sink is provided that includes a lower shell, an upper shell and an internal matrix. The lower shell, the upper shell and the internal matrix are formed as a single component using additive manufacturing techniques. The internal matrix includes a space that is configured to receive a phase change material.</p>
</abstract>
<drawings id="DRAWINGS">
<figure id="Fig-EMI-D00000" num="00000">
<img id="EMI-D00000" he="124.21mm" wi="158.75mm" file="US10123456-20181106-D00000.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00001" num="00001">
<img id="EMI-D00001" he="257.98mm" wi="201.42mm" orientation="landscape" file="US10123456-20181106-D00001.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00002" num="00002">
<img id="EMI-D00002" he="254.76mm" wi="177.04mm" file="US10123456-20181106-D00002.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00003" num="00003">
<img id="EMI-D00003" he="284.73mm" wi="197.53mm" file="US10123456-20181106-D00003.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00004" num="00004">
<img id="EMI-D00004" he="121.07mm" wi="133.94mm" file="US10123456-20181106-D00004.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
</drawings>
<description id="description">
<?BRFSUM description="Brief Summary" end="lead"?>
<heading id="h-0001" level="1">TECHNICAL FIELD</heading>
<p id="p-0002" num="0001">The present disclosure is directed, in general, to thermal technology and, more specifically, to a phase change material heat sink using additive manufacturing and method.</p>
<heading id="h-0002" level="1">BACKGROUND OF THE DISCLOSURE</heading>
<p id="p-0003" num="0002">Phase change material heat sinks are capable of increasing thermal capacitance per volume/mass as compared to typical metallic heat sinks. Containing the phase change material within a heat sink generally requires sealing that is accomplished by vacuum brazing two metal shells, in addition to brazing an internal metal matrix, such as aluminum foam. However, brazing operations are expensive and provide potential leak paths and fatigue failure points.</p>
<heading id="h-0003" level="1">SUMMARY OF THE DISCLOSURE</heading>
<p id="p-0004" num="0003">This disclosure provides a phase change material (PCM) heat sink using additive manufacturing and method.</p>
<p id="p-0005" num="0004">In one embodiment, a heat sink is provided that includes a lower shell, an upper shell and an internal matrix. The lower shell, the upper shell and the internal matrix are formed as a single component using additive manufacturing techniques. The internal matrix includes a space that is configured to receive a phase change material.</p>
<p id="p-0006" num="0005">In another embodiment, a PCM heat sink is provided that includes a phase change material, a lower shell, an upper shell and an internal matrix. The internal matrix includes a space that is configured to receive the phase change material. The lower shell, the upper shell and the internal matrix are formed as a single component using additive manufacturing techniques.</p>
<p id="p-0007" num="0006">In yet another embodiment, a method for forming a heat sink is provided. The method includes using additive manufacturing techniques to form a lower shell, an internal matrix and an upper shell of a heat sink. Thus, the lower shell, the upper shell and the internal matrix comprise a single-structure component.</p>
<p id="p-0008" num="0007">Other technical features may be readily apparent to one skilled in the art from the following figures, descriptions, and claims.</p>
<?BRFSUM description="Brief Summary" end="tail"?>
<?brief-description-of-drawings description="Brief Description of Drawings" end="lead"?>
<description-of-drawings>
<heading id="h-0004" level="1">BRIEF DESCRIPTION OF THE DRAWINGS</heading>
<p id="p-0009" num="0008">For a more complete understanding of the present disclosure, reference is now made to the following description taken in conjunction with the accompanying drawings, in which:</p>
<p id="p-0010" num="0009"><figref idref="DRAWINGS">FIG. 1</figref> illustrates an expanded view of a heat sink in accordance with the present disclosure;</p>
<p id="p-0011" num="0010"><figref idref="DRAWINGS">FIGS. 2A-C</figref> illustrate cross-sectional views of an example of the formation of a phase change material (PCM) heat sink in accordance with the present disclosure;</p>
<p id="p-0012" num="0011"><figref idref="DRAWINGS">FIGS. 3A-D</figref> illustrate examples of the internal matrix of <figref idref="DRAWINGS">FIGS. 2A-C</figref> in accordance with the present disclosure; and</p>
<p id="p-0013" num="0012"><figref idref="DRAWINGS">FIG. 4</figref> is a flowchart illustrating a method for forming the PCM heat sink of <figref idref="DRAWINGS">FIGS. 2A-C</figref> in accordance with the present disclosure.</p>
</description-of-drawings>
<?brief-description-of-drawings description="Brief Description of Drawings" end="tail"?>
<?DETDESC description="Detailed Description" end="lead"?>
<heading id="h-0005" level="1">DETAILED DESCRIPTION</heading>
<p id="p-0014" num="0013"><figref idref="DRAWINGS">FIGS. 1 through 4</figref>, discussed below, and the various embodiments used to describe the principles of the present disclosure in this patent document are by way of illustration only and should not be construed in any way to limit the scope of the disclosure. Those skilled in the art will understand that the principles of the present disclosure may be implemented using any number of techniques, whether currently known or not. Additionally, the drawings are not necessarily drawn to scale.</p>
<p id="p-0015" num="0014">As described above, containing a phase change material (PCM) within a heat sink generally requires sealing that is most effectively accomplished by creating a pressure vessel to contain the PCM. For example, paraffin wax is sealed in an aluminum container to form one type of PCM heat sink that typically uses vacuum brazing to prevent the paraffin wax from escaping the heat sink when it expands as a liquid. Vacuum brazing is performed at a limited number of facilities and typically has a multi-month lead time.</p>
<p id="p-0016" num="0015"><figref idref="DRAWINGS">FIG. 1</figref> illustrates an expanded view of a heat sink <b>100</b> in accordance with the present disclosure. The embodiment of the heat sink <b>100</b> shown in <figref idref="DRAWINGS">FIG. 1</figref> is for illustration only. Other embodiments of the heat sink <b>100</b> could be used without departing from the scope of this disclosure.</p>
<p id="p-0017" num="0016">The heat sink <b>100</b> comprises a lower shell <b>102</b>, an upper shell <b>104</b> and an internal matrix <b>106</b>. As described in more detail below, a phase change material (not shown in <figref idref="DRAWINGS">FIG. 1</figref>) is incorporated into the heat sink <b>100</b> to generate a phase change material (PCM) heat sink. The heat sink <b>100</b> may comprise aluminum or any other suitable thermally-conductive material. Although illustrated as circular, it will be understood that the heat sink <b>100</b> may comprise any suitable shape, such as oval, rectangular, triangular, configured to be adjacent to a printed circuit board or the like. In addition, the heat sink <b>100</b> may be designed into the structure of any suitable component, eliminating the need to physically attach the heat sink <b>100</b> to a component requiring thermal regulation.</p>
<p id="p-0018" num="0017">As described in more detail below, the internal matrix <b>106</b> comprises open space that is configured to accommodate the phase change material. The internal matrix <b>106</b> may comprise any suitable form, such as straight, slanted, spiral, zigzag, foam or the like, that includes open space for receiving the phase change material. The internal matrix <b>106</b> is configured to conduct thermal energy into the phase change material within the space of the internal matrix <b>106</b>.</p>
<p id="p-0019" num="0018">In conventional PCM heat sinks, the lower shell and the upper shell (and often the internal matrix also) are distinct components that are sealed together using vacuum brazing. However, the heat sink <b>100</b> of the present disclosure includes the lower shell <b>102</b>, the upper shell <b>104</b> and the internal matrix <b>106</b> integrated together as a single component that is generated using additive manufacturing.</p>
<p id="p-0020" num="0019">As a result, the heat sink <b>100</b> is less expensive to produce and more robust than conventional heat sinks. Additive manufacturing also allows for the possibility to generate the lower and upper shells <b>102</b> and <b>104</b>, as well as the internal matrix <b>106</b>, with more complex designs to address specific issues such as dissipating heat from high power density components. Thus, the design of the internal matrix <b>106</b> is not limited to a metal foam or other design that can be formed using traditional machining techniques. For example, a complex internal matrix <b>106</b> may be designed to optimize heat transport, maximize volume allocated for phase change material, and provide suitable PCM filling paths. This design may be customized to provide the most efficient removal of heat from a particular application and to optimize heat transfer into the phase change material.</p>
<p id="p-0021" num="0020">In addition, because the internal matrix <b>106</b> is formed together with the shells <b>102</b> and <b>104</b>, good contact with the shells <b>102</b> and <b>104</b> is inherently designed into the heat sink <b>100</b>. Finally, instead of being formed separately and later attached to a component, the heat sink <b>100</b> may be incorporated into the design of any suitable structural component, thereby increasing heat capacity for the structural component. For example, the structural component may include an airframe, bulkhead or any other suitable component that may be formed using additive manufacturing techniques.</p>
<p id="p-0022" num="0021">Although <figref idref="DRAWINGS">FIG. 1</figref> illustrates one example of a heat sink <b>100</b>, various changes may be made to the embodiment shown in <figref idref="DRAWINGS">FIG. 1</figref>. For example, the makeup and arrangement of the heat sink <b>100</b> are for illustration only. Components could be added, omitted, combined, subdivided, or placed in any other suitable configuration according to particular needs.</p>
<p id="p-0023" num="0022"><figref idref="DRAWINGS">FIGS. 2A-C</figref> illustrate cross-sectional views of an example of the formation of a PCM heat sink <b>120</b> in accordance with the present disclosure. As shown in <figref idref="DRAWINGS">FIG. 2A</figref>, the lower shell <b>102</b>, the upper shell <b>104</b> and the internal matrix <b>106</b> are formed together as a single-structure heat sink <b>100</b> using additive manufacturing techniques. The heat sink <b>100</b> also includes a fill port <b>108</b> and a vent port <b>110</b> to enable the insertion of a phase change material into open space <b>112</b> formed in the structure of the internal matrix <b>106</b>.</p>
<p id="p-0024" num="0023">It will be understood that the shapes of the shells <b>102</b> and <b>104</b> and the internal matrix <b>106</b> may include any suitable shapes and that the embodiment of the heat sink <b>100</b> shown in <figref idref="DRAWINGS">FIGS. 2A-C</figref> is for illustration only. Other embodiments of the heat sink <b>100</b> could be used without departing from the scope of this disclosure.</p>
<p id="p-0025" num="0024">As shown in <figref idref="DRAWINGS">FIG. 2B</figref>, a phase change material <b>114</b> is introduced through the fill port <b>108</b> so as to substantially fill the space <b>112</b> within the internal matrix <b>106</b>. The phase change material <b>114</b> may comprise a paraffin wax or other suitable material that absorbs thermal energy when changing from a solid state to a liquid state and releases thermal energy when changing from a liquid state to a solid state. Thus, the phase change material <b>114</b> is configured to store and release heat or thermal energy via the phase changes of the phase change material <b>114</b>.</p>
<p id="p-0026" num="0025">The structure of the internal matrix <b>106</b> is configured to conduct heat or thermal energy between the phase change material <b>114</b> and one or both of the shells <b>102</b> and <b>104</b>. The size, spacing and geometry of the internal matrix <b>106</b> structure may be selected based on any suitable criteria, such as the thermal requirements of the application in which the PCM heat sink <b>120</b> is to be implemented. In addition, the internal matrix <b>106</b> may have any type of three-dimensional, non-symmetric and/or non-matrix design because of the additive manufacturing techniques used to form the heat sink <b>100</b>.</p>
<p id="p-0027" num="0026">As shown in <figref idref="DRAWINGS">FIG. 2C</figref>, seal plugs <b>116</b><i>a </i>and <b>116</b><i>b </i>are used to seal the ports <b>108</b> and <b>110</b>, thus completing the formation of the PCM heat sink <b>120</b>. The seal plugs <b>116</b><i>a</i>-<i>b </i>may include any suitable structure and may be inserted by any suitable process so as to seal the ports <b>108</b> and <b>110</b>, thereby preventing the phase change material <b>114</b> from leaking out of the PCM heat sink <b>120</b>. For example, for a particular embodiment, the seal plugs <b>116</b><i>a</i>-<i>b </i>may include expansion plugs. For another embodiment, the seal plugs <b>116</b><i>a</i>-<i>b </i>may include solder.</p>
<p id="p-0028" num="0027">By forming the PCM heat sink <b>120</b> from a single-structure heat sink <b>100</b> generated using additive manufacturing techniques, the need for vacuum brazing is eliminated. As a result, the process to form the heat sink <b>100</b> and, thus, the PCM heat sink <b>120</b>, is significantly less expensive and faster to fabricate. In addition, the robustness of the PCM heat sink <b>120</b> is increased as compared to conventionally manufactured PCM heat sinks, and complex designs may be easily implemented. Furthermore, the lower shell <b>102</b>, the upper shell <b>104</b> and/or the internal matrix <b>106</b> may each include customizable, complex designs that are not possible with traditional machining techniques. This PCM heat sink <b>120</b> may be included in test hardware, commercial electronics or any other suitable application in which thermal energy needs to be managed.</p>
<p id="p-0029" num="0028">Although <figref idref="DRAWINGS">FIGS. 2A-C</figref> illustrate one example of the formation of a PCM heat sink <b>120</b>, various changes may be made to the embodiment shown in <figref idref="DRAWINGS">FIGS. 2A-C</figref>. For example, the makeup and arrangement of the PCM heat sink <b>120</b> are for illustration only. Components could be added, omitted, combined, subdivided, or placed in any other suitable configuration according to particular needs.</p>
<p id="p-0030" num="0029"><figref idref="DRAWINGS">FIGS. 3A-D</figref> illustrate examples of the internal matrix <b>106</b> in accordance with the present disclosure. The examples of the internal matrix <b>106</b> shown in <figref idref="DRAWINGS">FIGS. 3A-D</figref> are for illustration only. Other embodiments of the internal matrix <b>106</b> could be used without departing from the scope of this disclosure. For these examples, the internal matrix <b>106</b> comprises a thermally-conductive material <b>302</b>, represented by dark areas, and a space <b>304</b>, represented by white areas. In addition, the internal matrix <b>106</b> is illustrated in a top view.</p>
<p id="p-0031" num="0030">The thermally-conductive material <b>302</b> includes the same material as the lower and upper shells <b>102</b> and <b>104</b> of the heat sink <b>100</b> due to the additive manufacturing techniques used to form the heat sink <b>100</b> as a single structure, as described above. Because the internal matrix <b>106</b> is manufactured using additive manufacturing techniques, the thermally-conductive material <b>302</b> may be formed in any suitable configuration and is not limited to geometries that can be formed with traditional machining techniques.</p>
<p id="p-0032" num="0031">For the example shown in <figref idref="DRAWINGS">FIG. 3A</figref>, the thermally-conductive material <b>302</b> is configured as a plurality of pins. The space <b>304</b> comprises an open area formed by the pins. Although illustrated as square, it will be understood that the pins may alternatively be circular or any other suitable shape. For the example shown in <figref idref="DRAWINGS">FIG. 3B</figref>, the thermally-conductive material <b>302</b> is configured as a plurality of plates. The space <b>304</b> comprises an open area formed between the plates. Although illustrated as straight, it will be understood that the plates may alternatively be slanted, zigzag, or any other suitable shape. For the example shown in <figref idref="DRAWINGS">FIG. 3C</figref>, the thermally-conductive material <b>302</b> is configured as a grid. The space <b>304</b> comprises an open area formed by the grid. Although illustrated as a square grid, it will be understood that the grid may alternatively be formed in any other suitable shape. For the example shown in <figref idref="DRAWINGS">FIG. 3D</figref>, the thermally-conductive material <b>302</b> is configured in a non-standard shape to illustrate that the internal matrix <b>106</b> may have a complex, customized design that is tailored to meet the needs of a particular application. The space <b>304</b> in this example comprises an open area formed by the thermally-conductive material <b>302</b>.</p>
<p id="p-0033" num="0032">The geometry of the thermally-conductive material <b>302</b> may be as complex as desired and is not limited to the relatively simple shapes illustrated in <figref idref="DRAWINGS">FIGS. 3A-D</figref>. For example, the cross-section of any portion of the thermally-conductive material <b>302</b>, such as pins or plates, may be constant or varying due to the additive manufacturing techniques. As a particular example, an hour-glass shaped pin or plate could be implemented. Alternatively, each pin or plate could be designed independently, with each having any desired shape. Thus, the thermally-conductive material <b>302</b> may include any suitable simple or complex three-dimensional shape, including curvatures that are not possible with traditional machining techniques. In addition, for some embodiments, localized holes (not shown in <figref idref="DRAWINGS">FIGS. 3A-D</figref>) may be included in the thermally-conductive material <b>302</b> to allow the phase change material to be introduced into substantially the entire open space <b>304</b> when the thermally-conductive material <b>302</b> would otherwise block its path, which may be difficult or impossible to achieve with traditional machining techniques.</p>
<p id="p-0034" num="0033"><figref idref="DRAWINGS">FIG. 4</figref> is a flowchart illustrating a method <b>400</b> for forming the PCM heat sink <b>120</b> in accordance with the present disclosure. The method <b>400</b> shown in <figref idref="DRAWINGS">FIG. 4</figref> is for illustration only. The PCM heat sink <b>120</b> may be formed in any other suitable manner without departing from the scope of this disclosure.</p>
<p id="p-0035" num="0034">Initially, a single-structure heat sink <b>100</b> is formed using additive manufacturing techniques (step <b>402</b>). For a particular example, for some embodiments, a lower shell <b>102</b>, an upper shell <b>104</b> and an internal matrix <b>106</b> are formed as a single component. The heat sink <b>100</b> may comprise aluminum or other suitable material.</p>
<p id="p-0036" num="0035">A phase change material <b>114</b> is inserted via a fill port <b>108</b> of the heat sink <b>100</b> (step <b>404</b>). For a particular example, for some embodiments, the phase change material <b>114</b> is inserted such that open space <b>304</b> within the internal matrix <b>106</b> is substantially filled with the phase change material <b>114</b>. The phase change material <b>114</b> may comprise a paraffin wax or other suitable material.</p>
<p id="p-0037" num="0036">The fill port <b>108</b> and a vent port <b>110</b> of the heat sink <b>100</b> are sealed to complete formation of the PCM heat sink <b>120</b> (step <b>406</b>). The fill port <b>108</b> and the vent port <b>110</b> may be sealed using expansion plugs or other suitable method, such as soldering.</p>
<p id="p-0038" num="0037">As a result, the PCM heat sink <b>120</b> may be formed using a process that is significantly less expensive and faster as compared to conventional PCM heat sinks while providing the benefit of increased robustness. In addition, the heat sink <b>100</b> itself may be designed to optimize heat transport, maximize volume allocated for phase change material <b>114</b>, and provide suitable PCM filling paths due to the use of additive manufacturing techniques in the formation of the heat sink <b>100</b>.</p>
<p id="p-0039" num="0038">Although <figref idref="DRAWINGS">FIG. 4</figref> illustrates one example of a method <b>400</b> for forming the PCM heat sink <b>120</b>, various changes may be made to the embodiment shown in <figref idref="DRAWINGS">FIG. 4</figref>. For example, while shown as a series of steps, various steps in <figref idref="DRAWINGS">FIG. 4</figref> could overlap, occur in parallel, occur in a different order, or occur multiple times.</p>
<p id="p-0040" num="0039">Modifications, additions, or omissions may be made to the apparatuses, and methods described herein without departing from the scope of the disclosure. For example, the components of the apparatuses may be integrated or separated. The methods may include more, fewer, or other steps. Additionally, as described above, steps may be performed in any suitable order.</p>
<p id="p-0041" num="0040">It may be advantageous to set forth definitions of certain words and phrases used throughout this patent document. The term &#x201c;couple&#x201d; and its derivatives refer to any direct or indirect communication between two or more elements, whether or not those elements are in physical contact with one another. The terms &#x201c;include&#x201d; and &#x201c;comprise,&#x201d; as well as derivatives thereof, mean inclusion without limitation. The term &#x201c;or&#x201d; is inclusive, meaning and/or. The term &#x201c;each&#x201d; refers to each member of a set or each member of a subset of a set. Terms such as &#x201c;over&#x201d; and &#x201c;under&#x201d; may refer to relative positions in the figures and do not denote required orientations during manufacturing or use. Terms such as &#x201c;higher&#x201d; and &#x201c;lower&#x201d; denote relative values and are not meant to imply specific values or ranges of values. The phrases &#x201c;associated with&#x201d; and &#x201c;associated therewith,&#x201d; as well as derivatives thereof, may mean to include, be included within, interconnect with, contain, be contained within, connect to or with, couple to or with, be communicable with, cooperate with, interleave, juxtapose, be proximate to, be bound to or with, have, have a property of, or the like.</p>
<p id="p-0042" num="0041">While this disclosure has described certain embodiments and generally associated methods, alterations and permutations of these embodiments and methods will be apparent to those skilled in the art. Accordingly, the above description of example embodiments does not define or constrain this disclosure. Other changes, substitutions, and alterations are also possible without departing from the spirit and scope of this disclosure, as defined by the following claims.</p>
<?DETDESC description="Detailed Description" end="tail"?>
</description>
<us-claim-statement>What is claimed is:</us-claim-statement>
<claims id="claims">
<claim id="CLM-00001" num="00001">
<claim-text>1. A method comprising:
<claim-text>using additive manufacturing techniques:
<claim-text>forming a structural component;</claim-text>
<claim-text>forming a lower shell of a heat sink;</claim-text>
<claim-text>forming an internal matrix of the heat sink, the internal matrix comprising a plurality of parallel pins arranged in a grid pattern; and</claim-text>
<claim-text>forming an upper shell of the heat sink,</claim-text>
<claim-text>wherein the lower shell, the internal matrix, and the upper shell of the heat sink comprise a single-structure component that is incorporated into the structural component, such that the heat sink and the structural component are integral.</claim-text>
</claim-text>
</claim-text>
</claim>
<claim id="CLM-00002" num="00002">
<claim-text>2. The method of <claim-ref idref="CLM-00001">claim 1</claim-ref>, further comprising, using additive manufacturing techniques, forming a fill port and a vent port in the upper shell of the heat sink.</claim-text>
</claim>
<claim id="CLM-00003" num="00003">
<claim-text>3. The method of <claim-ref idref="CLM-00002">claim 2</claim-ref>, further comprising inserting a phase change material into the heat sink via the fill port.</claim-text>
</claim>
<claim id="CLM-00004" num="00004">
<claim-text>4. The method of <claim-ref idref="CLM-00003">claim 3</claim-ref>, wherein the phase change material comprises a paraffin wax, and wherein the lower shell, the internal matrix and the upper shell comprise a thermally-conductive material.</claim-text>
</claim>
<claim id="CLM-00005" num="00005">
<claim-text>5. The method of <claim-ref idref="CLM-00003">claim 3</claim-ref>, wherein the internal matrix further comprises a space, wherein inserting the phase change material comprises substantially filling the space of the internal matrix with the phase change material, and wherein fon ling the internal matrix comprises forming the internal matrix to optimize heat transfer into the phase change material.</claim-text>
</claim>
<claim id="CLM-00006" num="00006">
<claim-text>6. The method of <claim-ref idref="CLM-00003">claim 3</claim-ref>, further comprising sealing the fill port and the vent port with seal plugs to form a phase change material heat sink.</claim-text>
</claim>
<claim id="CLM-00007" num="00007">
<claim-text>7. The method of <claim-ref idref="CLM-00006">claim 6</claim-ref>, wherein the seal plugs comprise expansion plugs.</claim-text>
</claim>
<claim id="CLM-00008" num="00008">
<claim-text>8. The method of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the plurality of parallel pins comprise hour-glass shaped pins.</claim-text>
</claim>
<claim id="CLM-00009" num="00009">
<claim-text>9. The method of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the structural component comprises an airframe or a bulkhead.</claim-text>
</claim>
<claim id="CLM-00010" num="00010">
<claim-text>10. A method comprising:
<claim-text>using additive manufacturing techniques:
<claim-text>forming a structural component;</claim-text>
<claim-text>forming a lower shell of a heat sink;</claim-text>
<claim-text>forming an internal matrix of the heat sink, the internal matrix comprising a plurality of parallel plates; and</claim-text>
<claim-text>forming an upper shell of the heat sink,</claim-text>
<claim-text>wherein the lower shell, the internal matrix, and the upper shell of the heat sink comprise a single-structure component that is incorporated into the structural component, such that the heat sink and the structural component are integral.</claim-text>
</claim-text>
</claim-text>
</claim>
<claim id="CLM-00011" num="00011">
<claim-text>11. The method of <claim-ref idref="CLM-00010">claim 10</claim-ref>, further comprising, using additive manufacturing techniques, forming a fill port and a vent port in the upper shell of the heat sink.</claim-text>
</claim>
<claim id="CLM-00012" num="00012">
<claim-text>12. The method of <claim-ref idref="CLM-00011">claim 11</claim-ref>, further comprising inserting a phase change material into the heat sink via the fill port.</claim-text>
</claim>
<claim id="CLM-00013" num="00013">
<claim-text>13. The method of <claim-ref idref="CLM-00012">claim 12</claim-ref>, wherein the phase change material comprises a paraffin wax, and wherein the lower shell, the internal matrix and the upper shell comprise a thermally-conductive material.</claim-text>
</claim>
<claim id="CLM-00014" num="00014">
<claim-text>14. The method of <claim-ref idref="CLM-00012">claim 12</claim-ref>, wherein the internal matrix further comprises a space, wherein inserting the phase change material comprises substantially filling the space of the internal matrix with the phase change material, and wherein forming the internal matrix comprises forming the internal matrix to optimize heat transfer into the phase change material.</claim-text>
</claim>
<claim id="CLM-00015" num="00015">
<claim-text>15. The method of <claim-ref idref="CLM-00012">claim 12</claim-ref>, wherein the internal matrix further comprises a second plurality of parallel plates perpendicular to the pluralityof parallel plates.</claim-text>
</claim>
<claim id="CLM-00016" num="00016">
<claim-text>16. The method of <claim-ref idref="CLM-00012">claim 12</claim-ref>, further comprising sealing the fill port and the vent port with seal plugs to form a phase change material heat sink.</claim-text>
</claim>
<claim id="CLM-00017" num="00017">
<claim-text>17. The method of <claim-ref idref="CLM-00016">claim 16</claim-ref>, wherein the seal plugs comprise expansion plugs.</claim-text>
</claim>
<claim id="CLM-00018" num="00018">
<claim-text>18. A method comprising:
<claim-text>forming a structural component, a lower shell of a heat sink, an internal matrix of the heat sink, and an upper shell of the heat sink using additive manufacturing techniques, wherein the lower shell, the internal matrix, and the upper shell of the heat sink comprise a single-structure component that is incorporated into the structural component, such that the heat sink and the structural component are integral, wherein the internal matrix comprises a plurality of parallel plates or a plurality of parallel pins;</claim-text>
<claim-text>using additive manufacturing techniques, forming a fill port and a vent port in the upper shell of the heat sink;</claim-text>
<claim-text>inserting a phase change material into the heat sink via the fill port; and</claim-text>
<claim-text>sealing the fill port and the vent port with seal plugs.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00019" num="00019">
<claim-text>19. The method of <claim-ref idref="CLM-00018">claim 18</claim-ref>, wherein the seal plugs comprise expansion plugs.</claim-text>
</claim>
<claim id="CLM-00020" num="00020">
<claim-text>20. The method of <claim-ref idref="CLM-00018">claim 18</claim-ref>, wherein the phase change material comprises a paraffin wax, and wherein the lower shell, the internal matrix and the upper shell comprise a thermally-conductive material.</claim-text>
</claim>
<claim id="CLM-00021" num="00021">
<claim-text>21. The method of <claim-ref idref="CLM-00018">claim 18</claim-ref>, wherein the internal matrix further comprises a space, wherein inserting the phase change material comprises substantially filling the space of the internal matrix with the phase change material, and wherein for ling the internal matrix comprises foaming the internal matrix to optimize heat transfer into the phase change material.</claim-text>
</claim>
</claims>
# </us-patent-grant>"""  # Replace with actual XML content
patent = USPatentContent(xml_content)
structured_data = patent.get_data()
x = 0
#
# import json
#
# print(json.dumps(structured_data, indent=4))
#
# # Instantiate the USPatentContent class with XML content
# patent = USPatentContent(xml_content)
#
# # Retrieve the full text data
# full_text = patent.get_full_text()
#
# # Print the full formatted text
# print(full_text["to_string"]())
# # Instantiate the class
# patent = USPatentContent(xml_content)
#
# # Extract and print figure details
# figures = patent.get_figures()
# print(figures)
#
# # Display the first figure if the image file exists locally
# if figures:
#     image_path = figures[0]["image_file"]  # Assuming the TIFF file is available
#     patent.display_figure(image_path)
#
