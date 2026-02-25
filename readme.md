# Engagement Analytics Platform  
### A lightweight relational database and interactive dashboard built with Python, SQLite, and Streamlit
##### Author: [Lisa Monozlai](https://www.linkedin.com/in/lisamonozlai/)
---

### ▶ **[View Database Demo](https://lisamonozlai-relational-database-demo.streamlit.app/)**

Browse, filter, update, and visualize multi‑year data through a structured interface that protects the integrity of the original source files.

---

## About

This project demonstrates how organizations can transition from fragmented spreadsheets to a structured, queryable relational database system.

Many small and mid-sized teams rely on multi-year Excel files to track engagement data. While familiar, this approach limits visibility, consistency, and analytical insight. This project illustrates what becomes possible when engagement data is unified in a relational database and exposed through an interactive application.

All data in this project is fictional and designed to demonstrate:

- How relational storage improves data integrity and consistency  
- How controlled vocabularies reduce ambiguity across years  
- How structured schemas enable reliable filtering and aggregation  
- How a simple UI makes structured data accessible to non-technical users  
- How multi-year engagement patterns emerge once data is unified  

---

## Challenge

To ground the project, this system models a hypothetical team that wants to understand which organizations they engage with each year. Their data lives in three separate spreadsheets:

- `engagement_data_2022.xlsx`  
- `engagement_data_2023.xlsx`  
- `engagement_data_2024.xlsx`  

Although the files share similar fields, the team cannot easily:

- View all years together  
- Filter by industry, region, or organization size  
- Compare engagement patterns across years  
- Update records without manually editing spreadsheets  
- Maintain consistent vocabularies across files  

They need a solution that is low cost, low maintenance, and compatible with familiar workflows.

---

## Solution Overview

This project implements a lightweight engagement analytics platform built with:

- **Python** for cleaning, merging, and standardizing multi-year data  
- **SQLite** for relational storage  
- **SQL** for structured queries and aggregation  
- **Streamlit** for a non-technical, interactive frontend  
- **Generative AI tools** (e.g., Microsoft Copilot) for scaffolding and documentation acceleration  

The architectural pattern separates data processing, database logic, and UI rendering to ensure maintainability and clarity.

---

## Repository Structure

This project follows a simple, modular layout:

- **app.py** — Main Streamlit application that renders the interactive UI.  
- **requirements.txt** — Python dependencies for running the project.  
- **data/raw/** — Original multi‑year Excel files used as source inputs.  
- **data/processed/engagement.db** — SQLite database generated after ETL.  
- **db/schema.sql** — Defines the relational structure of the database.  
- **db/connection.py** — Creates and manages the SQLite connection.  
- **db/queries.py** — Parameterized SQL queries for CRUD and filtering.  
- **scripts/load_data.py** — ETL script that loads and standardizes raw files.  
- **ui/layout.py** — Page layout and navigation for the Streamlit interface.  
- **ui/components.py** — Reusable UI elements (tables, forms, filters).  
- **ui/styles.py** — Centralized styling for consistent presentation.  
- **utils/helpers.py** — Shared utility functions for cleaning and formatting.  
- **utils/caching.py** — Lightweight caching to improve app performance.

---

## Backend Design

The backend performs an ETL-style process:

1. Load multiple Excel files  
2. Standardize and normalize fields  
3. Apply controlled vocabularies  
4. Merge records into a unified relational schema  
5. Tag each record with `engagement_year` to enable longitudinal analysis  

Core functionality includes:

- CRUD operations (create, read, update, delete)  
- Keyword search across structured fields  
- Multi-field filtering  
- Summary table generation  
- Parameterized queries to ensure safe database interaction  

This structure ensures:

- Reduced duplication  
- Improved consistency  
- Reliable multi-year comparisons  
- Clear separation between storage and presentation layers  

---

## Frontend (Streamlit Interface)

The Streamlit application provides:

- A searchable directory of organizations  
- Advanced filtering by industry, region, geography, and size  
- Forms for adding, editing, and deleting records  
- Dynamic charts showing engagement trends  
- A built-in data dictionary documenting fields and controlled vocabularies  

The interface is intentionally simple to demonstrate how structured backend systems can be made accessible to non-technical users without exposing SQL or raw files.

---

## Analytical Capabilities

Once unified in a relational database, the data supports operational and strategic questions such as:

- Which industries do we engage with most frequently?  
- How does engagement vary by region or geography?  
- Are we reaching organizations of different sizes?  
- Which organizations appear across multiple years?  

These insights are difficult to generate reliably when data is siloed across spreadsheets.

---

## Role of Generative AI

Generative AI tools were used to accelerate boilerplate code generation and documentation. Only schema structure and fictional sample data were used in development.

This project demonstrates responsible AI usage for developer productivity while maintaining data privacy boundaries.

---

## Results

With this system, users can:

- Browse all engagement records across 2022–2024  
- Filter and search across structured fields  
- Add, edit, and delete records through validated forms  
- Visualize engagement patterns via charts  
- Reference a clear and documented data dictionary  

The result is a lightweight internal analytics tool that replaces fragmented spreadsheets with a maintainable relational architecture.

---

## Considerations and Constraints

This project is designed as a lightweight internal tool and technical demonstration.

- SQLite is well-suited for small datasets and single-user workflows but not concurrent editing  
- Streamlit is ideal for prototypes and internal tools but does not include built-in authentication  
- Generative AI should not be used with sensitive organizational data  

---

## Scaling the Architecture

A production-ready implementation could substitute:

- PostgreSQL or MySQL for multi-user database needs  
- FastAPI or a similar backend framework for API-based architecture  
- Authentication and role-based permissions  
- Cloud hosting with appropriate security controls  
- Low-code alternatives (e.g., SharePoint + Power Apps or Google AppSheet) for non-technical teams  

The core architectural pattern — ETL + relational schema + controlled vocabularies + UI layer — remains the same. Only the tooling changes.

---

## License

[MIT](https://opensource.org/license/mit)
