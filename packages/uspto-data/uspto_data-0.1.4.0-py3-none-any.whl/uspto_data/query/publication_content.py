import os
import xml.etree.ElementTree as ET

from uspto_data.query.common import get_dependencies_from_xml


class USPublicationContent:
    """Class to parse and store structured U.S. Patent Grant XML content, ensuring inline XML elements are processed correctly."""

    def __init__(self, xml_content):
        self.xml = xml_content
        self.tree = ET.ElementTree(ET.fromstring(xml_content.strip()))
        self.root = self.tree.getroot()
        self.data = {}
        self.parse_data()

    def extract_text_with_inline_elements(self, element):
        """Extracts text from an XML element while preserving inline components like <figref>, <b>, <i>."""
        text_parts = []

        if element.text:
            text_parts.append(element.text.strip())

        for child in element:
            try:
                if child.text and (stripped_text := child.text.strip()):
                    if child.tag == "figref":  # Handle Figure References
                        text_parts.append(f"[Figure: {stripped_text}]")  # Convert to structured text
                    elif child.tag == "b":  # Handle Bold Text
                        text_parts.append(f"**{stripped_text}**")  # Markdown-style bold
                    elif child.tag == "i":  # Handle Italic Text
                        text_parts.append(f"*{stripped_text}*")
                    else:
                        text_parts.append(stripped_text.strip())
                else:
                    text_parts.append("")
                if child.tail:
                    text_parts.append(child.tail.strip())
            except:
                pass

        return " ".join(text_parts).strip()

    def parse_data(self):
        """Extract key patent data based on U.S. Patent XML v4.5 documentation."""

        bib_data = self.root.find("us-bibliographic-data-application")
        if bib_data is None:
            return

        # **Title**
        self.data["title"] = self.get_text_from_xml(bib_data, "invention-title")

        # **Abstract**
        abstract = self.root.find("abstract")
        self.data["abstract"] = " ".join(
            [self.extract_text_with_inline_elements(p) for p in abstract.findall("p")]
        ) if abstract is not None else None

        # **Claims**
        claims = self.root.findall("claims/claim")

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

    def parse_description(self):
        """Parse the description section of the patent XML."""
        try:
            description_data = {}
            description_element = self.root.find("description")
            if description_element is None:
                return None
                
            drawing_description_element = description_element.find("description-of-drawings")
            
            # Create lists for iteration, handling None values
            description_items = list(description_element) if description_element is not None else []
            drawing_items = list(drawing_description_element) if drawing_description_element is not None else []
            
            current_section = None
            description_data["sections"] = []

            for elem in description_items + drawing_items:
                if elem.tag == "":
                    elem = elem.find("heading")
                if elem.tag == "heading" and elem.text:
                    # If a new heading appears, create a new section
                    current_section = {"title": elem.text.strip(), "paragraphs": []}
                    description_data["sections"].append(current_section)

                elif elem.tag == "p":
                    paragraph_text = self.extract_text_with_inline_elements(elem)
                    paragraph_num = elem.get("num", "Unknown")

                    if current_section:
                        current_section["paragraphs"].append({"number": paragraph_num, "text": paragraph_text})
                    else:
                        # If no heading was found before, store as general paragraph (rare case)
                        description_data["sections"].append({
                            "title": "General",
                            "paragraphs": [{"number": paragraph_num, "text": paragraph_text}]
                        })
        except Exception as e:
            return None

        return description_data

    def get_text_from_xml(self, element, path):
        """Helper function to retrieve text from an XML element, ensuring it handles missing elements."""
        if element is None:
            return None
        elem = element.find(path)
        return elem.text.strip() if elem is not None and elem.text else None

    def get_title(self):
        """Retrieve the title of the patent."""
        return self.data.get("title", "")

    def get_claims(self):
        """Retrieve structured list of claims with their numbers."""
        return self.data.get("claims", [])

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
                if img is not None:
                    figures.append({
                        "figure_number": figure.get("num"),
                        "image_file": img.get("file"),
                        "width": img.get("wi"),
                        "height": img.get("he"),
                        "format": img.get("img-format"),
                        "content_type": img.get("img-content"),
                        "description": img.get("alt", "No description available"),
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
            if full_text_data["abstract"]:
                text_representation.append("=== ABSTRACT ===\n" + full_text_data["abstract"] + "\n")

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



xml_content = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE us-patent-application SYSTEM "us-patent-application-v44-2014-04-03.dtd" [ ]>
<us-patent-application lang="EN" dtd-version="v4.4 2014-04-03" file="US20150151444A1-20150604.XML" status="PRODUCTION" id="us-patent-application" country="US" date-produced="20150520" date-publ="20150604">
<us-bibliographic-data-application lang="EN" country="US">
<publication-reference>
<document-id>
<country>US</country>
<doc-number>20150151444</doc-number>
<kind>A1</kind>
<date>20150604</date>
</document-id>
</publication-reference>
<application-reference appl-type="utility">
<document-id>
<country>US</country>
<doc-number>14612898</doc-number>
<date>20150203</date>
</document-id>
</application-reference>
<us-application-series-code>14</us-application-series-code>
<classifications-ipcr>
<classification-ipcr>
<ipc-version-indicator><date>20060101</date></ipc-version-indicator>
<classification-level>A</classification-level>
<section>B</section>
<class>26</class>
<subclass>D</subclass>
<main-group>1</main-group>
<subgroup>30</subgroup>
<symbol-position>F</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
</classification-ipcr>
<classification-ipcr>
<ipc-version-indicator><date>20060101</date></ipc-version-indicator>
<classification-level>A</classification-level>
<section>B</section>
<class>26</class>
<subclass>D</subclass>
<main-group>5</main-group>
<subgroup>16</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
</classification-ipcr>
<classification-ipcr>
<ipc-version-indicator><date>20060101</date></ipc-version-indicator>
<classification-level>A</classification-level>
<section>B</section>
<class>26</class>
<subclass>D</subclass>
<main-group>7</main-group>
<subgroup>04</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
</classification-ipcr>
<classification-ipcr>
<ipc-version-indicator><date>20060101</date></ipc-version-indicator>
<classification-level>A</classification-level>
<section>B</section>
<class>26</class>
<subclass>D</subclass>
<main-group>5</main-group>
<subgroup>10</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
</classification-ipcr>
</classifications-ipcr>
<classifications-cpc>
<main-cpc>
<classification-cpc>
<cpc-version-indicator><date>20130101</date></cpc-version-indicator>
<section>B</section>
<class>26</class>
<subclass>D</subclass>
<main-group>1</main-group>
<subgroup>305</subgroup>
<symbol-position>F</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
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
<class>26</class>
<subclass>D</subclass>
<main-group>5</main-group>
<subgroup>10</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
<scheme-origination-code>C</scheme-origination-code>
</classification-cpc>
<classification-cpc>
<cpc-version-indicator><date>20130101</date></cpc-version-indicator>
<section>B</section>
<class>26</class>
<subclass>D</subclass>
<main-group>5</main-group>
<subgroup>16</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
<scheme-origination-code>C</scheme-origination-code>
</classification-cpc>
<classification-cpc>
<cpc-version-indicator><date>20130101</date></cpc-version-indicator>
<section>B</section>
<class>26</class>
<subclass>D</subclass>
<main-group>7</main-group>
<subgroup>04</subgroup>
<symbol-position>L</symbol-position>
<classification-value>I</classification-value>
<action-date><date>20150604</date></action-date>
<generating-office><country>US</country></generating-office>
<classification-status>B</classification-status>
<classification-data-source>H</classification-data-source>
<scheme-origination-code>C</scheme-origination-code>
</classification-cpc>
</further-cpc>
</classifications-cpc>
<invention-title id="d0e43">CUTTING TOOL</invention-title>
<us-related-documents>
<continuation>
<relation>
<parent-doc>
<document-id>
<country>US</country>
<doc-number>12987585</doc-number>
<date>20110110</date>
</document-id>
<parent-status>PENDING</parent-status>
</parent-doc>
<child-doc>
<document-id>
<country>US</country>
<doc-number>14612898</doc-number>
</document-id>
</child-doc>
</relation>
</continuation>
</us-related-documents>
<us-parties>
<us-applicants>
<us-applicant sequence="00" app-type="applicant" designation="us-only">
<addressbook>
<last-name>ZHANG</last-name>
<first-name>Charlie</first-name>
<address>
<city>Oak Brook</city>
<state>IL</state>
<country>US</country>
</address>
</addressbook>
<residence>
<country>US</country>
</residence>
</us-applicant>
</us-applicants>
<inventors>
<inventor sequence="00" designation="us-only">
<addressbook>
<last-name>ZHANG</last-name>
<first-name>Charlie</first-name>
<address>
<city>Oak Brook</city>
<state>IL</state>
<country>US</country>
</address>
</addressbook>
</inventor>
</inventors>
</us-parties>
<assignees>
<assignee>
<addressbook>
<orgname>D-Cut Products, Inc.</orgname>
<role>02</role>
<address>
<city>Oak Brook</city>
<state>IL</state>
<country>US</country>
</address>
</addressbook>
</assignee>
</assignees>
</us-bibliographic-data-application>
<abstract id="abstract">
<p id="p-0001" num="0000">A portable, non-power operated cutting tool for cutting sheets of building materials in a straight fashion without splintering or cracking. The cutting tool includes a base, a blade holder with a blade, a handle with an eccentric cam rotatably connected to the base, and a support arm to hold the building material against the base, where the blade holder moves between an open position and a closed position by rotating the eccentric cam.</p>
</abstract>
<drawings id="DRAWINGS">
<figure id="Fig-EMI-D00000" num="00000">
<img id="EMI-D00000" he="204.47mm" wi="137.50mm" file="US20150151444A1-20150604-D00000.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00001" num="00001">
<img id="EMI-D00001" he="217.93mm" wi="137.58mm" file="US20150151444A1-20150604-D00001.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00002" num="00002">
<img id="EMI-D00002" he="212.51mm" wi="138.26mm" file="US20150151444A1-20150604-D00002.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00003" num="00003">
<img id="EMI-D00003" he="200.91mm" wi="177.04mm" file="US20150151444A1-20150604-D00003.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00004" num="00004">
<img id="EMI-D00004" he="127.34mm" wi="176.36mm" file="US20150151444A1-20150604-D00004.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00005" num="00005">
<img id="EMI-D00005" he="122.60mm" wi="175.68mm" file="US20150151444A1-20150604-D00005.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
<figure id="Fig-EMI-D00006" num="00006">
<img id="EMI-D00006" he="143.68mm" wi="158.67mm" file="US20150151444A1-20150604-D00006.TIF" alt="embedded image" img-content="drawing" img-format="tif"/>
</figure>
</drawings>
<description id="description">
<?cross-reference-to-related-applications description="Cross Reference To Related Applications" end="lead"?>
<heading id="h-0001" level="1">CROSS REFERENCE TO RELATED APPLICATION</heading>
<p id="p-0002" num="0001">This application is a continuation of U.S. patent application Ser. No. 12/987,585, filed on 10 Jan. 2011, which claims the benefit of U.S. Provisional Application Ser. No. 61/295,250, filed on 15 Jan. 2010. The co-pending parent application is hereby incorporated by reference herein in its entirety and is made a part hereof, including but not limited to those portions which specifically appear hereinafter.</p>
<?cross-reference-to-related-applications description="Cross Reference To Related Applications" end="tail"?>
<?summary-of-invention description="Summary of Invention" end="lead"?>
<heading id="h-0002" level="1">BACKGROUND OF THE INVENTION</heading>
<p id="p-0003" num="0002">1. Field of the Invention</p>
<p id="p-0004" num="0003">This invention relates to a cutting tool for cutting sheets of material, such as, for example, sheets of building materials. More specifically, this invention relates to a cutting tool including a base, a blade holder with a blade pivotally connected to the base, and a handle with an eccentric cam rotatably connected to the base, where the blade holder moves between an open position and a closed position by rotating the eccentric cam.</p>
<p id="p-0005" num="0004">2. Discussion of Related Art</p>
<p id="p-0006" num="0005">Certain building materials, such as, for example, flooring materials and siding, are provided as sheets or planks of various dimensions. When used on a job site, the sheets or planks must be customized to meet the specific requirements of the job site. For example, the sheets or planks must be cut to fit around edges or corners of a room and/or around fixtures. Various tools are currently used to cut sheets of building materials, but most are bulky, heavy, require power to be operated, produce large amounts of dust during the cutting process, and/or result in uneven or splintered cuts.</p>
<p id="p-0007" num="0006">There is a need or a desire for an improved cutting tool for cutting sheets or planks of building materials. There is a need or a desire for a portable, non-power operated cutting tool able to cut sheets of building materials in a predictable and straight fashion without splintering, cracking or similar problems and providing fast, dust-free cutting.</p>
<heading id="h-0003" level="1">SUMMARY OF THE INVENTION</heading>
<p id="p-0008" num="0007">The present invention provides a portable, non-power operated cutting tool for cutting sheets of building materials in a straight fashion without splintering or cracking.</p>
<p id="p-0009" num="0008">According to one embodiment of this invention, the cutting tool includes a base with a support surface, a blade holder with a blade, and an eccentric cam with a handle.</p>
<p id="p-0010" num="0009">The blade holder includes a fixed end that is hingely connected to the base at a blade holder pivot point and a free end opposite the fixed end. The eccentric cam is positioned over the free end of the blade holder and is rotatably connected to the base at a cam pivot point. In a preferred embodiment, the blade holder pivot point is spaced from the cam pivot point at a distance sufficient to allow the material to be cut to fit between.</p>
<p id="p-0011" num="0010">In operation, the blade holder is movable from an open position to a closed position by rotating the eccentric cam. In the open position, the blade holder is in contact with the eccentric cam at a relatively small radius of the cam. In this position, a material to be cut can be placed in an opening provided between the blade and a portion of the base, preferably a blade stop. To cut the material, the handle is lowered to rotate the eccentric cam. As the cam rotates, a gradually increasing radius of the cam comes in contact with the blade holder forcing the blade holder downwards until the blade contacts the base, thereby severing the material. A resulting cut is optimally free of splinters and the resulting cut end of the material is otherwise clean and straight.</p>
<?summary-of-invention description="Summary of Invention" end="tail"?>
<?brief-description-of-drawings description="Brief Description of Drawings" end="lead"?>
<description-of-drawings>
<heading id="h-0004" level="1">BRIEF DESCRIPTION OF THE DRAWINGS</heading>
<p id="p-0012" num="0011"><figref idref="DRAWINGS">FIG. 1</figref> is a perspective view of a cutting tool according to one embodiment of this invention;</p>
<p id="p-0013" num="0012"><figref idref="DRAWINGS">FIG. 2</figref> is another perspective view of the cutting tool shown in <figref idref="DRAWINGS">FIG. 1</figref> with a sheet of material to be cut;</p>
<p id="p-0014" num="0013"><figref idref="DRAWINGS">FIG. 3</figref> is a side view of the cutting tool shown in <figref idref="DRAWINGS">FIG. 1</figref> in an open position;</p>
<p id="p-0015" num="0014"><figref idref="DRAWINGS">FIG. 4</figref> is a side view of the cutting tool shown in <figref idref="DRAWINGS">FIG. 1</figref> in a closed position; and</p>
<p id="p-0016" num="0015"><figref idref="DRAWINGS">FIG. 5</figref> is an opposite side view of the cutting tool shown in <figref idref="DRAWINGS">FIG. 1</figref> in the closed position; and</p>
<p id="p-0017" num="0016"><figref idref="DRAWINGS">FIG. 6</figref> is an end view of the cutting tool shown in <figref idref="DRAWINGS">FIG. 1</figref>.</p>
</description-of-drawings>
<?brief-description-of-drawings description="Brief Description of Drawings" end="tail"?>
<?detailed-description description="Detailed Description" end="lead"?>
<heading id="h-0005" level="1">DESCRIPTION OF THE INVENTION</heading>
<p id="p-0018" num="0017"><figref idref="DRAWINGS">FIGS. 1-6</figref> show a cutting tool <b>10</b> according to one embodiment of this invention. The cutting tool <b>10</b> as described is preferably used to cut building materials <b>50</b>, such as flooring, in a predictable and straight fashion without splintering, cracking or similar problems that may arise from such cuts.</p>
<p id="p-0019" num="0018">As used herein, &#x201c;material&#x201d; refers to a sheet or plank of building material, preferably flooring, such as wood flooring, laminate flooring, parquet flooring, composite flooring, wood trim, baseboards, vinyl flooring, vinyl siding, vinyl composition tile or similar materials, including, but not limited to, one or more combinations of wood, fiber, concrete, plastic and/or other materials that may or may not include a laminated layer.</p>
<p id="p-0020" num="0019">The cutting tool <b>10</b> includes a base <b>12</b> that may be formed of steel or other similar rigid material. As shown in <figref idref="DRAWINGS">FIG. 1</figref>, the base <b>12</b> is T-shaped, however, the base <b>12</b> is not limited to a T-shape and can be any shape capable of providing support to the cutting tool <b>10</b>. The cutting tool <b>10</b> preferably includes a support surface <b>14</b> attached to the base <b>12</b>. The support surface <b>14</b> is desirably sized to accommodate a type of material to be cut, including for example, but not limited to, an <b>8</b> inch plank of flooring. As shown in <figref idref="DRAWINGS">FIGS. 1 and 2</figref>, additional support for the material <b>50</b> to be cut can be provided by a support element <b>48</b>.</p>
<p id="p-0021" num="0020">In a preferred embodiment, the cutting tool <b>10</b> includes at least one guide rail <b>16</b> to orientate the material <b>50</b> with respect to a blade <b>20</b>. The guide rail <b>16</b> can be set up to provide a rest for the material <b>50</b> to be cut at a right angle. In a preferred embodiment, the guide rail <b>16</b> includes a plurality of coupling forks which allow the guide rail <b>16</b> to be attached to the cutting tool <b>10</b> at a plurality of angles to the blade <b>20</b>. For example, the plurality of coupling forks allow the guide rail <b>16</b> to be attached to the cutting tool <b>10</b> at angles of 45&#xb0;, 90&#xb0; and 135&#xb0; to the blade <b>20</b>. In a alternative embodiment, the guide rail <b>16</b> includes a means to rotate about an axis perpendicular to the support surface <b>14</b> and a mechanism to lock the guide rail at an angle to the blade <b>20</b>, allowing materials to be cut at any angle from 0&#xb0; to 180&#xb0;.</p>
<p id="p-0022" num="0021">The base <b>12</b> further includes a base extension <b>18</b> for increased stability of the cutting tool <b>10</b>. In an embodiment of this invention, the base extension <b>18</b> is extendable and can operate in multiple ways including, but not limited to, a telescopic extension, a pivoting extension, or a bolt-on extension.</p>
<p id="p-0023" num="0022">In an embodiment of this invention, the cutting tool <b>10</b> includes a means for lining up the material <b>50</b> to be cut with the blade <b>20</b>, for example, the cutting tool <b>10</b> can include a laser guide for lining up the material to be cut.</p>
<p id="p-0024" num="0023">Connected to the base <b>12</b> is a pair of risers, a blade holder riser <b>22</b> and a cam riser <b>24</b>. In this embodiment, the blade holder riser <b>22</b> and the cam riser <b>24</b> are bolted to the base <b>12</b>. However, the blade holder riser <b>22</b> and the cam riser <b>24</b> can be secured to the base by any means including a weld or a rivet connection. Alternatively, either one or both of the blade holder riser <b>22</b> and the cam riser <b>24</b> could be integrally formed with the base <b>12</b>.</p>
<p id="p-0025" num="0024">Positioned over the base <b>12</b> is a blade holder <b>26</b> with a fixed end <b>28</b> and a free end <b>30</b>. The fixed end <b>28</b> is rotatably connected with the blade holder riser <b>22</b> with an axle <b>32</b> at a first pivot point. In a preferred embodiment, the axle <b>32</b> is a removable pin that allows the blade holder <b>26</b> to be removed for repairs or blade sharpening, however, the axle <b>32</b> can be any mechanism that allows the blade holder <b>26</b> to pivot.</p>
<p id="p-0026" num="0025">The blade <b>20</b> is preferably mounted to the blade holder <b>26</b> in a manner which allows the blade <b>20</b> to be detached, including, but not limited to, a threaded connection and a friction fit. Such a detachable mounting allows the blade to be removed for sharpening or repairs. However, the blade <b>20</b> can be permanently mounted to the blade holder with a weld, an adhesive connection, a friction fit or other type of connection. Alternatively, the blade <b>20</b> can be integrally formed with the blade holder <b>26</b>. As shown in <figref idref="DRAWINGS">FIG. 3</figref>, the blade <b>20</b> includes a straight edge. In an alternative embodiment, the blade <b>20</b> includes a tapered portion that allows for improved cutting through some types of materials and allows the blade <b>20</b> to extend along a greater portion of the blade holder <b>26</b> and fit between the blade holder <b>26</b> and the base <b>12</b>.</p>
<p id="p-0027" num="0026">As shown in the figures, an eccentric cam <b>34</b> is positioned over and in contact with the free end <b>30</b> of the blade holder <b>26</b>. The eccentric cam <b>34</b> is rotatably connected to the cam riser <b>24</b> with an axle <b>36</b> at a second pivot point. In an embodiment of this invention, the axle <b>36</b> is removable allowing for the eccentric cam to be removed for repairs and to provide access to the blade holder <b>26</b>.</p>
<p id="p-0028" num="0027">In an embodiment of this invention, the eccentric cam <b>34</b> includes a cam stop <b>35</b>. In operation, the cam stop <b>35</b> contacts the blade holder <b>26</b> in the closed position, preventing the eccentric cam <b>34</b> from over-rotating and possibly damaging the cutting tool <b>10</b>. The cam stop <b>35</b> can also provide additional leverage to force the blade <b>20</b> through tough-to-cut materials.</p>
<p id="p-0029" num="0028">A handle <b>38</b> connects with the eccentric cam <b>34</b> and provides leverage to rotate the eccentric cam <b>34</b>. In an embodiment of this invention, a proximate end <b>40</b> of the handle <b>38</b> fits over an extension of the eccentric cam <b>34</b> and is secured with a threaded connection. Alternatively, the handle <b>38</b> can be secured to the eccentric cam <b>34</b> with a weld or an adhesive connection. In an alternative embodiment, the handle <b>38</b> is integrally formed with the eccentric cam <b>34</b>. A distal end <b>42</b> of the handle <b>38</b> preferably includes a hand grip <b>44</b> or other portion for the user to manually grab or engage. In an embodiment of this invention, the handle <b>38</b> further includes an extension <b>46</b> which provides additional leverage for rotating the eccentric cam <b>34</b>.</p>
<p id="p-0030" num="0029">As shown in <figref idref="DRAWINGS">FIG. 5</figref>, the cutting tool <b>10</b> preferably includes a support arm <b>52</b> adjustably mounted to the base <b>12</b>. The support arm <b>52</b> holds the material <b>50</b> against the support surface <b>14</b> to prevent the material <b>50</b> from moving during cutting ensuring a clean cut of the material <b>50</b>. As shown in <figref idref="DRAWINGS">FIG. 2</figref>, the support arm <b>52</b> includes a mounting bracket <b>54</b>, an adjusting screw <b>56</b>, a support arm extension <b>58</b> and a foot <b>60</b>.</p>
<p id="p-0031" num="0030">The mounting bracket <b>54</b> and the screw <b>56</b> allow the support arm <b>52</b> to be secured at multiple positions to provide support of materials <b>50</b> of varying thickness. Alternatively, the mounting bracket <b>54</b> is biased in a downward direction by a spring, not shown, to hold the support arm <b>52</b> against the material <b>50</b>.</p>
<p id="p-0032" num="0031">The foot <b>60</b> is preferably manufactured from a rubber material but can be made of any material including, but not limited to, plastic, metals and composite materials. The material of the foot <b>60</b> is preferably capable of frictionally securing the position of the material <b>50</b> and is able to compensate for irregular surfaces of the material <b>50</b>. In an alternative embodiment, the foot <b>60</b> can pivot or float to secure the material <b>50</b> and to compensate for irregular surfaces of the material <b>50</b>.</p>
<p id="p-0033" num="0032">The cutting tool <b>10</b> is preferably highly portable when the handle <b>38</b> is in the closed position. In a preferred embodiment, the cutting tool <b>10</b> includes a lock to maintain the cutting tool in the closed position. In <figref idref="DRAWINGS">FIG. 1</figref>, the lock is a latch <b>62</b> and a hook <b>64</b> which extend between the base <b>12</b> and the handle <b>38</b>. In an alternative embodiment, the lock is a pin that fits into a receiver in the eccentric cam preventing the eccentric cam from rotating.</p>
<p id="p-0034" num="0033">In operation, the cutting tool <b>10</b> of this invention starts in an open position, as shown in <figref idref="DRAWINGS">FIGS. 1-3</figref>. In the open position, a spring biases the blade holder <b>26</b> upward and the eccentric cam <b>34</b> contacts the blade holder <b>26</b> at a relatively small radius, this provides an opening between the blade <b>20</b> and a portion of the base <b>12</b>, such as a blade stop <b>64</b>. A user inserts the material <b>50</b> to be cut onto the base <b>12</b> and through the opening formed between the blade <b>20</b> and the base <b>12</b>. To cut the material, the handle <b>38</b> is lowered to rotate the eccentric cam <b>34</b>. By rotating the eccentric cam <b>34</b>, a gradually increasing radius of the eccentric cam <b>34</b> contacts the blade holder <b>26</b> thereby forcing the blade <b>28</b> downward as the radius increases until the cutting tool <b>10</b> is in a closed position, as shown in <figref idref="DRAWINGS">FIGS. 4 and 6</figref>, thereby cutting the material <b>50</b>. The resulting cut is optimally free of splinters and a resulting cut end of the material is otherwise clean and straight.</p>
<p id="p-0035" num="0034">While in the foregoing specification this invention has been described in relation to certain preferred embodiments thereof, and many details have been set forth for purpose of illustration, it will be apparent to those skilled in the art that the material cutter is susceptible to additional embodiments and that certain of the details described herein can be varied considerably without departing from the basic principles of the invention.</p>
<?detailed-description description="Detailed Description" end="tail"?>
</description>
<us-claim-statement>What is claimed is:</us-claim-statement>
<claims id="claims">
<claim id="CLM-00001" num="00001">
<claim-text><b>1</b>. A cutting tool comprising:
<claim-text>a base;</claim-text>
<claim-text>a blade holder pivotally connected to the base at a first pivot point;</claim-text>
<claim-text>an eccentric cam positioned over a portion of the blade holder and pivotally connected to the base at a second pivot point;</claim-text>
<claim-text>a blade connected to the blade holder, wherein the blade holder and the blade are movable in a cutting direction from an open position to a closed position by rotating the eccentric cam; and</claim-text>
<claim-text>a support arm adjustable with respect to the base, wherein the support arm holds down a material to be cut against the base.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00002" num="00002">
<claim-text><b>2</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the support arm includes a mounting bracket, an adjusting screw and a foot, wherein the mounting bracket, the adjusting screw and the foot can be adjusted to support materials of varying thickness at multiple positions.</claim-text>
</claim>
<claim id="CLM-00003" num="00003">
<claim-text><b>3</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref> further comprising:
<claim-text>a spring positioned between the blade holder and the base, wherein the spring biases the cutting tool towards the open position.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00004" num="00004">
<claim-text><b>4</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the base includes a support surface for supporting a material to be cut.</claim-text>
</claim>
<claim id="CLM-00005" num="00005">
<claim-text><b>5</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref> further comprising:
<claim-text>a handle including a grip, wherein the handle provides leverage to rotate the eccentric cam about the second pivot point.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00006" num="00006">
<claim-text><b>6</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the eccentric cam includes a cam stop, wherein in the closed position the cam stop contacts the blade holder.</claim-text>
</claim>
<claim id="CLM-00007" num="00007">
<claim-text><b>7</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the first pivot point comprises a pin to hinge the blade holder and the second pivot point comprises a second pin to hinge the eccentric cam.</claim-text>
</claim>
<claim id="CLM-00008" num="00008">
<claim-text><b>8</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the blade includes a flat edge.</claim-text>
</claim>
<claim id="CLM-00009" num="00009">
<claim-text><b>9</b>. The cutting tool of <claim-ref idref="CLM-00001">claim 1</claim-ref>, wherein the blade includes a tapered edge.</claim-text>
</claim>
<claim id="CLM-00010" num="00010">
<claim-text><b>10</b>. A cutting tool comprising:
<claim-text>a base including a support surface, a cam riser with a cam pivot point and a blade holder riser with a holder pivot point;</claim-text>
<claim-text>an eccentric cam connected to a handle, the eccentric cam hingely connected to the cam pivot point;</claim-text>
<claim-text>a blade holder in contact with the eccentric cam and hingely connected to the base at the holder pivot point;</claim-text>
<claim-text>a blade positioned on the blade holder, wherein the blade holder and the blade are movable in a cutting direction from an open position to a closed position by rotating the eccentric cam; and</claim-text>
<claim-text>a support arm adjustably connected to the base to hold a material to be cut against the support surface.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00011" num="00011">
<claim-text><b>11</b>. The cutting tool of <claim-ref idref="CLM-00010">claim 10</claim-ref> further comprising:
<claim-text>a spring positioned between the blade holder and the base, wherein the spring biases the cutting tool towards the open position.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00012" num="00012">
<claim-text><b>12</b>. The cutting tool of <claim-ref idref="CLM-00010">claim 10</claim-ref>, further comprising:
<claim-text>a guide rail connected to the base to orientate the material at an angle with respect to the blade.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00013" num="00013">
<claim-text><b>13</b>. The cutting tool of <claim-ref idref="CLM-00010">claim 10</claim-ref>, wherein the eccentric cam includes a cam stop, wherein in the closed position the cam stop contacts the blade holder.</claim-text>
</claim>
<claim id="CLM-00014" num="00014">
<claim-text><b>14</b>. The cutting tool of <claim-ref idref="CLM-00010">claim 10</claim-ref>, wherein the holder pivot point comprises an axle to hinge the blade holder and the cam pivot point comprises a second axle to hinge the eccentric cam.</claim-text>
</claim>
<claim id="CLM-00015" num="00015">
<claim-text><b>15</b>. A cutting tool comprising:
<claim-text>a base including a support surface;</claim-text>
<claim-text>a blade holder including a fixed end and a free end, the fixed end hingely connected to the base;</claim-text>
<claim-text>an eccentric cam positioned over the free end of the blade holder and rotatably connected to the base;</claim-text>
<claim-text>a handle extending from the eccentric cam;</claim-text>
<claim-text>a blade positioned on the blade holder, wherein the blade holder and the blade are movable in a cutting direction from an open position to a closed position by rotating the eccentric cam;</claim-text>
<claim-text>a support arm adjustable with respect to the base, wherein the support arm holds down a material to be cut against the support surface of the base; and</claim-text>
<claim-text>a guide rail connected to the base, wherein the guide rail orientates the material to be cut at an angle to the blade.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00016" num="00016">
<claim-text><b>16</b>. The cutting tool of <claim-ref idref="CLM-00015">claim 15</claim-ref>, wherein the support arm includes a mounting bracket, an adjusting screw and a foot, wherein the mounting bracket, the adjusting screw and the foot can be adjusted to support materials of varying thickness at multiple positions.</claim-text>
</claim>
<claim id="CLM-00017" num="00017">
<claim-text><b>17</b>. The cutting tool of <claim-ref idref="CLM-00015">claim 15</claim-ref> further comprising:
<claim-text>a spring positioned between the blade holder and the base, wherein the spring biases the cutting tool towards the open position.</claim-text>
</claim-text>
</claim>
<claim id="CLM-00018" num="00018">
<claim-text><b>18</b>. The cutting tool of <claim-ref idref="CLM-00015">claim 15</claim-ref>, wherein the eccentric cam includes a cam stop to prevent the eccentric cam from over-rotating in the closed position.</claim-text>
</claim>
<claim id="CLM-00019" num="00019">
<claim-text><b>19</b>. The cutting tool of <claim-ref idref="CLM-00015">claim 15</claim-ref>, wherein the guide rail is adjustable to a plurality of angles with respect to the blade.</claim-text>
</claim>
<claim id="CLM-00020" num="00020">
<claim-text><b>20</b>. The cutting tool of <claim-ref idref="CLM-00015">claim 15</claim-ref>, wherein the blade includes a flat edge.</claim-text>
</claim>
</claims>
</us-patent-application>
"""
patent = USPublicationContent(xml_content)
structured_data = patent.get_data()
x=1
# import json
#
# print(json.dumps(structured_data, indent=4))
#
# # Instantiate the USPatentContent class with XML content
# patent = USPublicationContent(xml_content)
#
# # Retrieve the full text data
# full_text = patent.get_full_text()
#
# # Print the full formatted text
# print(full_text["to_string"]())
# # Instantiate the class
# patent = USPublicationContent(xml_content)
#
# # Extract and print figure details
# figures = patent.get_figures()
# print(figures)
#
# # Display the first figure if the image file exists locally
# if figures:
#     image_path = figures[0]["image_file"]  # Assuming the TIFF file is available
#     patent.display_figure(image_path)

