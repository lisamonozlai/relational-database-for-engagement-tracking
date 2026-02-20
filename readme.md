# Designing an Interactive, Relational Database with SQL, Python, Streamlit & GenAI
##### Author: [Lisa Monozlai](https://www.linkedin.com/in/lisamonozlai/)
---

## How to View the Demo

A live version of the interactive database is available here:

**[View the demo](https://your-demo-link-here.com)**

This shows how lightweight code deployed to [Streamlit](https://streamlit.io/) can help non-technical users browse, filter, update, and visualize program data.

---

## About

This project demonstrates how a small team can move from multiple spreadsheets to a simple relational database with an interactive interface. The goal is to show what becomes possible when program data is stored in a structured format rather than scattered across files. All data in this demo is **fictional** and exists only to illustrate how structured fields, controlled vocabularies, and relational storage work in practice.

You will also find in this project an approach to collecting demographic data that has been adapted from **[Candid's Philanthropy Classification System](https://taxonomy.candid.org/populations)**.

---

## Challenge

A hypothetical grantmaking organization wants to keep track of its grants and grantees. It runs multiple programs, and data for those programs lives in separate spreadsheets:

- `program_data_1.xlsx` 
- `program_data_2.xlsx` 

The team needs a simple, lightweight way to explore the data and to add, edit, or delete grantees. They do not have dedicated IT staff or money for expensive software. They need something using tools that are free, accessible, and easy to learn.

---

## Solution

#### Tools Used and Why

- **SQL** to store data in a structured format that supports reliable queries.  
- **Python** to connect spreadsheets, the database, and the interface.  
- **SQLite** as a lightweight, file based database suitable for small teams.  
- **Streamlit** to create a simple web interface that non technical users can navigate.  
- **Generative AI** (for example, Microsoft Copilot in an MS365 environment) to accelerate development by generating scaffolding, boilerplate code, and documentation without exposing any sensitive data.

#### Backend

Using Python in [VS Code](https://code.visualstudio.com/), the backend loads two separate spreadsheets into a single SQLite table. It links records using the primary key Unique ID, tags each record with the program name, and exposes functions for adding, editing, deleting, searching, filtering, and summarizing records. This unified structure reduces duplication and makes cross program comparisons immediate.

#### Frontend

The frontend is also written in Python and deployed through Streamlit. It provides forms, filters, tables, and charts that allow non technical users to interact with the database without touching SQL or the underlying files. This prevents inaccurate or inconsistent data from being introduced and skewing results. 

#### Role of Generative AI

A secure generative AI tool can help a non-technical team set up this system quickly. AI can generate the initial database structure, boilerplate functions, and UI scaffolding. Because only the structure of the data model is shared, and no identifying information is provided, this is a safe and appropriate use of AI for accelerating development.

---

## Results

With this system, the team can use the interface to:

- view a directory of all grantees  
- run keyword searches  
- apply structured filters  
- add, edit, and delete records through forms  
- view charts summarizing funding by mission, region, and population served  
- reference a data dictionary that explains each field  

The structured database also allows the team to answer common program questions, such as:

- How does funding distribution differ across the two programs?
- Which missions receive the most investment?  
- Which populations or regions are most frequently served?  
- Are there gaps in the types of organizations being supported?  

These insights come from the structure, not from complex analytics. Even a minimal relational setup can support meaningful decision-making.

---

## Considerations and Constraints

This project is a demonstration. It is not intended for sensitive data or enterprise scale use.

**SQLite** is suitable for small datasets and single user access. It is not designed for concurrent editing or regulated data.  
**Streamlit** is ideal for prototypes and internal tools. It does not provide authentication or role based permissions.  
**Generative AI** should not be used to process sensitive program data. It is appropriate for generating structure and scaffolding.

If an organization wanted to adopt this pattern for production, they would likely use:

- **PostgreSQL** or **MySQL** for the database  
- **Django**, **FastAPI**, or **Flask** for backend logic  
- A frontend framework with authentication  
- Cloud hosting with proper security controls  

The pattern remains the same. Only the tools change to meet production requirements.

## License

[MIT](https://opensource.org/license/mit)