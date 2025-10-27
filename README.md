# 💼 Billing & Inventory Management System

A **full-stack Django-based Billing & Inventory Management System** designed to simplify business operations by automating billing, stock management, and invoice generation.  
It provides a seamless workflow for managing products, customers, payments, and real-time sales analytics — all in one scalable platform.

## 🏗️ Features

- 🔐 User Authentication — Secure access for admin and staff  
- 👥 Customer Management — Add, update, and track customer details  
- 📦 Product Inventory — Manage stock levels, auto-update after billing  
- 🧾 Invoice System — Create, view, and print invoices in PDF format  
- 💰 Payments Module — Record and track cash, UPI, card, or bank payments  
- 📊 Analytics Dashboard — Visualize sales, revenue, and stock trends  
- 🕓 Timezone Safe — Automatically adjusts timestamps to local timezone  
- ⚙️ Responsive UI — Built with HTML5, CSS3, Bootstrap 5, and JS  

## 🧠 Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Django (Python) |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Database | MySQL |
| PDF Generation | WeasyPrint / xhtml2pdf |
| Analytics | Plotly Dash |
| DevOps | Git, GitHub, GitHub Actions |
| Tools | VS Code, Postman |

## 📂 Folder Structure

```
billing_system/
│
├── core/                     # Main app: customers, products, invoices, payments
│   ├── models.py             # Database models
│   ├── views.py              # Business logic and rendering
│   ├── urls.py               # Routing for core modules
│   ├── templates/            # HTML pages
│   └── static/               # CSS, JS, and images
│
├── billing_system/           # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── manage.py
```

## ⚙️ Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/sk-sanju/billing-system.git
cd billing-system
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Mac/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Create Superuser
```bash
python manage.py createsuperuser
```

### 6️⃣ Run Server
```bash
python manage.py runserver
```

Then visit 👉 http://127.0.0.1:8000/

## 🧾 Invoice Logic

- Invoice quantity cannot exceed available stock  
- Stock automatically decreases upon successful billing  
- If invoice item is deleted → stock is restored  
- PDF invoices are auto-generated using WeasyPrint  

## 📊 Analytics Dashboard

- Sales trends by date & category  
- Revenue visualization  
- Top-selling products  
- Stock movement insights  

## 🤝 Contributing

Contributions are always welcome!  
1. Fork the repository  
2. Create your feature branch  
3. Commit changes  
4. Push and create a pull request  

## 👨‍💻 Author

**Sanjay S (Sanju)**  
💼 Data Analyst | Python & Django Developer  
🔗 [GitHub](https://github.com/sk-sanju) | [LinkedIn](https://linkedin.com/in/sanjay_s953925)

## 🧩 License

This project is licensed under the **MIT License** — you’re free to modify and use it for your business or research.

⭐ **Star this repo** if you find it helpful!
