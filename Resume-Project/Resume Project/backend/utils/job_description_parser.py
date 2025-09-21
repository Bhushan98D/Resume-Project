"""
Job Description parsing utilities for extracting structured information.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class JobDescriptionData:
    """Structured data extracted from job description."""
    title: str
    company: str
    description: str
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    qualifications: List[str]
    experience_required: str
    location: str
    salary_range: str
    job_type: str  # Full-time, Part-time, Contract, etc.


class JobDescriptionParser:
    """Parser for extracting structured information from job descriptions."""
    
    def __init__(self):
        self.skill_keywords = self._load_skill_keywords()
        self.degree_keywords = self._load_degree_keywords()
        self.experience_patterns = self._load_experience_patterns()
    
    def parse_job_description(self, text: str, company: str = "") -> JobDescriptionData:
        """
        Parse job description text and extract structured information.
        
        Args:
            text: Raw job description text
            company: Company name (optional)
            
        Returns:
            JobDescriptionData object with extracted information
        """
        text = self._clean_text(text)
        
        # Extract basic information
        title = self._extract_job_title(text)
        location = self._extract_location(text)
        salary_range = self._extract_salary_range(text)
        job_type = self._extract_job_type(text)
        experience_required = self._extract_experience_required(text)
        
        # Extract skills
        must_have_skills = self._extract_must_have_skills(text)
        nice_to_have_skills = self._extract_nice_to_have_skills(text)
        
        # Extract qualifications
        qualifications = self._extract_qualifications(text)
        
        return JobDescriptionData(
            title=title,
            company=company,
            description=text,
            must_have_skills=must_have_skills,
            nice_to_have_skills=nice_to_have_skills,
            qualifications=qualifications,
            experience_required=experience_required,
            location=location,
            salary_range=salary_range,
            job_type=job_type
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize job description text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common job board artifacts
        text = re.sub(r'Apply now|Apply here|Click here to apply', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from text."""
        # Common job title patterns
        title_patterns = [
            r'(?:position|role|job):\s*([^,\n]+)',
            r'(?:we are looking for|seeking|hiring)\s+([^,\n]+)',
            r'^([A-Z][^,\n]{5,50})\s+(?:developer|engineer|analyst|manager|specialist)',
        ]
        
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            for pattern in title_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Fallback: look for common job titles
        common_titles = [
            'software engineer', 'data scientist', 'product manager',
            'business analyst', 'devops engineer', 'full stack developer',
            'frontend developer', 'backend developer', 'machine learning engineer'
        ]
        
        text_lower = text.lower()
        for title in common_titles:
            if title in text_lower:
                return title.title()
        
        return "Unknown Position"
    
    def _extract_location(self, text: str) -> str:
        """Extract job location from text."""
        # Common location patterns
        location_patterns = [
            r'(?:location|based in|office in):\s*([^,\n]+)',
            r'(?:remote|hybrid|onsite)',
            r'\b(?:New York|San Francisco|London|Berlin|Tokyo|Mumbai|Bangalore|Delhi)\b',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return "Not specified"
    
    def _extract_salary_range(self, text: str) -> str:
        """Extract salary range from text."""
        salary_patterns = [
            r'\$[\d,]+(?:k|K)?\s*[-–]\s*\$?[\d,]+(?:k|K)?',
            r'[\d,]+(?:k|K)\s*[-–]\s*[\d,]+(?:k|K)',
            r'(?:salary|compensation|pay):\s*([^,\n]+)',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return "Not specified"
    
    def _extract_job_type(self, text: str) -> str:
        """Extract job type from text."""
        job_types = ['full-time', 'part-time', 'contract', 'internship', 'freelance', 'remote', 'hybrid']
        
        text_lower = text.lower()
        for job_type in job_types:
            if job_type in text_lower:
                return job_type.title()
        
        return "Not specified"
    
    def _extract_experience_required(self, text: str) -> str:
        """Extract required experience from text."""
        experience_patterns = [
            r'(\d+)\s*(?:to|-)\s*(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(?:minimum|at least)\s*(\d+)\s*years?',
            r'(?:senior|junior|mid-level|entry-level)',
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return "Not specified"
    
    def _extract_must_have_skills(self, text: str) -> List[str]:
        """Extract must-have skills from job description."""
        must_have_skills = []
        
        # Look for explicit "must have" or "required" sections
        must_have_patterns = [
            r'(?:must have|required|essential|mandatory)[\s\S]*?(?=\n\n|\n[A-Z]|$)',
            r'(?:requirements|qualifications)[\s\S]*?(?=\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in must_have_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                section_text = match.group(0)
                skills = self._extract_skills_from_section(section_text)
                must_have_skills.extend(skills)
        
        # If no explicit section found, extract from entire text
        if not must_have_skills:
            must_have_skills = self._extract_skills_from_section(text)
        
        return list(set(must_have_skills))  # Remove duplicates
    
    def _extract_nice_to_have_skills(self, text: str) -> List[str]:
        """Extract nice-to-have skills from job description."""
        nice_to_have_skills = []
        
        # Look for "nice to have" or "preferred" sections
        nice_to_have_patterns = [
            r'(?:nice to have|preferred|bonus|plus)[\s\S]*?(?=\n\n|\n[A-Z]|$)',
            r'(?:additional|extra|optional)[\s\S]*?(?=\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in nice_to_have_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                section_text = match.group(0)
                skills = self._extract_skills_from_section(section_text)
                nice_to_have_skills.extend(skills)
        
        return list(set(nice_to_have_skills))  # Remove duplicates
    
    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract educational qualifications from job description."""
        qualifications = []
        
        # Look for education requirements
        education_patterns = [
            r'(?:bachelor|master|phd|doctorate|degree|diploma|certification)',
            r'(?:b\.?s\.?|m\.?s\.?|ph\.?d\.?|mba|bca|mca)',
            r'(?:computer science|engineering|mathematics|statistics|business)',
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in education_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    qualifications.append(line)
                    break
        
        return qualifications
    
    def _extract_skills_from_section(self, text: str) -> List[str]:
        """Extract skills from a specific text section."""
        skills = []
        text_lower = text.lower()
        
        # Check against predefined skill keywords
        for skill in self.skill_keywords:
            if skill.lower() in text_lower:
                skills.append(skill)
        
        # Extract skills mentioned in bullet points
        bullet_pattern = r'[•\-\*]\s*([^,\n]+)'
        bullets = re.findall(bullet_pattern, text)
        
        for bullet in bullets:
            bullet = bullet.strip()
            # Check if bullet contains skill keywords
            for skill in self.skill_keywords:
                if skill.lower() in bullet.lower():
                    skills.append(skill)
        
        return skills
    
    def _load_skill_keywords(self) -> List[str]:
        """Load predefined skill keywords."""
        return [
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
    
    def _load_degree_keywords(self) -> List[str]:
        """Load degree-related keywords."""
        return [
            'Bachelor', 'Master', 'PhD', 'Doctorate', 'B.S.', 'M.S.', 'MBA', 'BBA',
            'Computer Science', 'Engineering', 'Mathematics', 'Statistics', 'Business',
            'Information Technology', 'Software Engineering', 'Data Science'
        ]
    
    def _load_experience_patterns(self) -> List[str]:
        """Load experience-related patterns."""
        return [
            r'\d+\s*years?',
            r'senior', r'junior', r'mid-level', r'entry-level',
            r'experienced', r'seasoned', r'expert'
        ]


# Example usage and testing
if __name__ == "__main__":
    parser = JobDescriptionParser()
    
    sample_jd = """
    Software Engineer - Full Stack Developer
    
    We are looking for a talented Full Stack Developer to join our team.
    
    Requirements:
    • 3-5 years of experience in web development
    • Strong knowledge of Python, JavaScript, and React
    • Experience with Django or Flask frameworks
    • Database experience with PostgreSQL or MySQL
    • Knowledge of AWS or similar cloud platforms
    • Bachelor's degree in Computer Science or related field
    
    Nice to have:
    • Experience with Docker and Kubernetes
    • Knowledge of machine learning libraries
    • Previous startup experience
    
    Location: San Francisco, CA (Remote OK)
    Salary: $120k - $150k
    """
    
    result = parser.parse_job_description(sample_jd, "TechCorp")
    
    print("Job Title:", result.title)
    print("Company:", result.company)
    print("Location:", result.location)
    print("Experience Required:", result.experience_required)
    print("Must Have Skills:", result.must_have_skills)
    print("Nice to Have Skills:", result.nice_to_have_skills)
    print("Qualifications:", result.qualifications)
