# 🏠 Decision Support System for Accommodation Search

> **IT4341 – Decision Support Systems | Master's Program | SOICT – HUST**

A decision support system designed to help customers find suitable rental accommodations based on their personalized criteria.

---

## 📌 Overview

This project builds a **Decision Support System (DSS)** that assists users in discovering and selecting rental properties that match their needs — including location, price range, area, room type, and surrounding environment.

**Project Objectives:**
- Collect, clean, and preprocess real-world housing rental data.
- Apply decision support algorithms to rank and recommend suitable accommodations.
- Expose a RESTful API backend built with **FastAPI** and **PostgreSQL**.
- Deliver a responsive web frontend using **JavaScript**, **HTML**, and **CSS**.
- Containerize the entire system with **Docker** for easy deployment.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Analysis | Python, Jupyter Notebook |
| Backend API | FastAPI, Python, PostgreSQL (psycopg2) |
| Frontend | JavaScript, HTML, CSS (Jinja2 templates) |
| Deployment | Docker, Docker Compose |

---

## 📁 Project Structure

```
Decision_Support_System/
├── api/                    # FastAPI backend (main.py, model.py, function.py)
├── app/
│   ├── server/             # Application server logic
│   ├── web/                # Frontend web assets
│   └── requirements.txt    # Python dependencies
├── data/                   # Raw and processed datasets
├── documents/              # Project documentation
├── images/                 # Screenshots and diagrams
├── official-build/
│   ├── app/                # Production app configuration
│   ├── notebook/           # Jupyter notebooks for deployment
│   └── docker-compose.yaml # Docker Compose configuration
├── reports/                # Project reports
├── source-code/
│   └── pre-process-data/   # Data preprocessing scripts
└── README.md
```

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/db-check` | Database connection check |
| `GET` | `/provinces` | Get list of provinces |
| `GET` | `/districts/{province_id}` | Get districts by province |
| `GET` | `/wards/{district_id}` | Get wards by district |
| `GET` | `/house_types` | Get distinct house types |
| `GET` | `/contract_periods` | Get distinct contract periods |
| `POST` | `/search` | Search for accommodations |
| `POST` | `/house_rents_details` | Get details for a list of properties |

---

## 🚀 Deployment

**Prerequisites:** [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) must be installed.

```bash
cd official-build && docker-compose up -d --build
```

Once running, open your browser and navigate to `http://localhost:8000`.

---

## 📄 Reports & Documents

| File | Link |
|---|---|
| 📋 Project Planning | [DSS - planning.docx](https://github.com/Tran-Ngoc-Bao/Decision_Support_System/blob/master/reports/DSS%20-%20planning.docx) |
| 📝 Final Report (Word) | [report.docx](https://github.com/Tran-Ngoc-Bao/Decision_Support_System/blob/master/reports/report.docx) |
| 📄 Final Report (PDF) | [report.pdf](https://github.com/Tran-Ngoc-Bao/Decision_Support_System/blob/master/reports/report.pdf) |

---

## 👥 Team Members

| Name | Role |
|---|---|
| Hoàng Nhật Minh | Software Development |
| Trần Ngọc Bảo | Data Processing & Analysis |

---

## 📜 License

This project was developed as part of the academic curriculum at the  
**School of Information and Communication Technology – Hanoi University of Science and Technology (HUST)**.
