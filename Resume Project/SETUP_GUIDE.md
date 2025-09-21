# Resume Relevance Check System - Setup Guide

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the automated setup script
python run_demo.py
```

### Option 2: Manual Setup
Follow the steps below for manual installation and setup.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### 2. Verify Installation

```bash
# Check if all packages are installed correctly
python -c "import fastapi, streamlit, sqlalchemy, spacy; print('All packages installed successfully!')"
```

### 3. Initialize Database

```bash
# Create database tables
python -c "from backend.models.database import create_tables; create_tables(); print('Database initialized!')"
```

## Running the System

### Option 1: Start Both Servers Automatically

```bash
# Start both backend and frontend servers
python start_system.py
```

### Option 2: Start Servers Separately

**Terminal 1 - Backend Server:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend Server:**
```bash
streamlit run frontend/dashboard.py
```

### Option 3: Run Demo with Sample Data

```bash
# Run demo with pre-loaded sample data
python demo.py
```

## Accessing the System

- **Frontend Dashboard**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## System Components

### 1. Frontend Dashboard (Streamlit)
- **URL**: http://localhost:8501
- **Features**:
  - Upload resumes (PDF/DOCX)
  - Create job descriptions
  - Run evaluations
  - View results and analytics
  - Generate reports

### 2. Backend API (FastAPI)
- **URL**: http://localhost:8000
- **Features**:
  - RESTful API endpoints
- **Interactive Documentation**: http://localhost:8000/docs

## Sample Data

The system comes with sample data for testing:

### Sample Resumes (5 files)
- `data/sample_resumes/sample_resume_1.txt` - Software Engineer
- `data/sample_resumes/sample_resume_2.txt` - Data Scientist
- `data/sample_resumes/sample_resume_3.txt` - DevOps Engineer
- `data/sample_resumes/sample_resume_4.txt` - Product Manager
- `data/sample_resumes/sample_resume_5.txt` - Frontend Developer

### Sample Job Descriptions (2 files)
- `data/job_descriptions/sample_jd_1.txt` - Software Engineer Position
- `data/job_descriptions/sample_jd_2.txt` - Data Scientist Position

## Usage Instructions

### 1. Upload a Resume
1. Go to the "Upload Resume" page
2. Select a PDF or DOCX file
3. Click "Upload Resume"
4. View the parsed information

### 2. Create a Job Description
1. Go to the "Upload Job Description" page
2. Fill in the job title, company, and description
3. Click "Upload Job Description"
4. View the extracted requirements

### 3. Run an Evaluation
1. Go to the "Evaluate" page
2. Select a resume and job description
3. Click "Evaluate Resume"
4. View the relevance score and analysis

### 4. View Results
1. Go to the "Results" page
2. Filter and sort evaluations
3. Click "View Detailed Report" for in-depth analysis

### 5. Analytics Dashboard
1. Go to the "Analytics" page
2. View score distributions and trends
3. Analyze performance metrics

## API Usage

### Upload Resume
```bash
curl -X POST "http://localhost:8000/upload/resume" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

### Upload Job Description
```bash
curl -X POST "http://localhost:8000/upload/job-description" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "title=Software Engineer&company=TechCorp&description=Job description text..."
```

### Run Evaluation
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "resume_id=1&job_description_id=1"
```

### Get Results
```bash
curl -X GET "http://localhost:8000/results"
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite:///resume_checker.db

# OpenAI API Key (optional, for enhanced semantic matching)
OPENAI_API_KEY=your_openai_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=uploads
```

### Database Configuration
- **Default**: SQLite (file-based database)
- **Production**: PostgreSQL (recommended for production)

To use PostgreSQL:
1. Install PostgreSQL
2. Create a database
3. Update `DATABASE_URL` in `.env` file:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/resume_checker
   ```

## Troubleshooting

### Common Issues

#### 1. Package Installation Errors
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Install packages one by one
pip install fastapi uvicorn streamlit sqlalchemy
```

#### 2. spaCy Model Download Issues
```bash
# Try downloading with different method
python -m spacy download en_core_web_sm --user

# Or install via conda
conda install -c conda-forge spacy-model-en_core_web_sm
```

#### 3. Port Already in Use
```bash
# Kill processes using the ports
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### 4. Database Connection Issues
```bash
# Delete existing database file and recreate
rm resume_checker.db
python -c "from backend.models.database import create_tables; create_tables()"
```

#### 5. File Upload Issues
- Check file size (max 10MB)
- Ensure file is PDF or DOCX format
- Check file permissions

### Performance Issues

#### 1. Slow Processing
- Ensure spaCy model is properly installed
- Check available RAM (recommended: 4GB+)
- Close other applications

#### 2. Memory Issues
- Process smaller files
- Increase system memory
- Use batch processing for large datasets

## Development

### Project Structure
```
resume-checker/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── models/
│   │   └── database.py        # Database models
│   ├── services/
│   │   └── relevance_analyzer.py  # Analysis engine
│   └── utils/
│       ├── document_parser.py     # Document processing
│       └── job_description_parser.py  # JD parsing
├── frontend/
│   └── dashboard.py           # Streamlit dashboard
├── data/
│   ├── sample_resumes/        # Sample resume files
│   └── job_descriptions/      # Sample job descriptions
├── requirements.txt           # Python dependencies
├── demo.py                   # Demo script
├── start_system.py           # System startup script
└── README.md                 # Project documentation
```

### Adding New Features

1. **Backend**: Add new endpoints in `backend/app.py`
2. **Frontend**: Add new pages in `frontend/dashboard.py`
3. **Processing**: Add new analyzers in `backend/services/`
4. **Database**: Add new models in `backend/models/database.py`

### Testing

```bash
# Run demo to test functionality
python demo.py

# Test API endpoints
curl http://localhost:8000/

# Test frontend
# Open http://localhost:8501 in browser
```

## Production Deployment

### Using Docker (Recommended)

1. Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
EXPOSE 8000 8501

CMD ["python", "start_system.py"]
```

2. Build and run:
```bash
docker build -t resume-checker .
docker run -p 8000:8000 -p 8501:8501 resume-checker
```

### Using Cloud Services

1. **Backend**: Deploy FastAPI to Heroku, AWS, or Google Cloud
2. **Frontend**: Deploy Streamlit to Streamlit Cloud
3. **Database**: Use managed PostgreSQL service
4. **File Storage**: Use cloud storage (AWS S3, Google Cloud Storage)

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check the logs for error messages
4. Ensure all dependencies are properly installed

## License

This project is open source and available under the MIT License.
