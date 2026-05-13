# 🏭 Warehouse Management System

A Python-based dynamic warehouse tracking and reporting system built with PySide6 and MySQL. Designed for logistics companies and 3PL providers to manage stock, locations, customers, and products in real time.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- **Real-time stock tracking** by customer, product, and warehouse location
- **Daily movement recording** — Inbound (IN), Outbound (OUT), and Transfer
- **Dashboard** with KPI cards and 7-day bar chart
- **Weekly & monthly reports** auto-generated every Monday and 1st of month
- **Excel & PDF export** for all report types
- **Multi-customer support** — manage multiple customers in a single warehouse
- **Location management** — aisle, rack, and bin level tracking
- **Low stock alerts** — visual warnings for items below threshold

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI | PySide6 (Qt6) |
| Database | MySQL 8.0+ |
| ORM | SQLAlchemy 2.x |
| Reporting | openpyxl, reportlab |
| Charts | PySide6 QtCharts |
| Data | pandas |

---

## 📋 Requirements

- Python 3.10 or higher
- MySQL 8.0 or higher
- Windows 10/11, macOS 12+, or Ubuntu 20.04+

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/BatuhanARK/Warehouse.git
cd Warehouse
```

### 2. Create and activate virtual environment

```bash
# Create
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up MySQL database

Open MySQL Workbench or any MySQL client and run:

```sql
CREATE DATABASE warehouse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wms_user'@'localhost' IDENTIFIED BY 'Wms2026!';
GRANT ALL PRIVILEGES ON warehouse_db.* TO 'wms_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure database connection

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Then edit `.env`:

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=warehouse_db
DB_USER=wms_user
DB_PASSWORD=your_password_here
```

### 6. Initialize the database

```bash
python main.py
```

This will automatically create all required tables on first run.

### 7. (Optional) Load sample data

```bash
python -m utils.seed_data
```

This generates sample customers, products, locations, and movements across the previous month, current month, and next month.

---

## 📁 Project Structure

```
Warehouse/
├── main.py                   # Application entry point
├── config.py                 # Database configuration
├── requirements.txt          # Python dependencies
├── models/                   # SQLAlchemy ORM models
│   ├── customer.py
│   ├── product.py
│   ├── location.py
│   ├── stock.py
│   └── movement.py
├── services/                 # Business logic layer
│   ├── customer_service.py
│   ├── product_service.py
│   ├── location_service.py
│   ├── stock_service.py
│   ├── movement_service.py
│   └── report_service.py
├── ui/                       # PySide6 user interface
│   ├── main_window.py
│   ├── dashboard.py
│   ├── movements.py
│   ├── stock_view.py
│   ├── customers.py
│   ├── products.py
│   ├── locations.py
│   └── reports.py
├── utils/
│   ├── table_helper.py
│   ├── base_dialog.py
│   ├── scheduler.py
│   └── seed_data.py
└── raporlar/                 # Auto-generated reports (gitignored)
    ├── haftalik/             # Weekly Excel reports
    └── aylik/                # Monthly Excel reports
```

---

## 📖 Usage Guide

### Navigation

Use the left sidebar to navigate between modules:

| Module | Description |
|---|---|
| 📊 Dashboard | Real-time KPI cards and 7-day movement chart |
| 📦 Stock | Browse and filter current stock levels |
| 🔄 Movements | Record inbound, outbound, and transfer movements |
| 👥 Customers | Add and manage customers |
| 🛒 Products | Manage product catalog with SKU |
| 📍 Locations | Define warehouse map (aisles, racks, bins) |
| 📈 Reports | Generate and export movement and stock reports |

### Recording a Movement

1. Go to **🔄 Movements**
2. Click **+ New Movement**
3. Select movement type: **IN** (inbound), **OUT** (outbound), or **TRANSFER**
4. Select customer, product, location, and quantity
5. Enter a reference number (e.g. PO-2026-001) and click **Save**

### Generating Reports

1. Go to **📈 Reports**
2. Select report type tab: Movement Report, Stock Report, or Customer Report
3. Set date range and filters
4. Click **📊 Generate Report**
5. Export to **Excel** or **PDF**

### Automatic Reports

The scheduler runs in the background automatically:
- **Every Monday** — generates last week's movement report
- **Every 1st of the month** — generates last month's movement and stock reports

Reports are saved to:

```
raporlar/
├── haftalik/    ← weekly reports
└── aylik/       ← monthly reports
```

---

## 🗄️ Database Schema

| Table | Description |
|---|---|
| `customers` | Customer master data |
| `products` | Product catalog with SKU |
| `locations` | Warehouse location map |
| `stock` | Current inventory snapshot |
| `movements` | Immutable movement audit log |

---

## 📦 Dependencies

```
PySide6>=6.6.0
SQLAlchemy>=2.0.0
pymysql>=1.1.0
cryptography>=41.0.0
pandas>=2.0.0
openpyxl>=3.1.0
reportlab>=4.0.0
python-dateutil>=2.9.0
six>=1.16.0
python-dotenv>=1.0.0
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
