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

## 📦 Wanna contribute?
Here's how you can get started:

### 1. Clone your fork

```bash
git clone https://github.com/<your-username>/gcp-smart-dental-v2-lab.git
cd gcp-smart-dental-v2-lab
```

### 2. Create a new `branch` for your feature
```bash
git checkout -b feature/your-feature-name
```
Examples:
feature/add-authentication
fix/capacity-calculation-bug
docs/improved-readme

### 3. Make your changes
```bash
git add .
git commit -m "<your changes>"
```

### 4. Push your branch
```bash
git push origin feature/your-feature-name
```
### 5. Create a pull request
I. Go to your fork on Github:
```bash
https://github.com/<your-username>/gcp-smart-dental-v2-lab
```
II. And click `Compare & Pull Request`

III. Once reviewed and approved, your changes will be merged!

## 📌 After Merge: Keeping the Fork Updated
Here's what you can do as contributor to keep your fork in sync with the original repo:
```bash
git checkout main
git pull upstream main
git push origin main
```
## 🧩 Here's how the flow works
```
Main Repo
    ↑
Pull Request
    ↑
Contributor Fork
    ↑
feature/new-feature
```