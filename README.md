**1. Dashboard Overview**
<img width="1911" height="862" alt="Screenshot 2026-09-08 094327" src="https://github.com/user-attachments/assets/75abee44-7d2e-45a2-ad4f-02c1293734c6" />
**2. Dataset Statistics**
<img width="1917" height="865" alt="Screenshot 2026-09-08 094133" src="https://github.com/user-attachments/assets/17d6998e-0f86-489a-8634-c3ca763362d4" />
**3. Generate Visualizations**
<img width="1913" height="868" alt="Screenshot 2026-09-08 093939" src="https://github.com/user-attachments/assets/c04b05bd-c2fd-469f-9140-ff8d59194d74" />
**4. Agent Chat**
<img width="1917" height="862" alt="Screenshot 2026-09-08 093901" src="https://github.com/user-attachments/assets/cf1e03b0-3a91-41dc-a4cf-fc910da944b5" />
[![Live Demo](https://img.shields.io/badge/Demo-Live%20App-brightgreen)](https://data-sense-ai-ksif.vercel.app/dashboard)
# DataSense AI

DataSense AI is an interactive platform built to make dataset exploration, cleaning, and analysis effort-free. It combines automated data processing with conversational AI so you can ask questions, transform data, and build charts using natural language.

---

## Key Features

- Conversational Data Analysis: Ask questions in plain English. The platform converts queries into safe Pandas code to generate inline summary tables, counts, and insights.
- Data Cleaning Toolkit: Remove duplicates, fill missing values with multiple strategies, standardize and normalize data, encode categorical variables, remove outliers, and extract date features.
- Interactive Visualizations: Generate bar charts, line charts, scatter plots, box plots, histograms, and correlation heatmaps dynamically with Plotly.
- Automated Data Profiling: Upload CSV, Excel, JSON, or Parquet files to inspect summary statistics, data quality warnings, missing values, and inferred types.

---

## Tech Stack

- Backend: FastAPI, Python 3.11+, Pandas, NumPy, Scikit-learn, Plotly, SQLAlchemy, SQLite
- Frontend: React 18, TypeScript, Tailwind CSS, TanStack Query, Vite
- AI: OpenAI API

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key (optional for basic app usage, but required for natural-language chat and smart summaries)

### 1. Clone the Repository

```bash
git clone https://github.com/Kaoserahamed/datasense-ai.git
cd datasense-ai
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Create a .env file
cat > .env <<EOF
OPENAI_API_KEY=your-key-here
APP_NAME=DataSense AI
DEBUG=True
UPLOAD_DIR=uploads
EOF

# Run the backend server
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Run the frontend client
npm run dev
```

### Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Project Structure

```text
datasense-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers and endpoints
│   │   ├── ai/           # LLM and analysis helpers
│   │   ├── services/     # Business logic and data operations
│   │   ├── models/       # Database models
│   │   ├── repositories/ # Data access layer
│   │   ├── schemas/      # Request/response schemas
│   │   ├── core/         # Configuration
│   │   └── database/     # Database setup
│   ├── uploads/          # Uploaded datasets
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── services/     # API integration
│   │   └── layouts/      # Shared layout components
│   └── package.json
└── README.md
```

---

## Main API Routes

- Projects: POST /projects, GET /projects, GET /projects/{id}, PUT /projects/{id}, DELETE /projects/{id}
- Datasets: POST /datasets, GET /datasets/project/{project_id}, GET /datasets/{id}, DELETE /datasets/{id}
- Chat: POST /chat/ask, GET /chat/history/{dataset_id}, DELETE /chat/history/{chat_id}
- Analysis: POST /analysis/stats, GET /analysis/correlation/{dataset_id}, GET /analysis/value-counts/{dataset_id}/{column}
- Visualization: POST /visualization/bar-chart, POST /visualization/line-chart, POST /visualization/pie-chart, POST /visualization/scatter-plot, POST /visualization/histogram, POST /visualization/box-plot, POST /visualization/heatmap, POST /visualization/auto-chart
- Cleaning: POST /cleaning/remove-duplicates, POST /cleaning/fill-missing, POST /cleaning/drop-missing, POST /cleaning/standardize, POST /cleaning/normalize, POST /cleaning/encode-categorical, POST /cleaning/remove-outliers, POST /cleaning/parse-dates


