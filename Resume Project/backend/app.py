"""
FastAPI backend application for the Resume Relevance Check System.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os
import json
import uuid
from datetime import datetime
import shutil
from pathlib import Path

# Import our modules
from .models.database import get_db, create_tables, Resume, JobDescription, Evaluation
from .utils.document_parser import DocumentParser
from .utils.job_description_parser import JobDescriptionParser
from .services.relevance_analyzer import RelevanceAnalyzer

# Pydantic models
class JobDescriptionRequest(BaseModel):
    title: str
    company: str = ""
    description: str

class EvaluationRequest(BaseModel):
    resume_id: int
    job_description_id: int

# Initialize FastAPI app
app = FastAPI(
    title="Resume Relevance Check System",
    description="AI-powered system for evaluating resume relevance against job descriptions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parsers and analyzer
document_parser = DocumentParser()
jd_parser = JobDescriptionParser()
relevance_analyzer = RelevanceAnalyzer()

# Create upload directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
RESUME_DIR = UPLOAD_DIR / "resumes"
JD_DIR = UPLOAD_DIR / "job_descriptions"
RESUME_DIR.mkdir(exist_ok=True)
JD_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()
    print("Database initialized successfully!")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Resume Relevance Check System API",
        "version": "1.0.0",
        "endpoints": {
            "upload_resume": "/upload/resume",
            "upload_job_description": "/upload/job-description",
            "evaluate": "/evaluate",
            "results": "/results",
            "reports": "/reports/{evaluation_id}"
        }
    }


@app.post("/upload/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume file."""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        filename = f"{file_id}{file_extension}"
        file_path = RESUME_DIR / filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse document
        parsed_data = document_parser.parse_document(str(file_path))
        
        # Extract additional information
        sections = document_parser.extract_sections(parsed_data['text'])
        skills = document_parser.extract_skills(parsed_data['text'])
        education = document_parser.extract_education(parsed_data['text'])
        
        # Create structured data
        structured_data = {
            'sections': sections,
            'skills': skills,
            'education': education,
            'metadata': parsed_data.get('metadata', {})
        }
        
        # Save to database
        resume = Resume(
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_extension[1:].upper(),
            extracted_text=parsed_data['text'],
            parsed_data=json.dumps(structured_data)
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "resume_id": resume.id,
            "filename": resume.filename,
            "file_type": resume.file_type,
            "text_length": len(parsed_data['text']),
            "sections_found": list(sections.keys()),
            "skills_found": skills,
            "education_found": [edu['degree'] for edu in education]
        }
        
    except Exception as e:
        # Clean up file if error occurs
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.post("/upload/job-description")
async def upload_job_description(
    request: JobDescriptionRequest,
    db: Session = Depends(get_db)
):
    """Upload and parse a job description."""
    try:
        # Extract data from request
        title = request.title
        company = request.company
        description = request.description
        
        # Parse job description
        job_data = jd_parser.parse_job_description(description, company)
        job_data.title = title  # Use provided title
        
        # Save to database
        job_description = JobDescription(
            title=job_data.title,
            company=job_data.company,
            description=job_data.description,
            must_have_skills=json.dumps(job_data.must_have_skills),
            nice_to_have_skills=json.dumps(job_data.nice_to_have_skills),
            qualifications=json.dumps(job_data.qualifications),
            experience_required=job_data.experience_required,
            location=job_data.location
        )
        
        db.add(job_description)
        db.commit()
        db.refresh(job_description)
        
        return {
            "message": "Job description uploaded and parsed successfully",
            "job_id": job_description.id,
            "title": job_description.title,
            "company": job_description.company,
            "must_have_skills": job_data.must_have_skills,
            "nice_to_have_skills": job_data.nice_to_have_skills,
            "qualifications": job_data.qualifications,
            "experience_required": job_data.experience_required,
            "location": job_data.location
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing job description: {str(e)}")


@app.post("/evaluate")
async def evaluate_resume(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    """Evaluate resume against job description."""
    try:
        # Extract data from request
        resume_id = request.resume_id
        job_description_id = request.job_description_id
        
        # Get resume and job description from database
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        job_description = db.query(JobDescription).filter(JobDescription.id == job_description_id).first()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        if not job_description:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Prepare data for analysis
        resume_data = {
            'text': resume.extracted_text,
            'parsed_data': json.loads(resume.parsed_data) if resume.parsed_data else {}
        }
        
        job_data = {
            'description': job_description.description,
            'must_have_skills': json.loads(job_description.must_have_skills) if job_description.must_have_skills else [],
            'nice_to_have_skills': json.loads(job_description.nice_to_have_skills) if job_description.nice_to_have_skills else [],
            'qualifications': json.loads(job_description.qualifications) if job_description.qualifications else [],
            'experience_required': job_description.experience_required
        }
        
        # Perform relevance analysis
        relevance_score = relevance_analyzer.analyze_relevance(resume_data, job_data)
        
        # Save evaluation to database
        evaluation = Evaluation(
            resume_id=resume_id,
            job_description_id=job_description_id,
            relevance_score=relevance_score.overall_score,
            hard_match_score=relevance_score.hard_match_score,
            semantic_match_score=relevance_score.semantic_match_score,
            education_match_score=relevance_score.education_match_score,
            experience_match_score=relevance_score.experience_match_score,
            verdict=relevance_score.verdict,
            missing_skills=json.dumps(relevance_score.missing_skills),
            suggestions=json.dumps(relevance_score.suggestions),
            detailed_report=json.dumps(relevance_score.detailed_breakdown)
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        return {
            "message": "Evaluation completed successfully",
            "evaluation_id": evaluation.id,
            "resume_id": resume_id,
            "job_description_id": job_description_id,
            "relevance_score": relevance_score.overall_score,
            "verdict": relevance_score.verdict,
            "scores": {
                "overall": relevance_score.overall_score,
                "hard_match": relevance_score.hard_match_score,
                "semantic_match": relevance_score.semantic_match_score,
                "education_match": relevance_score.education_match_score,
                "experience_match": relevance_score.experience_match_score
            },
            "missing_skills": relevance_score.missing_skills,
            "suggestions": relevance_score.suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during evaluation: {str(e)}")


@app.get("/results")
async def get_results(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all evaluation results."""
    try:
        evaluations = db.query(Evaluation).offset(skip).limit(limit).all()
        
        results = []
        for eval in evaluations:
            # Get resume and job description info
            resume = db.query(Resume).filter(Resume.id == eval.resume_id).first()
            job_desc = db.query(JobDescription).filter(JobDescription.id == eval.job_description_id).first()
            
            results.append({
                "evaluation_id": eval.id,
                "resume_filename": resume.filename if resume else "Unknown",
                "job_title": job_desc.title if job_desc else "Unknown",
                "company": job_desc.company if job_desc else "Unknown",
                "relevance_score": eval.relevance_score,
                "verdict": eval.verdict,
                "created_at": eval.created_at.isoformat()
            })
        
        return {
            "results": results,
            "total": len(results),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")


@app.get("/reports/{evaluation_id}")
async def get_detailed_report(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed report for a specific evaluation."""
    try:
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        # Get resume and job description info
        resume = db.query(Resume).filter(Resume.id == evaluation.resume_id).first()
        job_desc = db.query(JobDescription).filter(JobDescription.id == evaluation.job_description_id).first()
        
        # Parse JSON fields
        missing_skills = json.loads(evaluation.missing_skills) if evaluation.missing_skills else []
        suggestions = json.loads(evaluation.suggestions) if evaluation.suggestions else []
        detailed_report = json.loads(evaluation.detailed_report) if evaluation.detailed_report else {}
        
        return {
            "evaluation_id": evaluation.id,
            "resume_info": {
                "filename": resume.filename if resume else "Unknown",
                "file_type": resume.file_type if resume else "Unknown",
                "uploaded_at": resume.created_at.isoformat() if resume else None
            },
            "job_info": {
                "title": job_desc.title if job_desc else "Unknown",
                "company": job_desc.company if job_desc else "Unknown",
                "location": job_desc.location if job_desc else "Unknown",
                "created_at": job_desc.created_at.isoformat() if job_desc else None
            },
            "scores": {
                "overall": evaluation.relevance_score,
                "hard_match": evaluation.hard_match_score,
                "semantic_match": evaluation.semantic_match_score,
                "education_match": evaluation.education_match_score,
                "experience_match": evaluation.experience_match_score
            },
            "verdict": evaluation.verdict,
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "detailed_breakdown": detailed_report,
            "created_at": evaluation.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving report: {str(e)}")


@app.get("/resumes")
async def get_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all uploaded resumes."""
    try:
        resumes = db.query(Resume).offset(skip).limit(limit).all()
        
        results = []
        for resume in resumes:
            parsed_data = json.loads(resume.parsed_data) if resume.parsed_data else {}
            results.append({
                "id": resume.id,
                "filename": resume.filename,
                "file_type": resume.file_type,
                "text_length": len(resume.extracted_text),
                "skills": parsed_data.get('skills', []),
                "uploaded_at": resume.created_at.isoformat()
            })
        
        return {
            "resumes": results,
            "total": len(results),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resumes: {str(e)}")


@app.get("/job-descriptions")
async def get_job_descriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all uploaded job descriptions."""
    try:
        job_descriptions = db.query(JobDescription).offset(skip).limit(limit).all()
        
        results = []
        for jd in job_descriptions:
            results.append({
                "id": jd.id,
                "title": jd.title,
                "company": jd.company,
                "location": jd.location,
                "experience_required": jd.experience_required,
                "must_have_skills": json.loads(jd.must_have_skills) if jd.must_have_skills else [],
                "nice_to_have_skills": json.loads(jd.nice_to_have_skills) if jd.nice_to_have_skills else [],
                "created_at": jd.created_at.isoformat()
            })
        
        return {
            "job_descriptions": results,
            "total": len(results),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving job descriptions: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
