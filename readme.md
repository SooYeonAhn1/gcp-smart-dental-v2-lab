# 🦷 Smart Dental Lab Matching API

This project provides a Flask-based backend API for matching dental clinics with dental labs based on lab type, services offered, pricing, turnaround time (TAT), queue capacity, and real-time availability. Labs are maintained in Google Firestore and deployed as a serverless microservice on Google Cloud Run.

---

## 🚀 Features

- Match labs based on **service type** and **lab specialization**
- Respond with real-time **availability** based on lab capacity & queue
- Maintain a **queue system** to balance lab workload
- Simple, RESTful API endpoints
- Fully containerized with Docker and deployable via Google Cloud Build & Cloud Run

---

## 🛠️ Tech Stack

- **Backend:** Flask (`app.py`)
- **Database:** Google Cloud Firestore
- **Deployment:** Docker, Cloud Build, Google Cloud Run
- **Cloud Integration:** `google-cloud-firestore`, `firebase-admin`
- **WSGI Server:** Gunicorn

---

## 📦 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/smart-dental-lab-matching.git
cd smart-dental-lab-matching