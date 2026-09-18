# Housing & Booking Management System (Migration & Modernization)

## 📌 Project Overview
Spearheaded the development and migration of a large-scale Housing and Booking Management System for military and civilian personnel. The project involved replacing a legacy Oracle-based database with a modern, robust Django web application, ensuring zero data loss during transition and synchronizing live operations between the two systems.

## 🚀 Key Responsibilities & Achievements

### 1. Complex Data Migration & Synchronization (Smart Sync)
- Developed a highly resilient **Python-based Smart Sync engine** to continuously migrate live data (Members, Contracts, Civilian Bookings, and Cancellations) from a legacy Oracle database to the new Django PostgreSQL environment.
- Engineered intelligent deduplication algorithms to handle conflicting records, ensuring data integrity by updating existing records rather than overwriting or duplicating them (e.g., matching bookings by Unit ID, Start Date, and End Date).
- Automated the reporting of synchronization conflicts by exporting edge-case records to Excel (openpyxl), enabling safe manual review without halting the sync process.

### 2. Database Refactoring & Data Integrity 
- Successfully identified and eliminated legacy data anomalies, including duplicate physical units and overlapping booking dates.
- Wrote safe database transaction scripts (	ransaction.atomic()) to remap thousands of active bookings from ghost/duplicate units to their verified master records dynamically, reducing database bloat and UI confusion.
- Implemented robust clean() and save() validations at the Django Model level to enforce strict business rules, such as auto-populating contract creation dates and aggressively preventing double-booking overlaps.

### 3. Server Deployment & System Administration
- Handled production deployment on Windows Server (IIS), writing custom batch scripts (.bat) to bypass PowerShell execution policy restrictions and automate continuous database maintenance routines.
- Resolved complex text encoding issues (CP1252 vs UTF-8) that were corrupting Arabic data imports from Excel files by dynamically parsing data via exact column index mapping rather than error-prone string headers.

## 🛠️ Tech Stack & Tools
- **Backend Framework:** Django, Python
- **Databases:** PostgreSQL (New), Oracle DB (Legacy)
- **Data Processing:** openpyxl, pandas, oracledb
- **Infrastructure & OS:** Windows Server, IIS, PowerShell/Batch scripting, Virtual Environments

## 💡 "Vibe Coder" Highlights
- **Shipped under pressure:** Iterated rapidly on live production servers, deploying hotfixes for structural database issues without bringing down the system.
- **Problem Solver:** Translated confusing legacy data relationships into a clean, modern ORM architecture while maintaining backward compatibility for ongoing legacy operations.
