# 🏥 e-Roster: Pharmacy Staff Scheduling System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)

> A full-stack web application built to solve a real operational problem: pharmacy managers relying on Excel spreadsheets for staff scheduling, leading to version conflicts, unclear ownership, and inefficient communication.

---

## 🔍 Overview

A full-stack rostering system prototype designed to replace manual Excel-based scheduling workflows in a pharmacy environment.

The system focuses on backend architecture, role-based access control, scheduling workflows, and REST API design using Django and PostgreSQL.

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

- **Frontend Integration** — Used AI-assisted React development to build a user interface for roster visibility and interaction with backend scheduling workflows

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

Built to explore backend-driven workflow improvements for real operational scheduling problems in a pharmacy environment.

---

## 🔗 Related Repository

- **Frontend:** [pharmacy_roster_system_front](https://github.com/gawe0925/pharmacy_roster_system_front)
