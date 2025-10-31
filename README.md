# 🧠 Text2Graph - Knowledge Graph Generator

## Project Overview

[**Text2Graph**](https://text2graph-generator.streamlit.app/)
 is an advanced knowledge graph generation platform designed to convert both structured and unstructured data into interactive, queryable graph representations. The system supports CSV, JSON, and plain text files, generating nodes and relationships within a Neo4j database. For dynamic visualization, the platform integrates PyVis with Streamlit to provide an intuitive and interactive user interface.

The primary objective of Text2Graph is to enable users to uncover hidden relationships, identify patterns, and extract actionable insights from raw data without extensive manual preprocessing.

---

## Features

* Support for structured datasets (CSV, JSON)
* Support for unstructured textual data (TXT)
* Automatic entity extraction using spaCy and NLTK
* Relationship extraction via entity patterns, dependency parsing, and prepositional phrase mapping
* Interactive network graph visualization with PyVis
* Neo4j integration for persistent graph storage
* Streamlit frontend with file upload, processing progress, and graph exploration
* Dynamic handling of entity types and relationship types
* Error handling for invalid Neo4j property types

---

## Architecture

```plaintext
TEXT2GRAPH/
│
├── app.py                          # Streamlit entry point
├── config.py                       # Configuration
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
├── core/
│   ├── database/
│   │   ├── connection_manager.py
│   │   └── neo4j_client.py
│   │
│   ├── processors/
│   │   ├── base_processor.py
│   │   ├── text_processor.py
│   │   ├── csv_processor.py
│   │   └── json_processor.py
│   │
│   ├── graph/
│   │   ├── graph_builder.py
│   │   └── graph_queries.py
│   │
│   └── nlp/
│       ├── entity_extractor.py
│       └── relationship_extractor.py
│
├── services/
│   ├── file_service.py
│   └── graph_service.py
│
├── ui/
│   ├── components/
│   │   ├── file_uploader.py
│   │   ├── progress_bar.py
│   │   └── graph_visualizer.py
│   └── pages/
│       └── home.py
│
├── utils/
│   ├── file_utils.py
│   ├── text_utils.py
│   ├── validators.py
│   └── logger.py
│
├── models/
│   ├── entity.py
│   ├── relationship.py
│   └── graph_data.py
│
├── tests/
│   ├── test_processors.py
│   ├── test_graph_builder.py
│   └── test_services.py
│
├── data/
│   ├── uploads/
│   ├── nltk_data/
│   └── samples/
│       ├── demo.txt
│       ├── example.csv
│       └── example.json
│
└── assets/
    ├── styles/
    └── images/
```

---

## Installation

### Prerequisites

* Python 3.11
* Neo4j AuraDB or local Neo4j instance
* Streamlit
* spaCy (`en_core_web_sm` model)
* NLTK (`punkt` tokenizer)
* PyVis
* Pandas

### Installation Steps

```bash
# Clone repository
git clone https://github.com/Ahmed-lashari/Text2Graph.git
cd Text2Graph

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

---

## Usage

1. Launch the Streamlit app:

```bash
streamlit run app.py
```

2. Upload CSV, JSON, or TXT files.
3. Track progress via the progress bar.
4. View the generated knowledge graph in PyVis.
5. Explore entities, relationships, and nested connections directly in Neo4j.

---

## Technical Details

### Text Processing

* NLTK for sentence tokenization
* spaCy for named entity recognition
* Relationships extracted using:

  * Entity pattern matching
  * Dependency parsing with verbs
  * Prepositional phrase mapping
* Data transformed into a DataFrame with:

  * `source`
  * `target`
  * `relationship`
  * `source_type`
  * `target_type`
  * `sentence`

### Neo4j Integration

* Nodes dynamically labeled based on entity type
* Relationships dynamically named and sanitized
* Structured data generates property-based relationships
* Textual data generates fully labeled node-relationship-node structures
* Supports graph persistence for Cypher querying

### Visualization

* PyVis renders interactive network graphs
* Nodes color-coded and shaped based on entity type
* Relationships annotated for clarity
* Streamlit embeds HTML graphs with physics-based layout for readability

---

## Error Handling

* Invalid Neo4j property types handled with fallback queries
* Missing or incomplete entity info defaults to generic types
* Streamlit displays errors with actionable messages

---

## Improvements and Future Work

* Multi-file batch uploads
* Advanced NLP for relationship extraction using transformers
* Enhanced visualization with clustering and filtering
* User-defined relationship mapping
* Caching layer for repeated files
* Graph export to JSON or GraphML

---

## Contributing

Community members are welcome to collaborate by raising issues, suggesting features, or submitting pull requests. While the repository is private, collaborators may request access through GitHub to contribute to improvements and enhancements.

---

## Developers / Collaborators
| Profile | Name | Profession | Contribution |
| ------- | ---- | ---------- | ------------ |
| <a href="https://www.linkedin.com/in/muhammad-ahmed-lashari/" target="_blank"><img src="https://media.licdn.com/dms/image/v2/D4D03AQHdrKCpdwmgZw/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1699094030253?00e=1762992000&v=beta&t=aLmZVqJRjrWFPqe2t6gbj2Azg9tT82Ikn0J7naO39J8" width="100" height="80" style="border-radius:40px;"></a> | [Muhammad Ahmed Lashari](https://www.linkedin.com/in/muhammad-ahmed-lashari/) | AI UnderGrad / Flutter Developer | Developed the initial version of Text2Graph and deployed on Streamlit Cloud. |


---