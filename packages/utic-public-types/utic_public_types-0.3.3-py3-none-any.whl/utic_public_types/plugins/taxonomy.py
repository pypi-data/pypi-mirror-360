"""
Here we define some foundational terminology and information architecture.

NOTE: Most of this file should really exist in a database, not a type system.
The exception is the ClassificationTier and some of the information about the
structure of how this taxonomy is structured.


┌──────────────┐                 Artifact/Document Classification Taxonomy
│Classification│                                  │
│Tier          │                                  │
├──────────────┤                ┌─────────────────┴─────────┐
├──────────────┤                │                           │
│              │                │                           │
│Structuredness│          Unstructured                   Structured
│              │                │                           │
│              │                │                           └──────┬──────────────────┐
├──────────────┤    ┌───────────┴───┐                              │                  │
│              │    │               │                              │                  │
│              │    │            Printable                         │                  │
│              │  Audio          Document                         text            binary
│  FormatType  │    │     etc...    │                              │                  │
│              │    │               │                              │                  │
│              │    │               │                              │                  │
│              │    │               │ ▲ taxonomy constrained ▲     │                  │
├──────────────┼────┼───────────────┼─┼──────────────────────┼─────┼──────────────────┼───────────────────────────
│              │    │               │ ▼    taxonomy open     ▼     │                  │
│              │    │               │                              │                  │
│              │    │        ┌──────┴────┐                ┌────────┴┐                 ├──────┬───────┐
│              │    │        │           │                │         │                 │      │       │
│     Format   │   WAV      PDF         PPTX             JSON     HTML               npy   proto   parquet
│              │    │        │            │               │         │                        │       │
│              │    │        │            │               │         │                        │       │
├──────────────┤    │        │            │               │         │           ┌────────────────────┴────┐
│              │    │        │            │               │         │           │example.com/schema.proto │
│              │    │        │            │               │         │           └────────────────────┬────┘
│              │    │      ┌─┴──────┐  ┌──┴────────┐      │         │ ┌──────────────────────────────┼─────┐
│     Schema   │    │      │ PDF-2.0│  │ 8/20/2024 │      │         │ │ https://example.com/schema.thrift  │
│              │    │      │ PDF-1.4│  └───────────┘      │         │ └────────────────────────────────────┘
│              │    │      └────────┘                     │    ┌────┴───────────────────────────────────────┐
│              │    │                                     │    │https://schema.org/Person                   │
│              │ ┌──┴────────────────────┐                │    │https://schema.org/DiagnosticProcedure      │
│              │ │audio/vnd.wave;codec=50│                │    │http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd│
│              │ └───────────────────────┘                │    └────────────────────────────────────────────┘
│              │                                     ┌────┴──────────────────────────────────────────────────────┐
│              │                                     │https://schema.ocsf.io/schema/classes/data_security_finding│
│              │                                     │io.k8s.kubernetes.pkg.api.v1.PodSpec                       │
│              │                                     │utic-elements                                              │
│              │                                     └───────────────────────────────────────────────────────────┘
└──────────────┘


created with https://asciiflow.com/#/
Editable: https://tinyurl.com/utic-document-type-taxonomy

"""

from enum import StrEnum, auto


class ClassificationTier(StrEnum):
    """
    This class is a "meta type" to bring formality to the discussion of file types, formats, and schema.
    As an example, if you had two JSON files with very different contents, you might say, "These are
    the same format, but they have incompatible different schema". Alternatively, you might convert a
    JSON file to YAML and then say "They have different formats, but compatible schema".
    """

    A_STRUCTUREDNESS = auto()
    """
    One way to think of the difference between structured and unstructured is:
    - If there exists an algorithm to parse the document and extract 100% of the information the author encoded
      into the document, it is Structured.
    - If the extraction of 100% of the available information would require "interpretation", or a neural network,
      then it is Unstructured.
    if a complete and lossless reading of  can be made algorithmically, it is almost certainly a structured format. 
    If instead there is meaning in the document which arises from phenomena beyond the reach of alogorithmic parsing, 
    then it is unstructured. You could say alogrithmic vs neural interpretation is a heuristic. 

    """
    B_FORMAT_TYPE = auto()
    """
    The media domain of the format. 
    Audio, Vide, etc. are at this level as well as text-vs-binary for structured.
    """

    C_FORMAT = auto()
    """
    aka "File Type" or "File Format"
    Format refers to the highest level of structure within a file, often thought of as synonymous with "File Type"
    This is the outermost sctructure within a digital format and knowledge of the format is needded in order to
    begin understanding the file and confirming if it adheres to a schema. 
    """

    D_SCHEMA = auto()
    """
    Schema refers to organization of information within the rules of the format. This level of classification helps
    navigate the compatibility between two example files that are otherwise the same "format".
    """


#################################################################################
#     _____ _                   _                      _
#    / ____| |                 | |                    | |
#   | (___ | |_ _ __ _   _  ___| |_ _   _ _ __ ___  __| |_ __   ___  ___ ___
#    \___ \| __| '__| | | |/ __| __| | | | '__/ _ \/ _` | '_ \ / _ \/ __/ __|
#    ____) | |_| |  | |_| | (__| |_| |_| | | |  __/ (_| | | | |  __/\__ \__ \
#   |_____/ \__|_|   \__,_|\___|\__|\__,_|_|  \___|\__,_|_| |_|\___||___/___/
#
#################################################################################


class ArtifactStructuredness(StrEnum):
    ANY = auto()
    STRUCTURED = auto()
    UNSTRUCTURED = auto()


#################################################################################
#    ______                         _     _______
#   |  ____|                       | |   |__   __|
#   | |__ ___  _ __ _ __ ___   __ _| |_     | |_   _ _ __   ___
#   |  __/ _ \| '__| '_ ` _ \ / _` | __|    | | | | | '_ \ / _ \
#   | | | (_) | |  | | | | | | (_| | |_     | | |_| | |_) |  __/
#   |_|  \___/|_|  |_| |_| |_|\__,_|\__|    |_|\__, | .__/ \___|
#                                               __/ | |
#                                              |___/|_|
#################################################################################


class UnstructuredFormatType(StrEnum):
    """
    An Unstructured Type is any for which a proper understanding of the information
    contained therein requires special interpretation logic. A good rule of thumb
    is if you want an ML model or signal processing, you can regard the file as unstructured.

    Images, PDFs, Audio, Video, etc.
    """

    NONE = auto()
    ANY = auto()
    AUDIO = auto()
    VIDEO = auto()
    IMAGE = auto()
    PRINTABLE_DOCUMENT = auto()
    MULTIMEDIA = auto()


class StructuredFormatType(StrEnum):
    NONE = auto()
    ANY = auto()
    TEXT = auto()
    BINARY = auto()


#################################################################################
#    ______                         _
#   |  ____|                       | |
#   | |__ ___  _ __ _ __ ___   __ _| |_
#   |  __/ _ \| '__| '_ ` _ \ / _` | __|
#   | | | (_) | |  | | | | | | (_| | |_
#   |_|  \___/|_|  |_| |_| |_|\__,_|\__|
#
#################################################################################

UnstructuredFormat = str
"""
The Unstructured Format level in the taxonomy is roughly synonymous with the file type.
For example, expect to see values here like "wav", "mov", "png", "pdf", etc

The defining feature of these types is that the information-value of the contents is only
accessible after "rendering" of one form or another.
"""


StructuredFormat = str
"""
A Structured Format is any for which the interpretation follows a clear set of parsing rules.
By definition, these formats have ways of describing the layout of information within them.
We refer to these descriptions as Schemas. Some of these formats have the capability of being
"self describing", but will also frequently have formalized techniques for expressing the schema.
Either way, a critical property for our purpose is the ability to determine if a given specimen
"conforms" to a schema. Another important property is that for each Structured Type, there is no
single universal schema. Thus, we must embrace the reality that to deal with objects at this
level, we must be "schema aware". Two JSON representations are not necessarily conformant to
the same JSONSchema, so we cannot reasonably expect that a system which behaves well on the
first will also behave well on the second.

In an ideal world, a reliable conversion could take place amongst arbitrary structured types.
This is not always possible, of course, but is often commercially valuable.
For example, if you can reliably convert JSON into SQL INSERT statements (given a JSONSchema),
and another tool can reliably convert HTML to JSON, your tools are more valuable, and you are
realizing the benefits of network effects. Some of these conversions are simple due to the properties
of the format. Others may require either clumsy assumptions, or the use of an independent artifact
to describe the mapping between types. It is less common for these "mapping" files to adhere themselves
to well-defined schemas. Even so, it can be a powerful enabler of a data platform to embrace them
where possible.
"""


#################################################################################

#     _____      _
#    / ____|    | |
#   | (___   ___| |__   ___ _ __ ___   __ _
#    \___ \ / __| '_ \ / _ \ '_ ` _ \ / _` |
#    ____) | (__| | | |  __/ | | | | | (_| |
#   |_____/ \___|_| |_|\___|_| |_| |_|\__,_|
#
#################################################################################

SchemaReference = str
"""
Schema Reference is an open field that allows plugins to indicate what shapes of data they know how to work with
within the given format. Indicating schema support can greatly improve the reliability of pipelines, where
plugins are composed and outputs from one are used as inputs of another. Often the Format alone does not 
provide enough information to ensure compatibility, but a format plus schema should.
"""


#################################################################################
#    __  __ _              _
#   |  \/  (_)            | |
#   | \  / |_ ___  ___ ___| | __ _ _ __   ___  ___  _   _ ___
#   | |\/| | / __|/ __/ _ \ |/ _` | '_ \ / _ \/ _ \| | | / __|
#   | |  | | \__ \ (_|  __/ | (_| | | | |  __/ (_) | |_| \__ \
#   |_|  |_|_|___/\___\___|_|\__,_|_| |_|\___|\___/ \__,_|___/
#
#################################################################################


class EncryptionMode(StrEnum):
    UNSUPPORTED = auto()
    PREFERRED = auto()
    "Preferred means encryption will be used if the provided certificate validates, but plaintext is okay. Insecure."
    REQUIRED = auto()


class EncryptionType(StrEnum):
    NONE = auto()
    RSA = auto()
    RSA_AES = auto()


class CompressionType(StrEnum):
    NONE = auto()
    GZIP = auto()
    BZ2 = auto()
    XZ = auto()
    LZ4 = auto()
    ZIP = auto()
    ZSTD = auto()


class FileAttributeType(StrEnum):
    ENCRYPTION_TYPE = auto()
    ENCRYPTION_KEY_IDENTIFIER = auto()
    COMPRESSED = auto()
    COMPRESSION_TYPE = auto()
    COMPRESSION_EXTRA = auto()


ELEMENTS_TYPE = f"/{ArtifactStructuredness.STRUCTURED}/{StructuredFormatType.TEXT}/json/utic-elements-v1"
