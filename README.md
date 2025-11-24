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

These materials support the creation of typologies and testing of LLM-based extraction methods.
