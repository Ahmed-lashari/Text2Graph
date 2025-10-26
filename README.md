# Text2Graph

## Project Overview

Text2Graph is a knowledge graph generation platform that converts structured and unstructured data into visual, queryable graph representations. The system supports CSV, JSON, and plain text files as input and generates nodes and relationships in Neo4j. For interactive visualization, the project leverages PyVis and Streamlit to provide an intuitive and dynamic interface.

The primary goal of Text2Graph is to enable users to explore data relationships, identify patterns, and derive insights from raw textual or structured information without extensive manual preprocessing.

## Features

* Support for structured datasets including CSV and JSON
* Support for unstructured textual data such as plain text files
* Automatic entity extraction using spaCy and NLTK
* Relationship extraction using dependency parsing, verb patterns, and entity pattern recognition
* Interactive graph visualization using PyVis
* Neo4j integration for persistent graph storage
* Streamlit frontend for file upload, processing, and visualization
* Dynamic handling of entity types and relationship types

## Architecture

```plaintext
TEXT2GRAPH/
│
├── app.py                          # Main Streamlit entry point (keep minimal)
├── config.py                       # Central configuration file
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
├── core/                           # Core business logic
│   ├── __init__.py
│   ├── database/                   # Database related
│   │   ├── __init__.py
│   │   ├── neo4j_client.py        # Renamed from neo4j_client.py
│   │   └── connection_manager.py   # Manages connection lifecycle
│   │
│   ├── processors/                 # Data processing
│   │   ├── __init__.py
│   │   ├── base_processor.py      # Abstract base class
│   │   ├── text_processor.py      # Text file processing
│   │   ├── csv_processor.py       # CSV processing
│   │   └── json_processor.py      # JSON processing
│   │
│   ├── graph/                      # Graph operations
│   │   ├── __init__.py
│   │   ├── graph_builder.py       # Graph creation
│   │   └── graph_queries.py       # Cypher queries
│   │
│   └── nlp/                        # NLP processing
│       ├── __init__.py
│       ├── entity_extractor.py    # Entity extraction
│       └── relationship_extractor.py  # Relationship extraction
│
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── file_service.py            # File handling orchestration
│   └── graph_service.py           # Graph operations orchestration
│
├── ui/                             # UI components (renamed from views)
│   ├── __init__.py
│   ├── components/                # Reusable UI components
│   │   ├── __init__.py
│   │   ├── file_uploader.py      # File upload component
│   │   ├── progress_bar.py       # Progress indicators
│   │   └── graph_visualizer.py   # Graph visualization
│   │
│   └── pages/                     # Multi-page support (future)
│       ├── __init__.py
│       └── home.py
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── file_utils.py
│   ├── text_utils.py
│   ├── validators.py
│   └── logger.py
│
├── models/                         # Data models/schemas
│   ├── __init__.py
│   ├── entity.py
│   ├── relationship.py
│   └── graph_data.py
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_processors.py
│   ├── test_graph_builder.py
│   └── test_services.py
│
├── data/                           # Data storage
│   ├── uploads/                   # Temporary file storage
│   ├── nltk_data/                 # NLTK data
│   └── samples/                   # Sample files
│       ├── demo.txt
│       ├── example.csv
│       └── example.json
│
└── assets/                         # Static assets
    ├── styles/
    │   └── custom.css
    └── images/

```


Text2Graph follows a modular architecture:

1. **Frontend**

   * Built with Streamlit
   * Provides file upload, progress tracking, and graph visualization
   * Sidebar displays Neo4j connection status

2. **Data Processing**

   * `DataProcessor` class handles file reading, preprocessing, and DataFrame generation
   * Structured files are read into DataFrames directly
   * Unstructured text is tokenized into sentences, entities are extracted using spaCy, and named entity relationships are mapped

3. **Graph Builder**

   * `GraphBuilder` class handles interaction with Neo4j
   * Creates nodes and relationships for structured CSV/JSON data
   * Creates text-based graphs with dynamic entity types and relationship types
   * Handles errors such as invalid Neo4j property types
   * Provides methods to export graph data to PyVis for visualization

4. **Visualization**

   * PyVis is used to render interactive network graphs
   * Node colors, shapes, and sizes are customizable based on entity type
   * Relationships are annotated and visually distinguishable
   * Streamlit embeds the HTML graph for dynamic exploration

## Installation

### Prerequisites

* Python 3.10 or higher
* Neo4j AuraDB
* Streamlit
* spaCy and the `en_core_web_sm` model
* NLTK and `punkt` tokenizer
* PyVis
* Pandas

### Installation Steps

```bash
# Clone the repository
git clone <repository_url>
cd Text2Graph

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK tokenizer
python -m nltk.downloader punkt
```

## Usage

1. Launch Streamlit:

```bash
streamlit run app.py
```

2. Upload a CSV, JSON, or TXT file through the web interface.
3. Track processing progress through the progress bar.
4. View the extracted knowledge graph in the interactive PyVis network.
5. Explore relationships, entity types, and nested connections directly in Neo4j.

## Technical Details

### Text Processing

* Uses NLTK for sentence tokenization
* spaCy for named entity recognition
* Relationships are extracted using three methods:

  * Entity pattern matching
  * Dependency parsing with verbs
  * Prepositional phrase mapping
* Data is transformed into a DataFrame with `source`, `target`, `relationship`, `source_type`, `target_type`, and `sentence` columns

### Neo4j Integration

* Uses `neo4j` Python driver for database operations
* Nodes are dynamically labeled based on entity type
* Relationships are dynamically named and sanitized for Neo4j constraints
* Structured data creates property-based relationships
* Textual data creates fully labeled node-relationship-node structures
* Graph persistence allows querying using Cypher

### Visualization

* PyVis renders dynamic, interactive graphs
* Supports color-coding and shape variation based on entity types
* Embedded in Streamlit as an HTML iframe
* Physics-based layout ensures readable and non-overlapping nodes

## Error Handling

* Invalid Neo4j property types are handled by fallback queries
* Missing or incomplete text entity information defaults to generic entity types
* Streamlit displays error messages with actionable information

## Improvements and Future Work

* Add support for multi-file batch uploads and processing
* Implement more advanced NLP techniques for relationship extraction such as transformers or relation classification models
* Enhance visualization with clustering and filtering of nodes
* Add user-defined relationship mapping for domain-specific graphs
* Integrate a caching layer for faster processing of repeated files
* Enable export of graphs to JSON or GraphML for external analysis

## Contributing

Contributions are welcome. Please follow the repository guidelines for:

* Forking the repository
* Creating feature branches
* Submitting pull requests
* Reporting issues

## License

This project is open source and available under the MIT license.

---

If you want, I can **also write a compact version of this README with diagrams, usage screenshots, and example graphs** to make it more professional for public GitHub release.

Do you want me to create that enhanced version?
