# Automated Resume Relevance Check System

An AI-powered system that evaluates resume relevance against job descriptions using both keyword matching and semantic analysis.

## Features

- **Document Processing**: Support for PDF and DOCX resume files
- **Intelligent Parsing**: Extract and clean text from resumes and job descriptions
- **Dual Matching**: Hard keyword matching + semantic similarity analysis
- **Comprehensive Scoring**: Weighted relevance scoring (0-100)
- **Detailed Reports**: Missing skills, suggestions, and improvement recommendations
- **Web Dashboard**: Streamlit-based interface for recruiters
- **Database Storage**: PostgreSQL/SQLite for storing evaluations and results

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Resume Upload │    │  JD Upload      │    │   Web Dashboard │
│   (PDF/DOCX)    │    │  (Text/File)    │    │   (Streamlit)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Flask/FastAPI         │
                    │     Backend Server        │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Document Processing     │
                    │   • PDF/DOCX Parsing     │
                    │   • Text Extraction      │
                    │   • NLP Preprocessing    │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Relevance Analysis      │
                    │   • Hard Matching (TF-IDF)│
                    │   • Semantic Matching     │
                    │   • Weighted Scoring      │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Report Generation       │
                    │   • Scores & Metrics      │
                    │   • Missing Skills        │
                    │   • Improvement Tips      │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Database Storage        │
                    │   (PostgreSQL/SQLite)     │
                    └───────────────────────────┘
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. Set up environment variables (create `.env` file):
   ```
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///resume_checker.db
   ```

## Usage

1. Start the backend server:
   ```bash
   python backend/app.py
   ```

2. Launch the Streamlit dashboard:
   ```bash
   streamlit run frontend/dashboard.py
   ```

3. Access the dashboard at `http://localhost:8501`

## Project Structure

```
resume-checker/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── models/                # Database models
│   ├── services/              # Business logic
│   └── utils/                 # Utility functions
├── frontend/
│   └── dashboard.py           # Streamlit dashboard
├── data/
│   ├── resumes/               # Sample resume files
│   └── job_descriptions/      # Sample job descriptions
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## API Endpoints

- `POST /upload/resume` - Upload resume file
- `POST /upload/job-description` - Upload job description
- `POST /evaluate` - Evaluate resume against job description
- `GET /results` - Get evaluation results
- `GET /reports/{evaluation_id}` - Generate detailed report

## Scoring Algorithm

The system uses a weighted scoring approach:

1. **Hard Matching (40%)**: TF-IDF + fuzzy matching for exact skills/keywords
2. **Semantic Matching (40%)**: Embedding-based similarity for contextual alignment
3. **Education Match (10%)**: Degree and certification matching
4. **Experience Match (10%)**: Years of experience and role relevance

Final score ranges from 0-100 with verdicts:
- **High (80-100)**: Excellent match
- **Medium (60-79)**: Good match with some gaps
- **Low (0-59)**: Poor match, significant improvements needed
