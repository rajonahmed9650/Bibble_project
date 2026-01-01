# Bible Journey Backend API

##  Project Overview
Bible Journey is a faith-based application that guides users through structured
daily spiritual journeys. Each journey consists of multiple days, and each day
includes steps such as Prayer, Devotion, Action, Reflection, and Quiz.

This repository contains the **Backend API** built with Django Rest Framework.

---

## Features
- User Authentication (JWT based)
- Subscription-based access control
- Journey & Day progression system
- Daily steps (Prayer, Devotion, Action, Quiz)
- Reflection notes storage
- Quiz submission & progress tracking
- Admin panel for content management

---

##  Tech Stack
- **Backend:** Django 5.x, Django Rest Framework
- **Database:**  SQLite (development)
- **Authentication:** JWT
- **Scheduler:** APScheduler (for background tasks)
- **Payments:** Stripe
- **Caching:**  Django Cache

---

## 📂 Project Structure

bibble_project/
│
├── accounts/ # User authentication & profiles
├── journey/ # Journey & days management
├── userprogress/ # User journey & day progress
├── subscriptions/ # Stripe subscription logic
├── manage.py
└── requirements.txt