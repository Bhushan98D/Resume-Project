"""
Relevance analysis engine for comparing resumes against job descriptions.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz, process
import openai
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RelevanceScore:
    """Container for relevance scoring results."""
    overall_score: float
    hard_match_score: float
    semantic_match_score: float
    education_match_score: float
    experience_match_score: float
    verdict: str
    missing_skills: List[str]
    suggestions: List[str]
    detailed_breakdown: Dict


class RelevanceAnalyzer:
    """Main analyzer for computing resume-job description relevance."""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.sentence_model = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize sentence transformer if available
        if SentenceTransformer:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load sentence transformer: {e}")
                self.sentence_model = None
        else:
            self.sentence_model = None
    
    def analyze_relevance(self, resume_data: Dict, job_data: Dict) -> RelevanceScore:
        """
        Analyze relevance between resume and job description.
        
        Args:
            resume_data: Parsed resume data
            job_data: Parsed job description data
            
        Returns:
            RelevanceScore object with detailed analysis
        """
        # Extract text and skills
        resume_text = resume_data.get('text', '')
        resume_skills = self._extract_resume_skills(resume_text)
        
        # Handle both dict and dataclass job_data
        if isinstance(job_data, dict):
            job_skills = job_data.get('must_have_skills', []) + job_data.get('nice_to_have_skills', [])
        else:
            job_skills = job_data.must_have_skills + job_data.nice_to_have_skills
        
        # Compute individual scores
        hard_match_score = self._compute_hard_match_score(resume_text, job_data)
        semantic_match_score = self._compute_semantic_match_score(resume_text, job_data.get('description', '') if isinstance(job_data, dict) else job_data.description)
        education_match_score = self._compute_education_match_score(resume_text, job_data.get('qualifications', []) if isinstance(job_data, dict) else job_data.qualifications)
        experience_match_score = self._compute_experience_match_score(resume_text, job_data.get('experience_required', '') if isinstance(job_data, dict) else job_data.experience_required)
        
        # Find missing skills first
        missing_skills = self._find_missing_skills(resume_skills, job_skills)
        
        # Weighted overall score (skills are most important)
        overall_score = (
            hard_match_score * 0.6 +
            semantic_match_score * 0.2 +
            education_match_score * 0.1 +
            experience_match_score * 0.1
        )
        
        # Add bonus for perfect skill matches
        if not missing_skills and hard_match_score >= 80:
            overall_score = min(overall_score + 10, 100)  # Up to 10 point bonus
        
        # Add bonus for high semantic similarity
        if semantic_match_score >= 70:
            overall_score = min(overall_score + 5, 100)  # Up to 5 point bonus
        
        # Determine verdict
        verdict = self._determine_verdict(overall_score)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            missing_skills, overall_score, verdict, resume_data, job_data
        )
        
        # Create detailed breakdown
        job_description = job_data.get('description', '') if isinstance(job_data, dict) else job_data.description
        job_qualifications = job_data.get('qualifications', []) if isinstance(job_data, dict) else job_data.qualifications
        job_experience = job_data.get('experience_required', '') if isinstance(job_data, dict) else job_data.experience_required
        
        detailed_breakdown = {
            'hard_match_details': self._get_hard_match_details(resume_text, job_data),
            'semantic_match_details': self._get_semantic_match_details(resume_text, job_description),
            'education_match_details': self._get_education_match_details(resume_text, job_qualifications),
            'experience_match_details': self._get_experience_match_details(resume_text, job_experience),
            'skill_analysis': {
                'resume_skills': resume_skills,
                'job_skills': job_skills,
                'matched_skills': list(set(resume_skills) & set(job_skills)),
                'missing_skills': missing_skills
            }
        }
        
        return RelevanceScore(
            overall_score=round(overall_score, 2),
            hard_match_score=round(hard_match_score, 2),
            semantic_match_score=round(semantic_match_score, 2),
            education_match_score=round(education_match_score, 2),
            experience_match_score=round(experience_match_score, 2),
            verdict=verdict,
            missing_skills=missing_skills,
            suggestions=suggestions,
            detailed_breakdown=detailed_breakdown
        )
    
    def _extract_resume_skills(self, resume_text: str) -> List[str]:
        """Extract skills from resume text."""
        # Common technical skills with better patterns
        skill_patterns = [
            # Programming Languages
            r'\b(?:python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala|r|matlab)\b',
            # Web Technologies
            r'\b(?:react|angular|vue|node\.?js|express|django|flask|fastapi|spring|laravel|rails|asp\.net)\b',
            r'\b(?:html|css|bootstrap|sass|less|tailwind|jquery|webpack|babel)\b',
            # Databases
            r'\b(?:sql|mysql|postgresql|mongodb|redis|elasticsearch|oracle|sqlite|dynamodb|cassandra)\b',
            # Cloud & DevOps
            r'\b(?:aws|azure|gcp|docker|kubernetes|terraform|ansible|jenkins|gitlab|github|ci/cd|devops)\b',
            # AI/ML
            r'\b(?:machine learning|ml|ai|deep learning|nlp|computer vision|pandas|numpy|scikit-learn|tensorflow|pytorch|keras)\b',
            # Tools & Frameworks
            r'\b(?:git|jira|confluence|slack|figma|photoshop|illustrator|tableau|power bi)\b',
            # Methodologies
            r'\b(?:agile|scrum|kanban|waterfall|tdd|bdd|microservices|rest api|graphql)\b',
            # Additional skills
            r'\b(?:linux|unix|windows|macos|android|ios|firebase|heroku|netlify|vercel)\b'
        ]
        
        skills = set()
        text_lower = resume_text.lower()
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            # Clean up matches and add to skills set
            for match in matches:
                if isinstance(match, tuple):
                    # Handle groups in regex
                    for group in match:
                        if group:
                            skills.add(group.strip())
                else:
                    skills.add(match.strip())
        
        # Also look for skills mentioned in common formats
        # Look for "Skills:" section
        skills_section = re.search(r'skills?[:\-]\s*([^\n]+(?:\n[^\n]+)*)', text_lower, re.IGNORECASE)
        if skills_section:
            skills_text = skills_section.group(1)
            # Split by common separators
            skill_list = re.split(r'[,;|\n•\-\*]', skills_text)
            for skill in skill_list:
                skill = skill.strip()
                if len(skill) > 2 and len(skill) < 50:  # Reasonable skill length
                    skills.add(skill)
        
        return list(skills)
    
    def _compute_hard_match_score(self, resume_text: str, job_data) -> float:
        """Compute hard matching score using TF-IDF and fuzzy matching."""
        # Handle both dict and dataclass job_data
        if isinstance(job_data, dict):
            description = job_data.get('description', '')
            must_have_skills = job_data.get('must_have_skills', [])
            nice_to_have_skills = job_data.get('nice_to_have_skills', [])
            qualifications = job_data.get('qualifications', [])
        else:
            description = job_data.description
            must_have_skills = job_data.must_have_skills
            nice_to_have_skills = job_data.nice_to_have_skills
            qualifications = job_data.qualifications
        
        # Combine all job requirements
        job_text = ' '.join([
            description,
            ' '.join(must_have_skills),
            ' '.join(nice_to_have_skills),
            ' '.join(qualifications)
        ])
        
        # TF-IDF similarity
        try:
            corpus = [resume_text, job_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
            tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            tfidf_similarity = 0.0
        
        # Extract skills from resume
        resume_skills = self._extract_resume_skills(resume_text)
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        
        # Skill matching with better logic
        must_have_matches = 0
        nice_to_have_matches = 0
        
        # Check must-have skills (weighted more heavily)
        for skill in must_have_skills:
            if not skill or not skill.strip():
                continue
            skill_lower = skill.lower().strip()
            
            # Exact match
            if skill_lower in resume_skills_lower:
                must_have_matches += 1
            else:
                # Check if skill appears in resume text
                if skill_lower in resume_text.lower():
                    must_have_matches += 0.8
                else:
                    # Fuzzy match
                    best_match = process.extractOne(skill_lower, resume_skills_lower, scorer=fuzz.ratio)
                    if best_match and best_match[1] >= 80:
                        must_have_matches += 0.6
        
        # Check nice-to-have skills
        for skill in nice_to_have_skills:
            if not skill or not skill.strip():
                continue
            skill_lower = skill.lower().strip()
            
            # Exact match
            if skill_lower in resume_skills_lower:
                nice_to_have_matches += 1
            else:
                # Check if skill appears in resume text
                if skill_lower in resume_text.lower():
                    nice_to_have_matches += 0.8
                else:
                    # Fuzzy match
                    best_match = process.extractOne(skill_lower, resume_skills_lower, scorer=fuzz.ratio)
                    if best_match and best_match[1] >= 80:
                        nice_to_have_matches += 0.6
        
        # Calculate skill scores
        must_have_score = (must_have_matches / max(len(must_have_skills), 1)) * 100 if must_have_skills else 0
        nice_to_have_score = (nice_to_have_matches / max(len(nice_to_have_skills), 1)) * 100 if nice_to_have_skills else 0
        
        # Weighted skill score (must-have skills are more important)
        if must_have_skills and nice_to_have_skills:
            skill_score = (must_have_score * 0.7 + nice_to_have_score * 0.3)
        elif must_have_skills:
            skill_score = must_have_score
        elif nice_to_have_skills:
            skill_score = nice_to_have_score
        else:
            skill_score = 0
        
        # Final weighted combination (skill_score is already 0-100)
        hard_match_score = (tfidf_similarity * 0.1 + skill_score * 0.9)
        
        # Add bonus for high skill coverage
        if skill_score >= 90:
            hard_match_score = min(hard_match_score + 5, 100)  # Bonus for excellent skill match
        elif skill_score >= 80:
            hard_match_score = min(hard_match_score + 3, 100)  # Bonus for good skill match
        
        return min(max(hard_match_score, 0.0), 100.0)
    
    def _compute_semantic_match_score(self, resume_text: str, job_description: str) -> float:
        """Compute semantic similarity using embeddings."""
        if not job_description or not job_description.strip():
            return 50.0  # Neutral score if no job description
        
        if not self.sentence_model:
            # Fallback to TF-IDF if sentence transformer not available
            try:
                corpus = [resume_text, job_description]
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
                tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return tfidf_similarity * 100  # Scale to 0-100
            except Exception as e:
                print(f"TF-IDF fallback error: {e}")
                return 50.0  # Neutral score on error
        
        try:
            # Generate embeddings
            resume_embedding = self.sentence_model.encode([resume_text])
            job_embedding = self.sentence_model.encode([job_description])
            
            # Compute cosine similarity
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            return similarity * 100  # Scale to 0-100
            
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            # Fallback to TF-IDF
            try:
                corpus = [resume_text, job_description]
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
                tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return tfidf_similarity * 100
            except:
                return 50.0  # Neutral score on error
    
    def _compute_education_match_score(self, resume_text: str, job_qualifications: List[str]) -> float:
        """Compute education matching score."""
        if not job_qualifications:
            return 50.0  # Neutral score if no education requirements
        
        # Extract education from resume
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'diploma',
            'b.s.', 'm.s.', 'mba', 'bca', 'mca', 'computer science',
            'engineering', 'mathematics', 'statistics'
        ]
        
        resume_education = []
        text_lower = resume_text.lower()
        
        for keyword in education_keywords:
            if keyword in text_lower:
                resume_education.append(keyword)
        
        if not resume_education:
            return 0.0
        
        # Check for degree level match
        degree_levels = {
            'phd': 4, 'doctorate': 4,
            'master': 3, 'm.s.': 3, 'mba': 3,
            'bachelor': 2, 'b.s.': 2, 'bca': 2,
            'diploma': 1
        }
        
        resume_max_level = 0
        for edu in resume_education:
            for degree, level in degree_levels.items():
                if degree in edu:
                    resume_max_level = max(resume_max_level, level)
        
        # Check job requirements
        job_max_level = 0
        for qual in job_qualifications:
            qual_lower = qual.lower()
            for degree, level in degree_levels.items():
                if degree in qual_lower:
                    job_max_level = max(job_max_level, level)
        
        if job_max_level == 0:
            return 50.0  # No specific degree requirement
        
        # Score based on degree level match
        if resume_max_level >= job_max_level:
            return 100.0
        elif resume_max_level >= job_max_level - 1:
            return 75.0
        elif resume_max_level >= job_max_level - 2:
            return 50.0
        else:
            return 25.0
    
    def _compute_experience_match_score(self, resume_text: str, experience_required: str) -> float:
        """Compute experience matching score."""
        if not experience_required or experience_required.lower() == 'not specified':
            return 50.0  # Neutral score if no experience requirement
        
        # Extract years from requirement
        years_match = re.search(r'(\d+)', experience_required)
        if not years_match:
            return 50.0
        
        required_years = int(years_match.group(1))
        
        # Extract experience from resume
        experience_patterns = [
            r'(\d+)\s*(?:to|-)\s*(\d+)\s*years?',
            r'(\d+)\+?\s*years?',
            r'(\d+)\s*years?\s*of\s*experience'
        ]
        
        resume_years = 0
        for pattern in experience_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:  # Range like "3-5 years"
                    resume_years = max(resume_years, int(match[1]))
                else:  # Single number
                    resume_years = max(resume_years, int(match[0]))
        
        # Score based on experience match
        if resume_years >= required_years:
            return 100.0
        elif resume_years >= required_years * 0.8:
            return 80.0
        elif resume_years >= required_years * 0.6:
            return 60.0
        elif resume_years >= required_years * 0.4:
            return 40.0
        else:
            return 20.0
    
    def _determine_verdict(self, overall_score: float) -> str:
        """Determine verdict based on overall score."""
        if overall_score >= 80:
            return "High"
        elif overall_score >= 55:
            return "Medium"
        else:
            return "Low"
    
    def _find_missing_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Find skills that are required but missing from resume."""
        if not job_skills:
            return []
            
        resume_skills_lower = [skill.lower().strip() for skill in resume_skills if skill.strip()]
        missing_skills = []
        
        for job_skill in job_skills:
            if not job_skill or not job_skill.strip():
                continue
                
            job_skill_lower = job_skill.lower().strip()
            found_match = False
            
            # Check for exact match
            if job_skill_lower in resume_skills_lower:
                found_match = True
            else:
                # Check for partial match (skill contains or is contained in resume skill)
                for resume_skill in resume_skills_lower:
                    if (job_skill_lower in resume_skill or resume_skill in job_skill_lower) and len(job_skill_lower) > 3:
                        found_match = True
                        break
                
                # Check for fuzzy match if no partial match found
                if not found_match:
                    best_match = process.extractOne(job_skill_lower, resume_skills_lower, scorer=fuzz.ratio)
                    if best_match and best_match[1] >= 75:  # 75% similarity threshold
                        found_match = True
            
            if not found_match:
                missing_skills.append(job_skill)
        
        return missing_skills
    
    def _generate_suggestions(self, missing_skills: List[str], overall_score: float, 
                            verdict: str, resume_data: Dict, job_data: Dict) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if verdict == "Low":
            suggestions.append("Consider gaining more relevant experience in the required field")
            suggestions.append("Focus on developing the core skills mentioned in the job description")
        
        if missing_skills:
            suggestions.append(f"Consider learning or highlighting these skills: {', '.join(missing_skills[:5])}")
        
        if overall_score < 70:
            suggestions.append("Add more specific examples of your achievements and impact")
            suggestions.append("Quantify your experience with metrics and numbers")
        
        if len(resume_data.get('text', '')) < 500:
            suggestions.append("Consider adding more detail to your resume sections")
        
        suggestions.append("Tailor your resume to match the specific job requirements")
        suggestions.append("Use keywords from the job description in your resume")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _get_hard_match_details(self, resume_text: str, job_data) -> Dict:
        """Get detailed breakdown of hard matching."""
        # Handle both dict and dataclass job_data
        if isinstance(job_data, dict):
            must_have_skills = job_data.get('must_have_skills', [])
            nice_to_have_skills = job_data.get('nice_to_have_skills', [])
        else:
            must_have_skills = job_data.must_have_skills
            nice_to_have_skills = job_data.nice_to_have_skills
            
        return {
            'tfidf_similarity': self._compute_hard_match_score(resume_text, job_data),
            'skill_matches': len(set(self._extract_resume_skills(resume_text)) & set(must_have_skills + nice_to_have_skills)),
            'total_required_skills': len(must_have_skills + nice_to_have_skills)
        }
    
    def _get_semantic_match_details(self, resume_text: str, job_description: str) -> Dict:
        """Get detailed breakdown of semantic matching."""
        return {
            'similarity_score': self._compute_semantic_match_score(resume_text, job_description),
            'resume_length': len(resume_text),
            'job_description_length': len(job_description)
        }
    
    def _get_education_match_details(self, resume_text: str, qualifications: List[str]) -> Dict:
        """Get detailed breakdown of education matching."""
        return {
            'education_score': self._compute_education_match_score(resume_text, qualifications),
            'resume_education_found': len([edu for edu in ['bachelor', 'master', 'phd', 'degree'] if edu in resume_text.lower()]),
            'job_education_requirements': len(qualifications)
        }
    
    def _get_experience_match_details(self, resume_text: str, experience_required: str) -> Dict:
        """Get detailed breakdown of experience matching."""
        return {
            'experience_score': self._compute_experience_match_score(resume_text, experience_required),
            'experience_required': experience_required,
            'resume_contains_experience': 'experience' in resume_text.lower() or 'years' in resume_text.lower()
        }


# Example usage and testing
if __name__ == "__main__":
    analyzer = RelevanceAnalyzer()
    
    # Sample data for testing
    resume_data = {
        'text': 'Software Engineer with 3 years of experience in Python, JavaScript, and React. Bachelor in Computer Science.',
        'skills': ['Python', 'JavaScript', 'React', 'HTML', 'CSS']
    }
    
    job_data = {
        'description': 'We are looking for a Full Stack Developer with strong Python and React skills.',
        'must_have_skills': ['Python', 'React', 'JavaScript', 'SQL'],
        'nice_to_have_skills': ['Docker', 'AWS'],
        'qualifications': ['Bachelor in Computer Science'],
        'experience_required': '2-4 years'
    }
    
    result = analyzer.analyze_relevance(resume_data, job_data)
    
    print(f"Overall Score: {result.overall_score}")
    print(f"Verdict: {result.verdict}")
    print(f"Missing Skills: {result.missing_skills}")
    print(f"Suggestions: {result.suggestions}")
