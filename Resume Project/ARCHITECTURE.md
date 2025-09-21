# Resume Relevance Check System - Architecture

## System Overview

The Resume Relevance Check System is a comprehensive AI-powered platform that evaluates resume relevance against job descriptions using both keyword matching and semantic analysis. The system consists of multiple components working together to provide accurate, actionable insights for recruiters and HR professionals.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit Dashboard (frontend/dashboard.py)                  │
│  • Resume Upload Interface                                    │
│  • Job Description Upload Interface                           │
│  • Evaluation Results Display                                 │
│  • Analytics Dashboard                                        │
│  • Report Generation                                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Server (backend/app.py)                              │
│  • Document Upload Endpoints                                  │
│  • Evaluation Processing                                      │
│  • Results Management                                         │
│  • Report Generation                                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Document Parser (backend/utils/document_parser.py)           │
│  • PDF Processing (PyMuPDF, pdfplumber)                       │
│  • DOCX Processing (python-docx, docx2txt)                    │
│  • Text Extraction & Cleaning                                 │
│  • Section Identification                                     │
│  • Skill Extraction                                           │
│                                                                 │
│  Job Description Parser (backend/utils/job_description_parser.py) │
│  • Text Analysis & Parsing                                    │
│  • Skill Extraction                                           │
│  • Requirement Identification                                 │
│  • Qualification Parsing                                      │
│                                                                 │
│  Relevance Analyzer (backend/services/relevance_analyzer.py)  │
│  • Hard Matching (TF-IDF + Fuzzy Matching)                    │
│  • Semantic Matching (Sentence Transformers)                  │
│  • Education Matching                                         │
│  • Experience Matching                                        │
│  • Weighted Scoring Algorithm                                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  Database (SQLite/PostgreSQL)                                 │
│  • Resumes Table                                              │
│  • Job Descriptions Table                                     │
│  • Evaluations Table                                          │
│  • Users Table (for admin features)                           │
│                                                                 │
│  File Storage                                                 │
│  • Uploaded Resume Files (PDF/DOCX)                           │
│  • Generated Reports                                          │
│  • Temporary Processing Files                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Streamlit Dashboard** (`frontend/dashboard.py`)
- **Purpose**: User interface for recruiters and HR professionals
- **Features**:
  - Resume upload and management
  - Job description creation and editing
  - Evaluation execution and monitoring
  - Results visualization and analytics
  - Report generation and export
- **Technology**: Streamlit, Plotly, Pandas

### 2. Backend Layer

**FastAPI Server** (`backend/app.py`)
- **Purpose**: RESTful API server handling all business logic
- **Endpoints**:
  - `POST /upload/resume` - Upload and parse resume files
  - `POST /upload/job-description` - Upload and parse job descriptions
  - `POST /evaluate` - Run relevance analysis
  - `GET /results` - Retrieve evaluation results
  - `GET /reports/{id}` - Get detailed reports
- **Technology**: FastAPI, Uvicorn, Pydantic

### 3. Processing Layer

#### Document Parser (`backend/utils/document_parser.py`)
- **PDF Processing**: Uses PyMuPDF and pdfplumber for robust text extraction
- **DOCX Processing**: Uses python-docx and docx2txt for Word document parsing
- **Text Cleaning**: Removes headers, footers, and formatting artifacts
- **Section Extraction**: Identifies resume sections (experience, education, skills)
- **Skill Extraction**: Uses regex patterns to identify technical skills

#### Job Description Parser (`backend/utils/job_description_parser.py`)
- **Text Analysis**: Parses job description text for structured information
- **Skill Extraction**: Identifies required and preferred skills
- **Requirement Parsing**: Extracts education, experience, and qualification requirements
- **Metadata Extraction**: Identifies company, location, salary, and job type

#### Relevance Analyzer (`backend/services/relevance_analyzer.py`)
- **Hard Matching (40% weight)**:
  - TF-IDF vectorization for document similarity
  - Fuzzy string matching for skill alignment
  - Keyword extraction and matching
- **Semantic Matching (40% weight)**:
  - Sentence transformer embeddings
  - Cosine similarity calculation
  - Contextual understanding of requirements
- **Education Matching (10% weight)**:
  - Degree level comparison
  - Field of study alignment
  - Certification matching
- **Experience Matching (10% weight)**:
  - Years of experience comparison
  - Role relevance assessment
  - Career progression analysis

### 4. Data Layer

#### Database Schema
- **Resumes Table**: Stores resume metadata and extracted text
- **Job Descriptions Table**: Stores job posting information and requirements
- **Evaluations Table**: Stores analysis results and scores
- **Users Table**: Manages user accounts and permissions

#### File Storage
- **Upload Directory**: Stores original resume files
- **Report Directory**: Stores generated reports and exports
- **Temporary Directory**: Handles processing intermediate files

## Data Flow

1. **Upload Phase**:
   - User uploads resume via Streamlit interface
   - File is saved to upload directory
   - Document parser extracts and cleans text
   - Structured data is stored in database

2. **Job Description Phase**:
   - User inputs job description via web form
   - Job description parser extracts requirements
   - Structured data is stored in database

3. **Evaluation Phase**:
   - User selects resume and job description for comparison
   - Relevance analyzer processes both documents
   - Multiple scoring algorithms are applied
   - Results are stored in database

4. **Reporting Phase**:
   - Results are retrieved from database
   - Detailed reports are generated
   - Visualizations are created for dashboard
   - Export options are provided

## Scoring Algorithm

The system uses a weighted scoring approach:

```
Overall Score = (Hard Match × 0.4) + (Semantic Match × 0.4) + 
                (Education Match × 0.1) + (Experience Match × 0.1)
```

### Score Ranges:
- **High (80-100%)**: Excellent match, strong candidate
- **Medium (60-79%)**: Good match with some gaps
- **Low (0-59%)**: Poor match, significant improvements needed

## Technology Stack

### Backend:
- **Python 3.8+**
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Database ORM
- **spaCy**: Natural language processing
- **scikit-learn**: Machine learning and TF-IDF
- **sentence-transformers**: Semantic embeddings
- **fuzzywuzzy**: Fuzzy string matching

### Frontend:
- **Streamlit**: Rapid web app development
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation and analysis

### Database:
- **SQLite**: Default database (development)
- **PostgreSQL**: Production database option

### Document Processing:
- **PyMuPDF**: PDF text extraction
- **pdfplumber**: PDF processing fallback
- **python-docx**: DOCX processing
- **docx2txt**: DOCX processing fallback

## Deployment Options

### Development:
1. Run `python start_system.py` for full system
2. Or run components separately:
   - Backend: `python backend/app.py`
   - Frontend: `streamlit run frontend/dashboard.py`

### Production:
1. Use PostgreSQL for database
2. Deploy FastAPI with Gunicorn/Uvicorn
3. Use Nginx as reverse proxy
4. Deploy Streamlit with Streamlit Cloud or Docker
5. Configure environment variables for API keys

## Security Considerations

- File upload validation and sanitization
- SQL injection prevention through ORM
- Input validation and error handling
- Secure file storage and access controls
- API rate limiting and authentication (future enhancement)

## Performance Optimizations

- Database indexing on frequently queried fields
- Caching of parsed documents and embeddings
- Asynchronous processing for large files
- Connection pooling for database operations
- Lazy loading of large text fields

## Future Enhancements

- **Machine Learning Models**: Custom ML models for better matching
- **Real-time Processing**: WebSocket support for live updates
- **Advanced Analytics**: More sophisticated reporting and insights
- **Integration APIs**: Connect with ATS systems and job boards
- **Mobile App**: Native mobile application
- **Multi-language Support**: Support for non-English resumes
- **AI-powered Suggestions**: GPT integration for improvement recommendations
