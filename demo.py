"""
Demo script for the Resume Relevance Check System.
This script demonstrates the system with sample data.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Add backend to path
sys.path.append('backend')

from models.database import create_tables
from utils.document_parser import DocumentParser
from utils.job_description_parser import JobDescriptionParser
from services.relevance_analyzer import RelevanceAnalyzer

# Configuration
API_BASE_URL = "http://localhost:8000"
SAMPLE_DATA_DIR = Path("data")

def setup_database():
    """Initialize the database."""
    print("Setting up database...")
    create_tables()
    print("Database setup complete!")

def upload_sample_resumes():
    """Upload sample resumes to the system."""
    print("\nUploading sample resumes...")
    
    resume_dir = SAMPLE_DATA_DIR / "sample_resumes"
    parser = DocumentParser()
    
    uploaded_resumes = []
    
    for resume_file in resume_dir.glob("*.txt"):
        print(f"Processing {resume_file.name}...")
        
        try:
            # Read the text file as if it were a resume
            with open(resume_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Create a mock parsed data structure
            parsed_data = {
                'text': text,
                'raw_text': text,
                'metadata': {},
                'file_type': 'TXT',
                'page_count': 1
            }
            
            # Extract additional information
            sections = parser.extract_sections(text)
            skills = parser.extract_skills(text)
            education = parser.extract_education(text)
            
            structured_data = {
                'sections': sections,
                'skills': skills,
                'education': education,
                'metadata': {}
            }
            
            # Simulate API upload
            resume_info = {
                'filename': resume_file.name,
                'file_type': 'TXT',
                'text': text,
                'structured_data': structured_data
            }
            
            uploaded_resumes.append(resume_info)
            print(f"✓ {resume_file.name} processed successfully")
            
        except Exception as e:
            print(f"✗ Error processing {resume_file.name}: {e}")
    
    return uploaded_resumes

def upload_sample_job_descriptions():
    """Upload sample job descriptions to the system."""
    print("\nUploading sample job descriptions...")
    
    jd_dir = SAMPLE_DATA_DIR / "job_descriptions"
    parser = JobDescriptionParser()
    
    uploaded_jds = []
    
    for jd_file in jd_dir.glob("*.txt"):
        print(f"Processing {jd_file.name}...")
        
        try:
            with open(jd_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Parse job description
            job_data = parser.parse_job_description(text)
            
            # Extract company from filename or text
            if "techcorp" in jd_file.name.lower():
                job_data.company = "TechCorp Inc."
            elif "datacorp" in jd_file.name.lower():
                job_data.company = "DataCorp Analytics"
            
            uploaded_jds.append(job_data)
            print(f"✓ {jd_file.name} processed successfully")
            
        except Exception as e:
            print(f"✗ Error processing {jd_file.name}: {e}")
    
    return uploaded_jds

def run_evaluations(resumes, job_descriptions):
    """Run evaluations between resumes and job descriptions."""
    print("\nRunning evaluations...")
    
    analyzer = RelevanceAnalyzer()
    evaluations = []
    
    for i, resume in enumerate(resumes):
        for j, job_desc in enumerate(job_descriptions):
            print(f"Evaluating Resume {i+1} vs Job Description {j+1}...")
            
            try:
                # Prepare data for analysis
                resume_data = {
                    'text': resume['text'],
                    'parsed_data': resume['structured_data']
                }
                
                job_data = {
                    'description': job_desc.description,
                    'must_have_skills': job_desc.must_have_skills,
                    'nice_to_have_skills': job_desc.nice_to_have_skills,
                    'qualifications': job_desc.qualifications,
                    'experience_required': job_desc.experience_required
                }
                
                # Perform analysis
                result = analyzer.analyze_relevance(resume_data, job_data)
                
                evaluation = {
                    'resume': resume['filename'],
                    'job_title': job_desc.title,
                    'company': job_desc.company,
                    'overall_score': result.overall_score,
                    'verdict': result.verdict,
                    'hard_match_score': result.hard_match_score,
                    'semantic_match_score': result.semantic_match_score,
                    'education_match_score': result.education_match_score,
                    'experience_match_score': result.experience_match_score,
                    'missing_skills': result.missing_skills,
                    'suggestions': result.suggestions
                }
                
                evaluations.append(evaluation)
                print(f"✓ Score: {result.overall_score}% - {result.verdict}")
                
            except Exception as e:
                print(f"✗ Error evaluating Resume {i+1} vs Job Description {j+1}: {e}")
    
    return evaluations

def display_results(evaluations):
    """Display evaluation results in a formatted table."""
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    
    for i, eval in enumerate(evaluations, 1):
        print(f"\nEvaluation {i}:")
        print(f"Resume: {eval['resume']}")
        print(f"Job: {eval['job_title']} at {eval['company']}")
        print(f"Overall Score: {eval['overall_score']}%")
        print(f"Verdict: {eval['verdict']}")
        print(f"Hard Match: {eval['hard_match_score']}%")
        print(f"Semantic Match: {eval['semantic_match_score']}%")
        print(f"Education Match: {eval['education_match_score']}%")
        print(f"Experience Match: {eval['experience_match_score']}%")
        
        if eval['missing_skills']:
            print(f"Missing Skills: {', '.join(eval['missing_skills'][:5])}")
            if len(eval['missing_skills']) > 5:
                print(f"... and {len(eval['missing_skills']) - 5} more")
        
        if eval['suggestions']:
            print("Suggestions:")
            for j, suggestion in enumerate(eval['suggestions'][:3], 1):
                print(f"  {j}. {suggestion}")
        
        print("-" * 80)

def generate_summary_report(evaluations):
    """Generate a summary report of all evaluations."""
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)
    
    total_evaluations = len(evaluations)
    high_scores = len([e for e in evaluations if e['overall_score'] >= 80])
    medium_scores = len([e for e in evaluations if 60 <= e['overall_score'] < 80])
    low_scores = len([e for e in evaluations if e['overall_score'] < 60])
    
    print(f"Total Evaluations: {total_evaluations}")
    print(f"High Relevance (80%+): {high_scores} ({high_scores/total_evaluations*100:.1f}%)")
    print(f"Medium Relevance (60-79%): {medium_scores} ({medium_scores/total_evaluations*100:.1f}%)")
    print(f"Low Relevance (<60%): {low_scores} ({low_scores/total_evaluations*100:.1f}%)")
    
    # Average scores by category
    avg_overall = sum(e['overall_score'] for e in evaluations) / total_evaluations
    avg_hard = sum(e['hard_match_score'] for e in evaluations) / total_evaluations
    avg_semantic = sum(e['semantic_match_score'] for e in evaluations) / total_evaluations
    avg_education = sum(e['education_match_score'] for e in evaluations) / total_evaluations
    avg_experience = sum(e['experience_match_score'] for e in evaluations) / total_evaluations
    
    print(f"\nAverage Scores:")
    print(f"Overall: {avg_overall:.1f}%")
    print(f"Hard Match: {avg_hard:.1f}%")
    print(f"Semantic Match: {avg_semantic:.1f}%")
    print(f"Education Match: {avg_education:.1f}%")
    print(f"Experience Match: {avg_experience:.1f}%")
    
    # Best matches
    best_matches = sorted(evaluations, key=lambda x: x['overall_score'], reverse=True)[:3]
    print(f"\nTop 3 Matches:")
    for i, match in enumerate(best_matches, 1):
        print(f"{i}. {match['resume']} vs {match['job_title']} - {match['overall_score']}%")

def main():
    """Main demo function."""
    print("Resume Relevance Check System - Demo")
    print("="*50)
    
    # Setup
    setup_database()
    
    # Upload sample data
    resumes = upload_sample_resumes()
    job_descriptions = upload_sample_job_descriptions()
    
    if not resumes:
        print("No resumes found. Please add sample resumes to data/sample_resumes/")
        return
    
    if not job_descriptions:
        print("No job descriptions found. Please add sample job descriptions to data/job_descriptions/")
        return
    
    # Run evaluations
    evaluations = run_evaluations(resumes, job_descriptions)
    
    if not evaluations:
        print("No evaluations completed.")
        return
    
    # Display results
    display_results(evaluations)
    generate_summary_report(evaluations)
    
    print("\n" + "="*80)
    print("Demo completed successfully!")
    print("You can now start the web dashboard with: streamlit run frontend/dashboard.py")
    print("And the API server with: python backend/app.py")
    print("="*80)

if __name__ == "__main__":
    main()
