<div align="center">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Oracle-F80000?style=for-the-badge&logo=oracle&logoColor=white" />
  <h1>🏢 Housing & Bookings Management System</h1>
  <p><i>A robust, high-performance migration and modernization of a large-scale housing & booking platform.</i></p>
</div>

---

## 📌 Overview
Spearheaded the complete architectural modernization of a legacy Oracle-based housing and booking database into a modern **Django & PostgreSQL** web application. Designed and executed a seamless transition strategy that synchronized live operations across both environments with **zero data loss** or system downtime.

## 🚀 Key Highlights & Impact

> *"Shipped critical infrastructure under pressure, untangled legacy data webs, and kept the servers humming."*

- **Live Data Migration Engine (Smart Sync):** 
  Built a resilient synchronization pipeline using Python to continuously port live data (Contracts, Members, Bookings) from Oracle to Django. Engineered algorithms to handle race conditions, overlaps, and data duplication seamlessly.
- **Surgical Database Refactoring:** 
  Wrote advanced Python scripts utilizing 	ransaction.atomic() to map thousands of active bookings from ghost/duplicate units to verified master records dynamically without disrupting live traffic.
- **Strict Data Integrity:** 
  Implemented bulletproof clean() and save() overrides at the ORM model level to enforce complex business rules, auto-generate timestamps, and aggressively prevent booking collisions.
- **Bare-Metal Problem Solving:** 
  Bypassed restrictive Windows Server & IIS execution policies via custom .bat scripts. Solved deep text-encoding corruption (CP1252 vs UTF-8) by engineering dynamic, index-based data parsers for Excel (openpyxl) reporting.

## 🛠️ Tech Stack
| Category | Technologies |
|---|---|
| **Backend** | Python, Django, Django ORM |
| **Databases** | PostgreSQL, Oracle DB |
| **Data Processing** | openpyxl, pandas, oracledb |
| **Infrastructure** | Windows Server, IIS, PowerShell, Batch Scripts |

## 💡 Technical Challenges Overcome
1. **The Overlapping Bookings Conundrum:** Implemented complex Django QuerySet logic to detect and reject any manual or automated booking that overlapped with existing reservation dates down to the exact check-in/check-out boundaries.
2. **Arabic Encoding in Production:** Fixed silent failures on Windows servers where Arabic column headers in Excel logs were mangled by system encodings, switching the architecture to rely on raw numeric indices.
3. **Safe Multi-System Sync:** Ensured that deleting corrupted data on the new system automatically re-assigned foreign keys (bookings) to the correct master records before executing cascading deletions.

---
<div align="center">
  <i>Built to handle real-world chaos elegantly. Ready for the next big challenge. 🚀</i>
</div>
