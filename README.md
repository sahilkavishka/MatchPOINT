# 🏏 Sports Manager — Tournament & Team Management Web Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-Full--Stack-092E20?logo=django)](https://www.djangoproject.com/)
[![MySQL](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-4479A1?logo=mysql)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-success)](#)

Sports Manager is a full-stack web application developed with **Django**, engineered to streamline sports tournament organization, team administration, player rosters, and fan engagement through a centralized, secure platform.

---

## 📌 Features & Highlights

* **🔐 Secure Authentication & Access Control:**
  * User registration and login protected with email-based OTP verification for account recovery and password resets.
  * Role-based permissions differentiating between tournament organizers, team managers, and regular users.

* **👥 Team & Roster Management:**
  * Create, edit, and manage sports teams.
  * Register individual players, assign positions, and organize squads.

* **🏆 Tournament Management & Scheduling:**
  * Create new sports tournaments with defined formats, categories, and timelines.
  * Seamless team registration into active tournaments with squad validation.

* **💬 Social & Community Engagement:**
  * Like and comment on tournaments, matches, and team updates.
  * Public community boards to build enthusiasm around local leagues.

* **🔍 Real-Time Search & Filtering:**
  * Instant filter and search controls to discover tournaments by sport, district, date, or status.

* **📱 Responsive & Modern UI:**
  * Built using Bootstrap 5, custom CSS styling, and vanilla JavaScript for smooth client-side interactions.

---

## 🛠️ Tech Stack

* **Backend:** Python, Django Web Framework
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
* **Database:** MySQL / SQLite
* **Authentication:** Django Auth + Custom Email OTP Verification

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/sahilkavishka/MatchPOINT.git
cd MatchPOINT
```

### 2. Set up virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install requirements
```bash
pip install django mysqlclient pillow
```

### 4. Configure database and migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser & start dev server
```bash
python manage.py createsuperuser
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your web browser.

---

## 👨‍💻 Author

**Sahil Kavishka**  
*Data Science Undergraduate @ Sabaragamuwa University of Sri Lanka*  
* [LinkedIn](https://www.linkedin.com/in/sahilkavishka/)
* [GitHub](https://github.com/sahilkavishka)
* [Portfolio](https://sahilkavishka.github.io/portfolio/)
