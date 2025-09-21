"""
Test script to verify the Resume Relevance Check System is working correctly.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test backend imports
        from models.database import create_tables, Resume, JobDescription, Evaluation
        from utils.document_parser import DocumentParser
        from utils.job_description_parser import JobDescriptionParser
        from services.relevance_analyzer import RelevanceAnalyzer
        print("✓ Backend imports successful")
    except ImportError as e:
        print(f"✗ Backend import error: {e}")
        return False
    
    try:
        # Test frontend imports
        import streamlit
        import pandas
        import plotly
        print("✓ Frontend imports successful")
    except ImportError as e:
        print(f"✗ Frontend import error: {e}")
        return False
    
    try:
        # Test ML/NLP imports
        import spacy
        import sklearn
        import sentence_transformers
        print("✓ ML/NLP imports successful")
    except ImportError as e:
        print(f"✗ ML/NLP import error: {e}")
        return False
    
    return True

def test_spacy_model():
    """Test if spaCy model is available."""
    print("Testing spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model loaded successfully")
        return True
    except OSError as e:
        print(f"✗ spaCy model error: {e}")
        print("Please install with: python -m spacy download en_core_web_sm")
        return False

def test_database():
    """Test database functionality."""
    print("Testing database...")
    
    try:
        from models.database import create_tables
        create_tables()
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_document_parser():
    """Test document parsing functionality."""
    print("Testing document parser...")
    
    try:
        from utils.document_parser import DocumentParser
        parser = DocumentParser()
        
        # Test with sample text
        sample_text = """
        John Smith
        Software Engineer
        Skills: Python, JavaScript, React
        Experience: 3 years
        Education: Bachelor in Computer Science
        """
        
        sections = parser.extract_sections(sample_text)
        skills = parser.extract_skills(sample_text)
        education = parser.extract_education(sample_text)
        
        print(f"✓ Document parser working - Found {len(skills)} skills, {len(education)} education entries")
        return True
    except Exception as e:
        print(f"✗ Document parser error: {e}")
        return False

def test_job_description_parser():
    """Test job description parsing functionality."""
    print("Testing job description parser...")
    
    try:
        from utils.job_description_parser import JobDescriptionParser
        parser = JobDescriptionParser()
        
        # Test with sample job description
        sample_jd = """
        Software Engineer Position
        Requirements: Python, JavaScript, 3+ years experience
        Education: Bachelor in Computer Science
        """
        
        result = parser.parse_job_description(sample_jd, "Test Company")
        
        print(f"✓ Job description parser working - Title: {result.title}")
        return True
    except Exception as e:
        print(f"✗ Job description parser error: {e}")
        return False

def test_relevance_analyzer():
    """Test relevance analysis functionality."""
    print("Testing relevance analyzer...")
    
    try:
        from services.relevance_analyzer import RelevanceAnalyzer
        analyzer = RelevanceAnalyzer()
        
        # Test with sample data
        resume_data = {
            'text': 'Software Engineer with Python and JavaScript experience',
            'parsed_data': {}
        }
        
        job_data = {
            'description': 'Looking for Python developer with 3+ years experience',
            'must_have_skills': ['Python', 'JavaScript'],
            'nice_to_have_skills': ['React'],
            'qualifications': ['Bachelor in Computer Science'],
            'experience_required': '3+ years'
        }
        
        result = analyzer.analyze_relevance(resume_data, job_data)
        
        print(f"✓ Relevance analyzer working - Score: {result.overall_score}%")
        return True
    except Exception as e:
        print(f"✗ Relevance analyzer error: {e}")
        return False

def test_sample_data():
    """Test if sample data files exist."""
    print("Testing sample data...")
    
    sample_files = [
        "data/sample_resumes/sample_resume_1.txt",
        "data/sample_resumes/sample_resume_2.txt",
        "data/sample_resumes/sample_resume_3.txt",
        "data/sample_resumes/sample_resume_4.txt",
        "data/sample_resumes/sample_resume_5.txt",
        "data/job_descriptions/sample_jd_1.txt",
        "data/job_descriptions/sample_jd_2.txt"
    ]
    
    missing_files = []
    for file_path in sample_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing sample files: {missing_files}")
        return False
    else:
        print("✓ All sample data files present")
        return True

def run_full_test():
    """Run a complete test of the system."""
    print("Running full system test...")
    
    try:
        from models.database import create_tables
        from utils.document_parser import DocumentParser
        from utils.job_description_parser import JobDescriptionParser
        from services.relevance_analyzer import RelevanceAnalyzer
        
        # Initialize components
        create_tables()
        doc_parser = DocumentParser()
        jd_parser = JobDescriptionParser()
        analyzer = RelevanceAnalyzer()
        
        # Load sample data
        sample_resume_path = "data/sample_resumes/sample_resume_1.txt"
        sample_jd_path = "data/job_descriptions/sample_jd_1.txt"
        
        if not Path(sample_resume_path).exists() or not Path(sample_jd_path).exists():
            print("✗ Sample data files not found")
            return False
        
        # Parse sample resume
        with open(sample_resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        resume_data = {
            'text': resume_text,
            'parsed_data': {
                'sections': doc_parser.extract_sections(resume_text),
                'skills': doc_parser.extract_skills(resume_text),
                'education': doc_parser.extract_education(resume_text)
            }
        }
        
        # Parse sample job description
        with open(sample_jd_path, 'r', encoding='utf-8') as f:
            jd_text = f.read()
        
        job_data = jd_parser.parse_job_description(jd_text, "Test Company")
        
        # Run analysis
        result = analyzer.analyze_relevance(resume_data, job_data)
        
        print(f"✓ Full system test successful!")
        print(f"  Resume: {sample_resume_path}")
        print(f"  Job Description: {sample_jd_path}")
        print(f"  Relevance Score: {result.overall_score}%")
        print(f"  Verdict: {result.verdict}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full system test error: {e}")
        return False

def main():
    """Main test function."""
    print("Resume Relevance Check System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("spaCy Model Test", test_spacy_model),
        ("Database Test", test_database),
        ("Document Parser Test", test_document_parser),
        ("Job Description Parser Test", test_job_description_parser),
        ("Relevance Analyzer Test", test_relevance_analyzer),
        ("Sample Data Test", test_sample_data),
        ("Full System Test", run_full_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run demo: python demo.py")
        print("2. Start system: python start_system.py")
        print("3. Open dashboard: http://localhost:8501")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("3. Check file permissions and paths")

if __name__ == "__main__":
    main()
