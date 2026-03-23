# IMETO
**Impact Measurement Tool — Automated Assessment of Research Impact**

IMeTo (Impact Measurement Tool) is a **work-in-progress prototype** developed at the Institute of Literary Research of the Polish Academy of Sciences (IBL PAN) within the **GRAPHIA** project.  
The goal is to explore how AI, LLMs, and structured data workflows can support **automated assessment and communication of research impact** in the humanities and social sciences (SSH).

The system is not yet a complete solution — it is an evolving architectural and methodological concept under active development.

---

# 1. Purpose of IMeTo

IMeTo aims to support institutions, research teams, and individual researchers by:

- analysing a wide range of scientific outputs (publications, grant descriptions, teaching activity, dissemination work),  
- identifying elements relevant for research evaluation frameworks,  
- assisting in the preparation of **draft impact descriptions**,  
- helping document **societal, cultural, policy, and economic influence** of SSH research.

The tool is designed to improve how SSH institutions understand, monitor, and communicate their impact.

---

# 2. Connection to the GRAPHIA Project

IMeTo is part of **GRAPHIA**, a Horizon Europe project developing an **AI-enhanced knowledge graph for SSH**. GRAPHIA integrates data from major research infrastructures and develops services that modernise SSH research practices.

Within this context, IMeTo explores how:

- open-source LLMs (e.g., Mistral, Llama),  
- structured metadata models,  
- ingestion pipelines (upload + API),  
- and vector-based text search  

can be combined to support impact evaluation workflows.

---

# 3. Planned System Concept 

Although under development, the intended architecture includes:

### **Data ingestion:**
- Upload of PDFs and text files  
- Retrieval from APIs (Crossref, ORCID, local CRIS systems)  

### **Analysis pipeline:**
- Document parsing and chunking  
- Classification using analytical LLM labels (activity type, beneficiaries, outcomes)  
- Generation of draft impact descriptions with a generative LLM  

### **Reporting:**
- Structured impact reports combining extracted labels and generated narratives  
- Integration with CRIS systems or local datasets  

This hybrid analytical + generative approach is currently being prototyped.

---

# 4. Data Foundations

The development draws on annotated impact descriptions from **[RAD-on](https://radon.nauka.gov.pl/)**, the national system for higher education and research in Poland. These descriptions document real cases of societal impact across domains such as:

- economy,  
- public administration,  
- healthcare,  
- culture,  
- environment,  
- national security.

---

# 5. Installation & Usage

## Prerequisites

- Python 3.10+
- (optional) MongoDB — only needed for ingestion scripts, **not** for local download

## Setup

```bash
# Clone the repository
git clone https://github.com/patthub/impact_measurement_tool.git
cd impact_measurement_tool

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# Install the project in editable mode (this fixes all import issues)
pip install -e .
```

## Download impacts from RAD-on (no MongoDB needed)

```bash
# Download all impacts (kindCode=1) to JSON
python -m app.scripts.download_impacts -o impacts.json

# Download all impacts to CSV (with flattened evidence & achievements columns)
python -m app.scripts.download_impacts -o impacts.csv

# Test run — first 100 records only
python -m app.scripts.download_impacts -o test_impacts.json --max-records 100

# Download impacts for specific institutions (UUIDs from file)
python -m app.scripts.download_impacts \
    --institutions-file app/data/institutions.txt \
    -o impacts_institutions.json

# Change kindCode
python -m app.scripts.download_impacts --kind-code 2 -o impacts_kind2.json

# Include full raw API response in JSON
python -m app.scripts.download_impacts -o impacts_full.json --include-raw
```

## Ingest impacts to MongoDB

Requires a running MongoDB instance on `localhost:27017` (configurable in `app/db/mongo.py`).

```bash
# Ingest all impacts (kindCode=1)
python -m app.scripts.ingest_radon_impacts_all --kind-code 1

# Ingest impacts for institutions listed in file
python -m app.scripts.ingest_radon_impacts \
    --institutions-file app/data/institutions.txt
```

## Run the FastAPI server

```bash
pip install uvicorn
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`. Health check: `GET /health`. Impacts endpoint: `GET /impacts`.

---

# 6. Project Structure

```
impact_measurement_tool/
├── pyproject.toml                    # Project config & dependencies
├── requirements.txt                  # Pinned dependencies
├── app/
│   ├── main.py                       # FastAPI application
│   ├── api/
│   │   └── impacts.py                # API endpoints for impacts
│   ├── connectors/
│   │   ├── base.py                   # Abstract base connector
│   │   └── radon.py                  # RAD-on API connector
│   ├── db/
│   │   └── mongo.py                  # MongoDB connection
│   ├── models/
│   │   ├── impact_case.py            # ImpactCaseSchema, EvidenceItem, AchievementItem
│   │   ├── identifiers.py            # IdentifierSchema
│   │   ├── entities.py               # AssessedEntitySchema
│   │   ├── evaluation.py             # Evaluation schemas
│   │   └── ...                       # Other domain models
│   ├── repositories/
│   │   └── impact_repository.py      # MongoDB CRUD for impacts
│   ├── scripts/
│   │   ├── download_impacts.py       # Download to JSON/CSV (no DB)
│   │   ├── ingest_radon_impacts.py   # Ingest by institution UUID → MongoDB
│   │   └── ingest_radon_impacts_all.py  # Ingest all by kindCode → MongoDB
│   └── data/
│       └── institutions.txt          # List of institution UUIDs
```
