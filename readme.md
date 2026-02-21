# Building a Lightweight Relational Engagement Tracker with Python, SQL and Streamlit  
##### Author: [Lisa Monozlai](https://www.linkedin.com/in/lisamonozlai/)
---

## About

This project demonstrates how organizations can move from scattered spreadsheets to a lightweight relational database. It shows what becomes possible when engagement data is stored in a structured, queryable format rather than siloed across files.

All data in this demo is fictional and is used to illustrate:

- how relational storage improves consistency  
- how controlled vocabularies reduce ambiguity  
- how a simple UI makes structured data accessible to non technical users  
- how multi year engagement patterns emerge once data is unified  

---

## Live Demo

→ **[Click to View](https://tbd.streamlit.app/)**

The interface allows users to browse, filter, update, and visualize multi year engagement data without risking accidental edits to the original files.

---

## Challenge

To ground the demo, it uses a fictional scenario where a team wants to understand which organizations they engage with each year. Their data lives in three separate spreadsheets:

- `engagement_data_2022.xlsx`  
- `engagement_data_2023.xlsx`  
- `engagement_data_2024.xlsx`  

Although the files share similar fields, the team cannot easily:

- view all years together  
- filter by industry, region, or organization size  
- compare engagement patterns across years  
- update records without editing spreadsheets  
- maintain consistent vocabularies  

They need a simple, low cost, low maintenance solution that works with familiar tools.

---

## Solution

### Tools Used

- **Python** for cleaning, merging, and standardizing multi year data  
- **SQLite** as a lightweight relational database  
- **SQL** for structured storage and reliable queries  
- **Streamlit** for an intuitive, non technical interface  
- **Generative AI** (for example, Microsoft Copilot) to accelerate scaffolding and documentation  

### Backend

The backend loads three Excel files, standardizes their fields, and merges them into a single relational table. Each record is tagged with an `engagement_year`, which enables multi year comparisons.

It provides functions for:

- adding, editing, and deleting records  
- keyword search  
- structured filtering  
- generating summary tables  

This structure ensures consistency and reduces the risk of data corruption.

### Frontend

The Streamlit frontend includes:

- a directory of all organizations  
- keyword search and advanced filters  
- forms for adding, editing, and deleting records  
- charts showing engagement patterns by industry and geography  
- a data dictionary that documents each field and vocabulary  

The UI is intentionally simple so non technical users can interact with the data without touching SQL or the underlying files.

### Role of Generative AI

Generative AI supports rapid development by generating boilerplate code, documentation, and UI scaffolding. Because only the structure of the data model is shared and no identifying information is provided, this is a safe and appropriate use of AI.

---

## Results

With this system, users can:

- browse all organizations engaged across 2022 to 2024  
- filter by industry, region, geography, or employee size  
- run keyword searches across names and descriptions  
- add, edit, and delete records through controlled forms  
- view charts that summarize engagement patterns  
- reference a clear data dictionary  

The structured database also supports common operational questions, such as:

- Which industries do we engage with most often?
- How does engagement vary by region or geography?  
- Are we reaching organizations of different sizes?  
- Which organizations appear across multiple years?  

---

## Considerations and Constraints

This project is a demonstration and represents one approach to working with structured data. It is not intended for sensitive data or enterprise scale use.

- **SQLite** is suitable for small datasets and single user access, but not concurrent editing  
- **Streamlit** is ideal for prototypes and internal tools, but does not include authentication  
- **Generative AI** should not be used to process sensitive organizational data  

A production ready version might use:

- **PostgreSQL**, **MySQL**, **FastAPI**, or similar tools for teams with technical capacity  
- **MS SharePoint with Power Apps** or **Google AppSheet** for low code environments  
- A frontend with authentication and role based permissions  
- Cloud hosting with appropriate security controls  

The architectural pattern remains the same. Only the tools change.

---

## License

[MIT](https://opensource.org/license/mit)