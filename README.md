# TRIACT - A Full-Stack Inventory Management System

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)

TRIACT is a full-stack web application designed for small shop owners to manage inventory, track sales and profits, handle employees, and generate invoices efficiently.

## Features

- **Role-Based Authentication:** Separate accounts and interfaces for Owners and Employees.
- **Comprehensive Owner Dashboard:** At-a-glance KPIs for revenue, profit, units sold, and product count, with charts for sales trends and category performance.
- **Full Product Management:** A dedicated page to add, edit (price, cost, stock), and filter all products. Includes an intelligent category suggestion system.
- **Employee Management:** A complete interface to add, remove, and edit employees, including a payroll system to track and mark salary payments.
- **Point of Sale (POS):** A "Smart POS" page for creating orders with a fast, searchable product grid and category filters.
- **Automatic PDF Invoice Generation:** Invoices are automatically created, saved, and linked to each order.
- **In-App Notifications:** Real-time alerts for owners when any product's stock runs low.
- **OCR Invoice Scanning:** Upload an image of an invoice, and the app will use OCR to extract items and check them against your inventory.

## Tech Stack

- **Frontend:** React (Vite), JavaScript, Tailwind CSS, Chart.js
- **Backend:** Next.js API Routes (Node.js)
- **Database:** MongoDB (with Mongoose)
- **Authentication:** JSON Web Tokens (JWT)

---

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- A MongoDB Atlas account (the free tier is sufficient)
- Git

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/TRIACT.git](https://github.com/your-username/TRIACT.git)
cd TRIACT
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Install all necessary packages:

```bash
npm install
```

Create your own environment file by copying the example:

```bash
cp .env.example .env
```

Open the new .env file and add your MongoDB Connection String and a unique JWT Secret.

### 3. Frontend Setup

In a separate terminal, navigate to the frontend directory:

```bash
cd frontend
```

Install all necessary packages:

```bash
npm install
```

### Running the Application

Seed the Database (First time only):  
In your backend terminal, run the seed script. This will wipe the database and populate it with a large set of realistic sample data.

```bash
npm run seed
```

Start the Backend Server:  
In your backend terminal, run:

```bash
npm run dev
```

The backend API will now be running at http://localhost:3001.

Start the Frontend Server:  
In your frontend terminal, run:

```bash
npm run dev
```

The React application will now be running at http://localhost:5173.

---

### Test Credentials

You can log in and explore the application using the pre-made sample accounts:

**Owner Account:**

Email: owner1@example.com

Password: Password123

**Employee Account:**

Email: rahul@example.com

Password: Password123



# 🛍️ TRIACT RAG (Gemini-powered AI Assistant)

This module implements a Retrieval-Augmented Generation (RAG) pipeline for TRIACT.
It allows owners and employees to ask natural language questions about shop data (sales, stock, invoices) and get AI-powered answers using Google Gemini AI.

📂 Project Structure
```
triact-rag/
│── server.py          # FastAPI backend (RAG query endpoint)
│── ingestion.py       # Script to load, chunk, and embed shop data
│── requirements.txt   # Python dependencies
```
⚙️ Setup Instructions
1. Create a Virtual Environment
## Windows
```bash
python -m venv venv
venv\Scripts\activate
```
## Mac/Linux
```
python3 -m venv venv
source venv/bin/activate
```
## 2. Install Dependencies
```
pip install -r requirements.txt
```

## 3. Set Up Environment Variables

### Create .env inside triact-rag/:
```
MONGO_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net
MONGO_DB=triact
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_EMBEDDING_MODEL=text-embedding-004   # or your chosen Gemini embedding model
GEMINI_GENERATIVE_MODEL=gemini-2.5-flash      # for generation in server.py
JWT_SECRET=your_jwt_secret
```

## 5.📥 Data Ingestion

Run:
```
python ingestion.py
```

This will:

Load shop documents (invoices, stock, sales, etc.)

Chunk them into smaller pieces

Generate embeddings using Gemini

Save them into MongoDB (embeddings collection)

## 6.🚀 Run the RAG Server
```
uvicorn server:app --port 8011 --reload
```

- Server → http://localhost:8011
- Server/docs → http://localhost:8011/docs

🔗 API Endpoints
Query RAG
```
POST /api/rag/query

Request body:

{
  "query": "What is the recent sold stock?"
}
```

Headers:
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

Response:
```
{
  "answer": "The most recently sold stock was 20 units of Product X on Sept 30."
}
```
🖥️ Frontend Integration

In your React frontend:
```
async function askRag(query, jwtToken) {
  const resp = await fetch("http://localhost:8000/api/rag/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${jwtToken}`
    },
    body: JSON.stringify({ query })
  });
  return await resp.json();
}
```

Use this inside your dashboard Chat component.
