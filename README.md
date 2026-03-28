# 🍽️ RestaurantAPI

A Django REST Framework backend for a restaurant ordering system - covering menu management, cart operations, transactional order placement, and role-based access control across three distinct user roles.

The design focuses on clean permission boundaries, predictable state transitions, and backend-only REST API structure without server-rendered templates.

> Python · Django · Django REST Framework · SQLite · Djoser

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-092E20?style=flat&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Djoser](https://img.shields.io/badge/Djoser-092E20?style=flat&logo=django&logoColor=white)

---

## 📋 Overview

| Area | Approach |
|---|---|
| 🔐 Authentication | Token-based auth via Djoser and DRF `authtoken` |
| 🛡️ Authorisation | Group-based RBAC - Customer, Manager, Delivery Crew |
| 🏗️ Architecture | Standard Django layered - URLs → Views → Serializers → Models |
| 🛒 Cart | Per-user cart with deduplication and server-side price calculation |
| 📦 Orders | Transactional order creation with cart-to-order conversion |
| 🔍 Querying | Filtering, search, ordering, and pagination across key endpoints |

---

## 🏗️ System Design

### 🔐 Authentication

Authentication is handled through Djoser and DRF token authentication. Users register via `/api/users/`, obtain a token via `/api/token/login/`, and include that token in the `Authorization` header on subsequent requests. Django's built-in `User` model is used — no custom user model.

---

### 🛡️ Role-Based Access Control

Roles are implemented using Django's built-in `Group` model — no custom role tables. Three groups govern access:

- **Customer** - menu browsing, cart management, order placement, own order visibility
- **Manager** - full menu control, staff group assignment, all order visibility and management
- **Delivery Crew** - assigned order visibility and delivery status updates only

Managers and Delivery Crew are explicitly blocked from customer-facing cart and order creation endpoints. Permissions are enforced at the view level through DRF permission classes combined with group membership checks.

---

### 🛒 Cart & Order Flow

Cart entries deduplicate on `(user, menuitem)` - adding the same item again increments quantity and recalculates the line price rather than creating a duplicate row. Cart totals are computed server-side.

Order creation is wrapped in a database transaction:

1. Cart is validated - empty cart raises an error
2. An `Order` record is created for the user
3. Each cart row is converted to an `OrderItem` with price snapshot
4. Total order value is calculated and stored
5. Cart is cleared after successful commit

`OrderItem` stores `menuitem`, `quantity`, and `price` as a snapshot - decoupled from live catalog data so historical order values remain consistent regardless of future menu price changes.

---

### 🧱 Architecture

```text
URLs → Views → Serializers → Models → SQLite
```

| Layer | Responsibility |
|---|---|
| Views | Request handling, permission enforcement, response shaping |
| Serializers | Field mapping, business logic, nested reads |
| Models | Data structure and relationships |
| Permissions | Role and group-based access control |

---

## 🔑 Role & Permission Matrix

| Action | Customer | Manager | Delivery Crew |
|---|---|---|---|
| Browse menu | ✅ | ✅ | ✅ |
| Create / update / delete menu items | ❌ | ✅ | ❌ |
| Manage staff groups | ❌ | ✅ | ❌ |
| Cart operations | ✅ | ❌ | ❌ |
| Place orders | ✅ | ❌ | ❌ |
| View own orders | ✅ | ✅ | ❌ |
| View all orders | ❌ | ✅ | ❌ |
| View assigned orders | ❌ | ❌ | ✅ |
| Assign delivery crew | ❌ | ✅ | ❌ |
| Update delivery status | ❌ | ✅ | ✅ |
| Delete orders | ❌ | ✅ | ❌ |

---

## 📡 API Reference

### 🔐 Auth

| Method | Endpoint |
|---|---|
| `POST` | `/api/users/` |
| `POST` | `/api/token/login/` |
| `POST` | `/api/token/logout/` |

### 👥 Group Management

| Method | Endpoint |
|---|---|
| `GET` | `/api/groups/<group_name>/users` |
| `POST` | `/api/groups/<group_name>/users` |
| `DELETE` | `/api/groups/<group_name>/users/<userId>` |

### 🍴 Menu

| Method | Endpoint |
|---|---|
| `GET` | `/api/menu-items/` |
| `POST` | `/api/menu-items/` |
| `GET` | `/api/menu-items/<pk>/` |
| `PUT` | `/api/menu-items/<pk>/` |
| `PATCH` | `/api/menu-items/<pk>/` |
| `DELETE` | `/api/menu-items/<pk>/` |

### 🛒 Cart

| Method | Endpoint |
|---|---|
| `GET` | `/api/cart/menu-items/` |
| `POST` | `/api/cart/menu-items/` |
| `DELETE` | `/api/cart/menu-items/` |

### 📦 Orders

| Method | Endpoint |
|---|---|
| `GET` | `/api/orders/` |
| `POST` | `/api/orders/` |
| `GET` | `/api/orders/<pk>/` |
| `PUT` | `/api/orders/<pk>/` |
| `PATCH` | `/api/orders/<pk>/` |
| `DELETE` | `/api/orders/<pk>/` |

---

## 🔍 Filtering, Search & Pagination

| Endpoint | Filter | Search | Order By |
|---|---|---|---|
| Menu items | `category`, `featured` | `title`, `category` | `price`, `title` |
| Orders | `status`, `date` | `id`, `username` | `date`, `order_value` |

Global pagination: page-number based, page size of 5.

---

## 📂 Project Structure

```text
LittleLemon/
├── LittleLemon/         → Project config, root URLs, WSGI/ASGI
└── LittleLemonAPI/      → Models, serializers, views, permissions, routes, migrations
```

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) |
| Framework | ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-092E20?style=flat&logo=django&logoColor=white) |
| Auth | ![Djoser](https://img.shields.io/badge/Djoser-092E20?style=flat&logo=django&logoColor=white) |
| Database | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) |
| Filtering | django-filter |

---

## 🚀 Running Locally

### Prerequisites

- 🐍 Python 3.x
- 📦 pip
- 🔧 Pipenv (`pip install pipenv`)

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/syed-anas-a/restaurant-api.git
cd restaurant-api
```

**2. Activate the Pipenv shell**

```bash
pipenv shell
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root**

```env
SECRET_KEY=your_secret_key
DEBUG=True
```

**5. Apply migrations**

```bash
python manage.py migrate
```

**6. Run the application**

```bash
python manage.py runserver
```

Backend runs at `http://localhost:8000`

---

## ✅ Implementation Highlights

- Token-based authentication via Djoser with protected endpoints
- Group-based RBAC across Customer, Manager, and Delivery Crew with explicit permission boundaries
- Cart deduplication - same item increments quantity rather than duplicating rows
- Transactional order creation - cart-to-order conversion with price snapshots and cart cleanup in a single DB transaction
- Role-aware order visibility and update permissions enforced at the view level
- Filtering, search, ordering, and pagination across menu and order endpoints

---

## 🔭 Future Development

- Extended restaurant modeling - online table booking, reservations, and offline order support
- Payment integration - Stripe or Razorpay
- MySQL migration from SQLite for production readiness
- Frontend UI

---

## 📝 Background

Built as the capstone project for the Meta Backend Developer Professional Certificate. Being iteratively extended beyond the course scope with additional features and architectural improvements.
