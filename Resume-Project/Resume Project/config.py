"""
Configuration file for the Resume Relevance Check System.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///resume_checker.db')

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))

# Upload Configuration
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB

# Create upload directories
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "resumes").mkdir(exist_ok=True)
(UPLOAD_DIR / "job_descriptions").mkdir(exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Scoring Weights
SCORING_WEIGHTS = {
    'hard_match': 0.4,
    'semantic_match': 0.4,
    'education_match': 0.1,
    'experience_match': 0.1
}

# Verdict Thresholds
VERDICT_THRESHOLDS = {
    'high': 80,
    'medium': 60,
    'low': 0
}

# Supported File Types
SUPPORTED_FILE_TYPES = ['.pdf', '.docx']

# Skill Keywords for Extraction
SKILL_KEYWORDS = [
    # Programming Languages
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby',
    'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash',
    
    # Web Technologies
    'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'Django', 'Flask',
    'FastAPI', 'Spring', 'Laravel', 'ASP.NET', 'jQuery', 'Bootstrap', 'SASS', 'LESS',
    
    # Databases
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra',
    'Oracle', 'SQLite', 'DynamoDB', 'Neo4j',
    
    # Cloud & DevOps
    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins',
    'Git', 'GitHub', 'GitLab', 'CI/CD', 'Ansible', 'Chef', 'Puppet',
    
    # Data Science & ML
    'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'Data Science',
    'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'Keras',
    'Natural Language Processing', 'Computer Vision', 'Statistics', 'Analytics',
    
    # Mobile Development
    'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
    
    # Other Technologies
    'Linux', 'Unix', 'Windows', 'MacOS', 'REST API', 'GraphQL', 'Microservices',
    'Agile', 'Scrum', 'Kanban', 'DevOps', 'TDD', 'BDD'
]
