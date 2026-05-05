# 🏥 e-Roster: Pharmacy Staff Scheduling System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)

> A full-stack web application built to solve a real operational problem: pharmacy managers relying on Excel spreadsheets for staff scheduling, leading to version conflicts, unclear ownership, and inefficient communication.

---

## 🔍 The Problem

At the pharmacy where I work, shift schedules were created manually in Excel, printed out, and corrected by hand when changes were needed. There was no single source of truth, no visibility for staff, and no way to track historical changes.

I built e-Roster to replace this process with a structured, role-based web application that anyone on the team can access and use.

---

## ✨ Features

| Feature | Description |

| 🗓 Shift Management | Create, edit, and delete shifts with configurable time slots and contextual notes |
| 👥 Role-Based Access | Four user types: Manager, Full-time, Part-time, and Casual staff — each with different permissions |
| 📋 Leave Requests | Staff can submit leave requests; managers can approve or decline |
| 🔄 Shift Swaps | Shift swap functionality with traceable assignment history |
| 💰 Payroll Integration | Planned integration with third-party accounting APIs (e.g. Xero) for payslip visibility |

---

## 🛠 Tech Stack

| Category | Technology |

| Backend | Python, Django REST Framework |
| Frontend | React (AI-assisted development) |
| Database | PostgreSQL |
| Backend Deployment | Render |
| Frontend Deployment | Vercel |
| Tools | Git, GitHub, Python Virtual Environment |

---

## 💡 Technical Highlights

- **Database Design** — Independently designed the schema, modelling real-world pharmacy workflows into structured PostgreSQL relationships across multiple tables

- **Role-Based API** — Built a Django REST API with role-based permissions, ensuring each user type only accesses relevant data and actions

- **Remote Database Development** — Connected to a remote PostgreSQL instance during local development via VS Code, running migrations and managing tables without a local PostgreSQL installation

- **AI-Assisted Frontend** — Developed the React frontend using AI-assisted tools to visualise backend data and make the system accessible to non-technical users. Backend logic alone is invisible to end users, so the frontend was essential to bridge that gap and allow real people to interact with and benefit from the system

- **Cloud Deployment** — Deployed backend to Render and frontend to Vercel after initial AWS testing, transitioning to manage infrastructure costs

---

## 🏗 Architecture Overview

```
Frontend (React / Vercel)
        ↕ REST API
Backend (Django / Render)
        ↕
Database (PostgreSQL)
```

---

## 🎯 Purpose

This project was built from direct observation of a real operational gap, not from a tutorial or brief. The goal was to translate a genuine workplace problem into a working digital solution, and to gain hands-on experience in full-stack development, cloud deployment, and role-based system design.

---

## 🔗 Related Repository

- **Frontend:** [pharmacy_roster_system_front](https://github.com/gawe0925/pharmacy_roster_system_front)
