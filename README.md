# IMETO — Overview of the Project  
**Impact Measurement Tool — Automated Analysis of Research Impact**

IMeTo (Impact Measurement Tool) is a pilot initiative of the Institute of Literary Research of the Polish Academy of Sciences (IBL PAN), developed within the **GRAPHIA** project.  
Its goal is to automate the assessment of research impact by combining:

- structured data models,  
- ingestion pipelines (upload + API),  
- vector-based text indexing,  
- analytical and generative LLMs,  
- a modular backend API.

IMeTo is designed to support managers of research institutions, research teams, and individual researchers in evaluating and communicating the societal, scientific, and economic impact of their work.

---

# 1. Project Context and Objectives

IMeTo aims to measure the impact of scientific activities by analysing both:

- research publications, and  
- activities defined by national evaluation frameworks (e.g., teaching, public engagement, dissemination, applied research).

The tool is intended to:

- streamline assessment processes,  
- improve institutional reporting,  
- support strategic decision-making,  
- enhance communication of research impact to society.

---

# 2. GRAPHIA Project Background

IMeTo is part of **GRAPHIA**, an EU-funded Horizon Europe project focused on:

- developing a **knowledge graph for humanities and social sciences (SSH)**,
- integrating distributed datasets and infrastructures, including:  
  EHRI Collection Graph, E-RIHS DIGILAB KG, RESILIENCE ReIReSearch, CNRS KG Matilda, OpenCitations, ORKG, and GESIS Knowledge Graph,
- building advanced AI- and LLM-powered services for SSH,
- modernising SSH research and innovation workflows.

GRAPHIA involves **20 partners from 10 countries**, including **five ESFRI infrastructures**, highlighting its strategic importance for the European Research Area.

---

# 3. Knowledge and Technology Transfer in SSH

IMeTo contributes to strengthening knowledge and technology transfer in the humanities and social sciences by enabling researchers and institutions to:

- document how research results benefit society,
- identify beneficiaries and practical applications,
- understand the pathways through which knowledge influences public, cultural, economic, policy, or educational domains.

In SSH, technology transfer often focuses on:

- dissemination of knowledge,  
- communication of insights to broader audiences,  
- shaping public awareness or cultural practices.

IMeTo helps structure and analyse these processes in a data-informed manner.

---

# 4. System Architecture Overview

The tool consists of four main layers:

## 4.1. **Data Layer**
IMeTo ingests data in two ways:

1. **File uploads (PDF, TXT, DOCX)**  
   - publications, teaching materials, grant documents, conference abstracts.

2. **API-based ingestion**  
   - Crossref  
   - ORCID  
   - local CRIS systems  
   - POL-on (Poland’s national research information system)

All data is normalized to unified Pydantic schemas, covering:

- subjects (researcher, team, institution),
- research outputs,
- ingestion metadata,
- impact reports.

## 4.2. **Ingestion Pipeline**

Processing includes:

- parsing uploaded documents (PDF → text),  
- extracting metadata,  
- text chunking for vector indexing,  
- indexing in a vector store.

## 4.3. **Analytical and Generative LLM Components**

IMeTo uses a hybrid LLM architecture:

### **Analytical model**  
Assigns labels from impact typologies to text segments:

- activity type,  
- beneficiaries,  
- societal context,  
- intended use of research results,  
- evidence of impact.

### **Generative model**  
Produces coherent impact narratives based on:

- extracted labels,  
- textual analysis,  
- relationships between impact types.

IMeTo is designed to work with open-source LLMs such as:

- Llama  
- Mistral  
- PLLuM  

with the option for **fine-tuning** on SSH impact data.

## 4.4. **Reporting Layer**

The system generates structured impact reports that include:

- descriptions of research activities,  
- identified societal contributions,  
- contextual explanations,  
- structured evidence of impact.

Reports can be consumed via:

- JSON API,  
- UI,  
- CRIS integrations,  
- MCP-based agent workflows.

---

# 5. Data Source: POL-on

A key dataset for developing typologies and training analytical components comes from the **POL-on** system — Poland’s integrated national database of higher education and science.

It contains institution-submitted descriptions explaining how specific research results have influenced:

- economy,  
- public administration,  
- healthcare,  
- culture,  
- environmental protection,  
- national security,  
- other areas of social development.

These descriptions are used in national research evaluation and provide high-quality input for training and testing impact analysis models.

---

# 6. Importance of IMeTo

IMeTo addresses a fundamental challenge in SSH:

> **How can the societal impact of research be documented, analysed, and communicated effectively?**

Research shows [1–3] that:

- impact evaluation must be data-driven,  
- SSH institutions require scalable tools to analyse diverse outputs,  
- researchers need support in articulating impact narratives.

IMeTo enhances this process by:

- analysing large volumes of data,  
- standardising reporting practices,  
- improving visibility of SSH impact,  
- strengthening institutional capacity for evidence-based assessment.
