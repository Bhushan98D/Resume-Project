"""
Streamlit dashboard for the Resume Relevance Check System.
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64


# Configuration
st.set_page_config(
    page_title="Resume Relevance Check System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Enhanced CSS for improved contrast and readability
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Dark Theme Base */
    .main {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
    }
    
    /* Typography - Enhanced Contrast */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #f8fafc !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    h1 {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f8fafc !important;
    }
    
    h2 {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0 !important;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #cbd5e1 !important;
    }
    
    h4 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #cbd5e1 !important;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #60a5fa !important;
        text-align: center;
        margin-bottom: 3rem;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar Styling - Dark Theme */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: 1px solid #334155 !important;
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: #e2e8f0 !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Enhanced Cards with Better Contrast */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card h3, .metric-card h4 {
        color: #1e293b !important;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .metric-card p {
        color: #475569 !important;
        font-weight: 500;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Info Cards with Enhanced Text */
    .info-card {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .info-card h4 {
        color: #1e40af !important;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .info-card p {
        color: #1e3a8a !important;
        font-weight: 500;
    }
    
    /* Success Cards */
    .success-card {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #22c55e;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .success-card h4 {
        color: #166534 !important;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .success-card p {
        color: #15803d !important;
        font-weight: 500;
    }
    
    /* Warning Cards */
    .warning-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .warning-card h4 {
        color: #92400e !important;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .warning-card p {
        color: #a16207 !important;
        font-weight: 500;
    }
    
    /* Error Cards */
    .error-card {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .error-card h4 {
        color: #991b1b !important;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .error-card p {
        color: #b91c1c !important;
        font-weight: 500;
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    }
    
    /* Enhanced Form Elements */
    .stSelectbox > div > div {
        background-color: white !important;
        border: 2px solid #d1d5db !important;
        border-radius: 8px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #2563eb !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stSelectbox label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #d1d5db !important;
        border-radius: 8px;
        padding: 0.75rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        background-color: white !important;
        color: #1e293b !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stTextInput label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .stTextArea > div > div > textarea {
        border: 2px solid #d1d5db !important;
        border-radius: 8px;
        padding: 0.75rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        background-color: white !important;
        color: #1e293b !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stTextArea label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Enhanced File Uploader */
    .stFileUploader > div {
        border: 2px dashed #64748b !important;
        border-radius: 12px;
        padding: 2rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #60a5fa !important;
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
    }
    
    .stFileUploader label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Enhanced Metrics with Better Contrast */
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e40af !important;
        margin-bottom: 0.5rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .metric-label {
        font-size: 1rem;
        color: #475569 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Enhanced Tables */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        background-color: white !important;
    }
    
    .dataframe th {
        background-color: #f8fafc !important;
        color: #1e293b !important;
        font-weight: 700;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 1rem 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .dataframe td {
        color: #374151 !important;
        font-weight: 500;
        padding: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .dataframe tr:hover {
        background-color: #f8fafc !important;
    }
    
    /* Enhanced Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        border-radius: 4px;
    }
    
    /* Enhanced Spinner */
    .stSpinner {
        color: #60a5fa !important;
    }
    
    /* Enhanced Dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #475569 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Custom Grid Layout */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* Enhanced Status Badges */
    .status-high {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .status-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .status-low {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced Slider */
    .stSlider > div > div > div {
        background-color: #334155 !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #60a5fa !important;
    }
    
    .stSlider label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Enhanced Markdown Text */
    .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    .stMarkdown strong {
        color: #f8fafc !important;
        font-weight: 700;
    }
    
    .stMarkdown code {
        background-color: #1e293b !important;
        color: #60a5fa !important;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
    }
    
    /* Enhanced Help Text */
    .stHelp {
        color: #94a3b8 !important;
        font-weight: 500;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.2rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .grid-container {
            grid-template-columns: 1fr;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    
    /* Additional Dark Theme Enhancements */
    .stApp > header {
        background-color: #0f172a !important;
    }
    
    .stApp > div {
        background-color: #0f172a !important;
    }
    
    /* Ensure all text in white containers is visible */
    .metric-card, .info-card, .success-card, .warning-card, .error-card {
        color: #1e293b !important;
    }
    
    .metric-card *, .info-card *, .success-card *, .warning-card *, .error-card * {
        color: inherit !important;
    }
    
    /* Enhanced evaluation section text visibility */
    .metric-container .metric-value {
        color: #1e40af !important;
        font-weight: 800 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    }
    
    .metric-container .metric-label {
        color: #475569 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Ensure evaluation results text is visible */
    .evaluation-results h3, .evaluation-results h4 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }
    
    .evaluation-results p {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)


def make_api_request(endpoint, method="GET", data=None, files=None):
    """Make API request to backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, data=data)
            else:
                response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API. Please ensure the backend server is running.")
        return None
    except Exception as e:
        st.error(f"Error making API request: {str(e)}")
        return None


def display_header():
    """Display the main header."""
    st.markdown('<h1 class="main-header">📄 Resume Relevance Check System</h1>', unsafe_allow_html=True)
    st.markdown("---")


def display_sidebar():
    """Display sidebar navigation."""
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Home", "📤 Upload Resume", "📝 Upload Job Description", "🔍 Evaluate", "📊 Results", "📈 Analytics"]
    )
    return page


def home_page():
    """Display home page with system overview."""
    st.markdown("## Welcome to the Resume Relevance Check System")
    st.markdown("Transform your hiring process with AI-powered resume analysis and intelligent matching.")
    
    # Feature cards with modern design
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3 style="margin-top: 0; color: #2563eb;">📤 Upload Resumes</h3>
            <p style="margin-bottom: 0; color: #64748b;">Upload PDF or DOCX resume files to the system for comprehensive analysis and skill extraction.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3 style="margin-top: 0; color: #2563eb;">📝 Job Descriptions</h3>
            <p style="margin-bottom: 0; color: #64748b;">Add detailed job descriptions with requirements, qualifications, and skill expectations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3 style="margin-top: 0; color: #2563eb;">🔍 AI Analysis</h3>
            <p style="margin-bottom: 0; color: #64748b;">Get AI-powered relevance scores, missing skills analysis, and personalized improvement suggestions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick stats section
    st.markdown("### 📊 System Overview")
    
    # Get system statistics
    results = make_api_request("/results")
    resumes_data = make_api_request("/resumes")
    jd_data = make_api_request("/job-descriptions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_evaluations = len(results.get("results", [])) if results else 0
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_evaluations}</div>
            <div class="metric-label">Total Evaluations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_resumes = len(resumes_data.get("resumes", [])) if resumes_data else 0
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_resumes}</div>
            <div class="metric-label">Resumes Uploaded</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_jds = len(jd_data.get("job_descriptions", [])) if jd_data else 0
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_jds}</div>
            <div class="metric-label">Job Descriptions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if total_evaluations > 0:
            high_count = len([r for r in results.get("results", []) if r.get('verdict') == 'High'])
            avg_score = sum([r.get('relevance_score', 0) for r in results.get("results", [])]) / total_evaluations
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{avg_score:.1f}%</div>
                <div class="metric-label">Average Score</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-value">0%</div>
                <div class="metric-label">Average Score</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity with enhanced design
    st.markdown("### 🕒 Recent Activity")
    
    # Get recent results
    recent_results = make_api_request("/results?limit=5")
    if recent_results and recent_results.get("results"):
        for i, result in enumerate(recent_results["results"]):
            verdict_class = f"status-{result['verdict'].lower()}"
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div>
                        <strong style="color: #1f2937;">{result['resume_filename']}</strong>
                        <span style="color: #6b7280; margin: 0 0.5rem;">vs</span>
                        <strong style="color: #1f2937;">{result['job_title']}</strong>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span style="font-size: 1.5rem; font-weight: 700; color: #2563eb;">{result['relevance_score']}%</span>
                        <span class="{verdict_class}">{result['verdict']}</span>
                    </div>
                </div>
                <div style="color: #6b7280; font-size: 0.875rem;">
                    {result.get('created_at', '')[:10] if result.get('created_at') else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-card">
            <p style="margin: 0; text-align: center; color: #64748b;">
                No evaluations yet. Upload some resumes and job descriptions to get started!
            </p>
        </div>
        """, unsafe_allow_html=True)


def upload_resume_page():
    """Display resume upload page."""
    st.markdown("## 📤 Upload Resume")
    st.markdown("Upload PDF or DOCX resume files for AI-powered analysis and skill extraction.")
    
    # Upload section with enhanced styling
    st.markdown("### Choose Resume File")
    uploaded_file = st.file_uploader(
        "Drag and drop your resume file here or click to browse",
        type=['pdf', 'docx'],
        help="Supported formats: PDF, DOCX (Max size: 10MB)",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Display file info with modern card
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.markdown(f"""
        <div class="info-card">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 2rem;">📄</div>
                <div>
                    <h4 style="margin: 0; color: #1f2937;">{uploaded_file.name}</h4>
                    <p style="margin: 0.25rem 0 0 0; color: #6b7280;">{file_size_mb:.2f} MB • {uploaded_file.type}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Upload & Process Resume", type="primary"):
            with st.spinner("🤖 Processing resume with AI..."):
                # Prepare file for upload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Make API request
                result = make_api_request("/upload/resume", method="POST", files=files)
                
                if result:
                    st.markdown("""
                    <div class="success-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #16a34a;">✅ Resume uploaded successfully!</h4>
                        <p style="margin: 0; color: #15803d;">Your resume has been processed and is ready for evaluation.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display parsed information with enhanced layout
                    st.markdown("### 📊 Parsed Information")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div class="metric-card">
                            <h4 style="margin-top: 0; color: #2563eb;">📋 File Details</h4>
                        """, unsafe_allow_html=True)
                        st.markdown(f"**File Type:** `{result['file_type']}`")
                        st.markdown(f"**Text Length:** `{result['text_length']:,}` characters")
                        st.markdown(f"**Sections Found:** `{', '.join(result['sections_found'])}`")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div class="metric-card">
                            <h4 style="margin-top: 0; color: #2563eb;">🎯 Extracted Content</h4>
                        """, unsafe_allow_html=True)
                        st.markdown(f"**Skills Found:** `{len(result['skills_found'])}`")
                        if result['skills_found']:
                            skills_text = ", ".join(result['skills_found'][:10])
                            if len(result['skills_found']) > 10:
                                skills_text += f" ... and {len(result['skills_found']) - 10} more"
                            st.markdown(f"**Skills:** `{skills_text}`")
                        
                        st.markdown(f"**Education Found:** `{len(result['education_found'])}`")
                        if result['education_found']:
                            st.markdown(f"**Education:** `{', '.join(result['education_found'])}`")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Resume ID with copy functionality
                    st.markdown(f"""
                    <div class="info-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #2563eb;">🆔 Resume ID</h4>
                        <code style="background: #f1f5f9; padding: 0.5rem; border-radius: 4px; font-size: 1.1rem;">{result['resume_id']}</code>
                        <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.875rem;">Use this ID to reference this resume in evaluations.</p>
                    </div>
                    """, unsafe_allow_html=True)


def upload_job_description_page():
    """Display job description upload page."""
    st.markdown("## 📝 Upload Job Description")
    st.markdown("Add detailed job descriptions with requirements, qualifications, and skill expectations for AI analysis.")
    
    with st.form("job_description_form"):
        st.markdown("### 📋 Job Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Job Title *", 
                placeholder="e.g., Senior Software Engineer",
                help="Enter the specific job title or position name"
            )
            company = st.text_input(
                "Company", 
                placeholder="e.g., TechCorp Inc.",
                help="Name of the hiring company"
            )
        
        with col2:
            location = st.text_input(
                "Location", 
                placeholder="e.g., San Francisco, CA",
                help="Job location (city, state, country)"
            )
            experience = st.text_input(
                "Experience Required", 
                placeholder="e.g., 3-5 years",
                help="Required years of experience"
            )
        
        st.markdown("### 📄 Job Description")
        description = st.text_area(
            "Job Description *",
            placeholder="Paste the complete job description here...\n\nInclude:\n• Key responsibilities\n• Required qualifications\n• Preferred skills\n• Education requirements\n• Any other relevant details",
            height=300,
            help="Provide a comprehensive job description for accurate AI analysis"
        )
        
        submitted = st.form_submit_button("🚀 Upload & Process Job Description", type="primary")
        
        if submitted:
            if not title or not description:
                st.markdown("""
                <div class="error-card">
                    <h4 style="margin: 0 0 0.5rem 0; color: #dc2626;">❌ Missing Required Fields</h4>
                    <p style="margin: 0; color: #991b1b;">Please fill in the Job Title and Description fields to continue.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner("🤖 Processing job description with AI..."):
                    # Prepare data for upload
                    data = {
                        "title": title,
                        "company": company,
                        "description": description
                    }
                    
                    # Make API request
                    result = make_api_request("/upload/job-description", method="POST", data=data)
                    
                    if result:
                        st.markdown("""
                        <div class="success-card">
                            <h4 style="margin: 0 0 0.5rem 0; color: #16a34a;">✅ Job description uploaded successfully!</h4>
                            <p style="margin: 0; color: #15803d;">Your job description has been processed and is ready for resume evaluation.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display parsed information with enhanced layout
                        st.markdown("### 📊 Parsed Information")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                            <div class="metric-card">
                                <h4 style="margin-top: 0; color: #2563eb;">🏢 Job Details</h4>
                            """, unsafe_allow_html=True)
                            st.markdown(f"**Title:** `{result['title']}`")
                            st.markdown(f"**Company:** `{result['company']}`")
                            st.markdown(f"**Location:** `{result['location']}`")
                            st.markdown(f"**Experience Required:** `{result['experience_required']}`")
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <div class="metric-card">
                                <h4 style="margin-top: 0; color: #2563eb;">🎯 Skills Analysis</h4>
                            """, unsafe_allow_html=True)
                            st.markdown(f"**Must-Have Skills:** `{len(result['must_have_skills'])}`")
                            if result['must_have_skills']:
                                must_have_text = ", ".join(result['must_have_skills'][:10])
                                if len(result['must_have_skills']) > 10:
                                    must_have_text += f" ... and {len(result['must_have_skills']) - 10} more"
                                st.markdown(f"**Skills:** `{must_have_text}`")
                            
                            st.markdown(f"**Nice-to-Have Skills:** `{len(result['nice_to_have_skills'])}`")
                            if result['nice_to_have_skills']:
                                nice_to_have_text = ", ".join(result['nice_to_have_skills'][:5])
                                if len(result['nice_to_have_skills']) > 5:
                                    nice_to_have_text += f" ... and {len(result['nice_to_have_skills']) - 5} more"
                                st.markdown(f"**Skills:** `{nice_to_have_text}`")
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Job ID with copy functionality
                        st.markdown(f"""
                        <div class="info-card">
                            <h4 style="margin: 0 0 0.5rem 0; color: #2563eb;">🆔 Job Description ID</h4>
                            <code style="background: #f1f5f9; padding: 0.5rem; border-radius: 4px; font-size: 1.1rem;">{result['job_id']}</code>
                            <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.875rem;">Use this ID to reference this job description in evaluations.</p>
                        </div>
                        """, unsafe_allow_html=True)


def evaluate_page():
    """Display evaluation page."""
    st.markdown("## 🔍 Evaluate Resume")
    st.markdown("Run AI-powered analysis to match resumes against job descriptions and get detailed relevance scores.")
    
    # Get available resumes and job descriptions
    resumes_data = make_api_request("/resumes")
    job_descriptions_data = make_api_request("/job-descriptions")
    
    if not resumes_data or not job_descriptions_data:
        st.markdown("""
        <div class="error-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #dc2626;">❌ Connection Error</h4>
            <p style="margin: 0; color: #991b1b;">Could not load resumes or job descriptions. Please check your connection and try again.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    resumes = resumes_data.get("resumes", [])
    job_descriptions = job_descriptions_data.get("job_descriptions", [])
    
    if not resumes:
        st.markdown("""
        <div class="warning-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #d97706;">⚠️ No Resumes Found</h4>
            <p style="margin: 0; color: #92400e;">Please upload some resumes first before running evaluations.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if not job_descriptions:
        st.markdown("""
        <div class="warning-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #d97706;">⚠️ No Job Descriptions Found</h4>
            <p style="margin: 0; color: #92400e;">Please upload some job descriptions first before running evaluations.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    with st.form("evaluation_form"):
        st.markdown("### 📋 Select Files for Evaluation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Resume selection with enhanced display
            st.markdown("**📄 Select Resume**")
            resume_options = {f"{r['filename']} (ID: {r['id']})": r['id'] for r in resumes}
            selected_resume = st.selectbox(
                "Choose a resume to evaluate",
                list(resume_options.keys()),
                help="Select the resume file you want to analyze",
                label_visibility="collapsed"
            )
            resume_id = resume_options[selected_resume]
        
        with col2:
            # Job description selection with enhanced display
            st.markdown("**📝 Select Job Description**")
            jd_options = {f"{jd['title']} at {jd['company']} (ID: {jd['id']})": jd['id'] for jd in job_descriptions}
            selected_jd = st.selectbox(
                "Choose a job description to match against",
                list(jd_options.keys()),
                help="Select the job description to compare against",
                label_visibility="collapsed"
            )
            jd_id = jd_options[selected_jd]
        
        submitted = st.form_submit_button("🚀 Run AI Evaluation", type="primary")
        
        if submitted:
            with st.spinner("🤖 Running AI analysis... This may take a few moments."):
                # Prepare data for evaluation
                data = {
                    "resume_id": resume_id,
                    "job_description_id": jd_id
                }
                
                # Make API request
                result = make_api_request("/evaluate", method="POST", data=data)
                
                if result:
                    st.markdown("""
                    <div class="success-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #16a34a;">✅ Evaluation completed successfully!</h4>
                        <p style="margin: 0; color: #15803d;">Your resume has been analyzed against the job description.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display results with enhanced layout
                    st.markdown("### 📊 Evaluation Results")
                    
                    # Score metrics with modern cards
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-value">{result['relevance_score']}%</div>
                            <div class="metric-label">Overall Score</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-value">{result['scores']['hard_match']}%</div>
                            <div class="metric-label">Hard Match</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-value">{result['scores']['semantic_match']}%</div>
                            <div class="metric-label">Semantic Match</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        verdict_class = f"status-{result['verdict'].lower()}"
                        st.markdown(f"""
                        <div class="metric-container">
                            <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                                <span class="{verdict_class}">{result['verdict']}</span>
                            </div>
                            <div class="metric-label">Verdict</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Additional scores
                    st.markdown("### 📈 Detailed Scores")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin-top: 0; color: #1e293b; font-weight: 700;">🎓 Education Match</h4>
                            <div style="font-size: 2rem; font-weight: 700; color: #1e40af; text-align: center;">
                                {result['scores']['education_match']}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin-top: 0; color: #1e293b; font-weight: 700;">💼 Experience Match</h4>
                            <div style="font-size: 2rem; font-weight: 700; color: #1e40af; text-align: center;">
                                {result['scores']['experience_match']}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Missing skills with enhanced display
                    if result['missing_skills']:
                        st.markdown("### ❌ Missing Skills")
                        st.markdown("""
                        <div class="warning-card">
                            <h4 style="margin: 0 0 1rem 0; color: #92400e; font-weight: 700;">Skills Not Found in Resume</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        """, unsafe_allow_html=True)
                        for skill in result['missing_skills']:
                            st.markdown(f'<span class="status-medium">{skill}</span>', unsafe_allow_html=True)
                        st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # Suggestions with enhanced display
                    if result['suggestions']:
                        st.markdown("### 💡 Improvement Suggestions")
                        st.markdown("""
                        <div class="info-card">
                            <h4 style="margin: 0 0 1rem 0; color: #1e40af; font-weight: 700;">AI-Generated Recommendations</h4>
                            <ol style="margin: 0; padding-left: 1.5rem;">
                        """, unsafe_allow_html=True)
                        for i, suggestion in enumerate(result['suggestions'], 1):
                            st.markdown(f"<li style='margin-bottom: 0.5rem; color: #1e3a8a; font-weight: 500;'>{suggestion}</li>", unsafe_allow_html=True)
                        st.markdown("</ol></div>", unsafe_allow_html=True)
                    
                    # Evaluation ID
                    st.markdown(f"""
                    <div class="info-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #1e40af; font-weight: 700;">🆔 Evaluation ID</h4>
                        <code style="background: #f1f5f9; color: #1e293b; padding: 0.5rem; border-radius: 4px; font-size: 1.1rem; font-weight: 600;">{result['evaluation_id']}</code>
                        <p style="margin: 0.5rem 0 0 0; color: #1e3a8a; font-size: 0.875rem; font-weight: 500;">Use this ID to reference this evaluation in reports.</p>
                    </div>
                    """, unsafe_allow_html=True)


def results_page():
    """Display results page."""
    st.markdown("## 📊 Evaluation Results")
    st.markdown("View and analyze all resume evaluations with detailed insights and filtering options.")
    
    # Get results
    results = make_api_request("/results")
    
    if not results:
        st.markdown("""
        <div class="error-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #dc2626;">❌ Connection Error</h4>
            <p style="margin: 0; color: #991b1b;">Could not load results. Please check your connection and try again.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    evaluations = results.get("results", [])
    
    if not evaluations:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #2563eb;">📋 No Evaluations Found</h4>
            <p style="margin: 0; color: #64748b;">Run some evaluations to see results here. Go to the Evaluate page to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Create DataFrame for display
    df = pd.DataFrame(evaluations)
    
    # Display summary metrics with modern cards
    st.markdown("### 📈 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{len(evaluations)}</div>
            <div class="metric-label">Total Evaluations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        high_count = len(df[df['verdict'] == 'High'])
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{high_count}</div>
            <div class="metric-label">High Relevance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        medium_count = len(df[df['verdict'] == 'Medium'])
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{medium_count}</div>
            <div class="metric-label">Medium Relevance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        low_count = len(df[df['verdict'] == 'Low'])
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{low_count}</div>
            <div class="metric-label">Low Relevance</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter options with enhanced design
    st.markdown("### 🔍 Filters & Search")
    
    col1, col2 = st.columns(2)
    
    with col1:
        verdict_filter = st.selectbox(
            "Filter by Verdict", 
            ["All", "High", "Medium", "Low"],
            help="Filter results by relevance verdict"
        )
    
    with col2:
        score_threshold = st.slider(
            "Minimum Score", 
            0, 100, 0,
            help="Show only results with scores above this threshold"
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if verdict_filter != "All":
        filtered_df = filtered_df[filtered_df['verdict'] == verdict_filter]
    
    filtered_df = filtered_df[filtered_df['relevance_score'] >= score_threshold]
    
    # Display results table with enhanced styling
    st.markdown("### 📋 Results Table")
    
    if filtered_df.empty:
        st.markdown("""
        <div class="info-card">
            <p style="margin: 0; text-align: center; color: #64748b;">
                No results match your current filters. Try adjusting the filter criteria.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Format the dataframe for display
        display_df = filtered_df[['resume_filename', 'job_title', 'company', 'relevance_score', 'verdict', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['Resume', 'Job Title', 'Company', 'Score (%)', 'Verdict', 'Date']
        
        # Enhanced color coding for verdict column with better contrast
        def color_verdict(val):
            if val == 'High':
                return 'background-color: #dcfce7; color: #166534; font-weight: 600; padding: 0.5rem; border-radius: 4px;'
            elif val == 'Medium':
                return 'background-color: #fef3c7; color: #92400e; font-weight: 600; padding: 0.5rem; border-radius: 4px;'
            elif val == 'Low':
                return 'background-color: #fecaca; color: #991b1b; font-weight: 600; padding: 0.5rem; border-radius: 4px;'
            return ''
        
        # Enhanced table styling with better contrast
        styled_df = (display_df.style
                    .map(color_verdict, subset=['Verdict'])
                    .set_properties(**{
                        'background-color': '#ffffff',
                        'color': '#1e293b',
                        'font-weight': '500',
                        'padding': '0.75rem',
                        'border': '1px solid #e2e8f0'
                    })
                    .set_table_styles([
                        {
                            'selector': 'thead th',
                            'props': [
                                ('background-color', '#f8fafc'),
                                ('color', '#1e293b'),
                                ('font-weight', '700'),
                                ('font-size', '0.875rem'),
                                ('text-transform', 'uppercase'),
                                ('letter-spacing', '0.05em'),
                                ('padding', '1rem 0.75rem'),
                                ('border-bottom', '2px solid #e2e8f0')
                            ]
                        },
                        {
                            'selector': 'tbody tr:hover',
                            'props': [
                                ('background-color', '#f8fafc'),
                                ('transition', 'all 0.2s ease')
                            ]
                        }
                    ]))
        
        st.dataframe(styled_df, use_container_width=True)
    
    # Detailed view with enhanced design
    if not filtered_df.empty:
        st.markdown("### 🔍 Detailed View")
        
        # Create options for selection
        options = []
        for idx, row in filtered_df.iterrows():
            options.append(f"{row['resume_filename']} vs {row['job_title']} ({row['relevance_score']}%)")
        
        selected_index = st.selectbox(
            "Select an evaluation for detailed view", 
            range(len(filtered_df)),
            format_func=lambda x: options[x],
            help="Choose an evaluation to view detailed analysis"
        )
        
        if st.button("📊 View Detailed Report", type="primary"):
            evaluation_id = filtered_df.iloc[selected_index]['evaluation_id']
            
            # Get detailed report
            report = make_api_request(f"/reports/{evaluation_id}")
            
            if report:
                # Display detailed report with enhanced layout
                st.markdown("#### 📋 Detailed Report")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <h4 style="margin-top: 0; color: #2563eb;">📄 Resume Information</h4>
                    """, unsafe_allow_html=True)
                    st.markdown(f"**File:** `{report['resume_info']['filename']}`")
                    st.markdown(f"**Type:** `{report['resume_info']['file_type']}`")
                    st.markdown(f"**Uploaded:** `{report['resume_info']['uploaded_at']}`")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <h4 style="margin-top: 0; color: #2563eb;">🏢 Job Information</h4>
                    """, unsafe_allow_html=True)
                    st.markdown(f"**Title:** `{report['job_info']['title']}`")
                    st.markdown(f"**Company:** `{report['job_info']['company']}`")
                    st.markdown(f"**Location:** `{report['job_info']['location']}`")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Scores breakdown with enhanced chart
                st.markdown("#### 📊 Score Breakdown")
                
                scores = report['scores']
                score_data = pd.DataFrame([
                    ['Overall', scores['overall']],
                    ['Hard Match', scores['hard_match']],
                    ['Semantic Match', scores['semantic_match']],
                    ['Education Match', scores['education_match']],
                    ['Experience Match', scores['experience_match']]
                ], columns=['Category', 'Score'])
                
                fig = px.bar(
                    score_data, 
                    x='Category', 
                    y='Score', 
                    title='Score Breakdown',
                    color='Score',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif")
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Missing skills and suggestions with enhanced display
                col1, col2 = st.columns(2)
                
                with col1:
                    if report['missing_skills']:
                        st.markdown("""
                        <div class="warning-card">
                            <h4 style="margin: 0 0 1rem 0; color: #d97706;">❌ Missing Skills</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        """, unsafe_allow_html=True)
                        for skill in report['missing_skills']:
                            st.markdown(f'<span class="status-medium">{skill}</span>', unsafe_allow_html=True)
                        st.markdown("</div></div>", unsafe_allow_html=True)
                
                with col2:
                    if report['suggestions']:
                        st.markdown("""
                        <div class="info-card">
                            <h4 style="margin: 0 0 1rem 0; color: #2563eb;">💡 Suggestions</h4>
                            <ol style="margin: 0; padding-left: 1.5rem;">
                        """, unsafe_allow_html=True)
                        for i, suggestion in enumerate(report['suggestions'], 1):
                            st.markdown(f"<li style='margin-bottom: 0.5rem; color: #374151;'>{suggestion}</li>", unsafe_allow_html=True)
                        st.markdown("</ol></div>", unsafe_allow_html=True)


def analytics_page():
    """Display analytics page."""
    st.markdown("## 📈 Analytics Dashboard")
    st.markdown("Comprehensive insights and visualizations of your resume evaluation data.")
    
    # Get results
    results = make_api_request("/results")
    
    if not results:
        st.markdown("""
        <div class="error-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #dc2626;">❌ Connection Error</h4>
            <p style="margin: 0; color: #991b1b;">Could not load results. Please check your connection and try again.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    evaluations = results.get("results", [])
    
    if not evaluations:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #2563eb;">📊 No Data Available</h4>
            <p style="margin: 0; color: #64748b;">Run some evaluations to see analytics here. Go to the Evaluate page to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    df = pd.DataFrame(evaluations)
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Key metrics overview
    st.markdown("### 📊 Key Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = df['relevance_score'].mean()
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{avg_score:.1f}%</div>
            <div class="metric-label">Average Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        high_percentage = (df['verdict'] == 'High').mean() * 100
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{high_percentage:.1f}%</div>
            <div class="metric-label">High Relevance Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_resumes = df['resume_filename'].nunique()
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_resumes}</div>
            <div class="metric-label">Unique Resumes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_jobs = df['job_title'].nunique()
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_jobs}</div>
            <div class="metric-label">Unique Job Titles</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Score distribution with enhanced charts
    st.markdown("### 📈 Score Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram with enhanced styling and better contrast
        fig = px.histogram(
            df, 
            x='relevance_score', 
            nbins=20, 
            title='Score Distribution',
            color_discrete_sequence=['#60a5fa'],
            opacity=0.9
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", color='#f1f5f9', size=14),
            title_font=dict(size=18, color='#f8fafc'),
            xaxis=dict(
                title="Relevance Score (%)",
                title_font=dict(color='#e2e8f0', size=14),
                tickfont=dict(color='#cbd5e1', size=12),
                gridcolor='#334155',
                linecolor='#475569'
            ),
            yaxis=dict(
                title="Number of Evaluations",
                title_font=dict(color='#e2e8f0', size=14),
                tickfont=dict(color='#cbd5e1', size=12),
                gridcolor='#334155',
                linecolor='#475569'
            ),
            margin=dict(l=60, r=60, t=80, b=60)
        )
        fig.update_traces(
            marker_line_color='#1e40af', 
            marker_line_width=2,
            hovertemplate='<b>Score Range:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Verdict pie chart with enhanced styling and better contrast
        verdict_counts = df['verdict'].value_counts()
        colors = {'High': '#22c55e', 'Medium': '#f59e0b', 'Low': '#ef4444'}
        fig = px.pie(
            values=verdict_counts.values, 
            names=verdict_counts.index, 
            title='Verdict Distribution',
            color=verdict_counts.index,
            color_discrete_map=colors
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", color='#f1f5f9', size=14),
            title_font=dict(size=18, color='#f8fafc'),
            legend=dict(
                font=dict(color='#e2e8f0', size=12),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='#334155',
                borderwidth=1
            ),
            margin=dict(l=60, r=60, t=80, b=60)
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(color='white', size=12, family='Inter'),
            marker=dict(line=dict(color='white', width=2))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Time series analysis
    st.markdown("### 📅 Evaluations Over Time")
    
    daily_evaluations = df.groupby(df['created_at'].dt.date).size().reset_index()
    daily_evaluations.columns = ['Date', 'Count']
    
    fig = px.line(
        daily_evaluations, 
        x='Date', 
        y='Count', 
        title='Daily Evaluations Trend',
        color_discrete_sequence=['#60a5fa']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color='#f1f5f9', size=14),
        title_font=dict(size=18, color='#f8fafc'),
        xaxis=dict(
            title="Date",
            title_font=dict(color='#e2e8f0', size=14),
            tickfont=dict(color='#cbd5e1', size=12),
            gridcolor='#334155',
            linecolor='#475569'
        ),
        yaxis=dict(
            title="Number of Evaluations",
            title_font=dict(color='#e2e8f0', size=14),
            tickfont=dict(color='#cbd5e1', size=12),
            gridcolor='#334155',
            linecolor='#475569'
        ),
        margin=dict(l=60, r=60, t=80, b=60)
    )
    fig.update_traces(
        line=dict(width=4, color='#60a5fa'), 
        marker=dict(size=10, color='#3b82f6', line=dict(color='white', width=2)),
        hovertemplate='<b>Date:</b> %{x}<br><b>Evaluations:</b> %{y}<extra></extra>'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top performing resumes with enhanced design
    st.markdown("### 🏆 Top Performing Resumes")
    
    top_resumes = df.groupby('resume_filename')['relevance_score'].agg(['mean', 'count']).reset_index()
    top_resumes = top_resumes[top_resumes['count'] >= 2]  # Only resumes with multiple evaluations
    top_resumes = top_resumes.sort_values('mean', ascending=False).head(10)
    
    if not top_resumes.empty:
        fig = px.bar(
            top_resumes, 
            x='resume_filename', 
            y='mean', 
            title='Average Score by Resume',
            color='mean',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            xaxis_title="Resume File",
            yaxis_title="Average Score (%)",
            xaxis_tickangle=45
        )
        fig.update_traces(marker_line_color='white', marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display top resumes table
        st.markdown("#### 📋 Top Resumes Summary")
        display_top_resumes = top_resumes.copy()
        display_top_resumes.columns = ['Resume File', 'Average Score (%)', 'Number of Evaluations']
        display_top_resumes['Average Score (%)'] = display_top_resumes['Average Score (%)'].round(1)
        st.dataframe(display_top_resumes, use_container_width=True)
    else:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #2563eb;">📊 Insufficient Data</h4>
            <p style="margin: 0; color: #64748b;">Not enough data for top performing resumes analysis. Run more evaluations to see this analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional insights
    st.markdown("### 💡 Additional Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score range analysis
        score_ranges = pd.cut(df['relevance_score'], bins=[0, 55, 80, 100], labels=['Low (0-55%)', 'Medium (55-80%)', 'High (80-100%)'])
        range_counts = score_ranges.value_counts()
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin-top: 0; color: #2563eb;">📊 Score Range Distribution</h4>
        """, unsafe_allow_html=True)
        for range_name, count in range_counts.items():
            percentage = (count / len(df)) * 100
            st.markdown(f"**{range_name}:** {count} evaluations ({percentage:.1f}%)")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Recent activity
        recent_evaluations = df.tail(5)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin-top: 0; color: #2563eb;">🕒 Recent Activity</h4>
        """, unsafe_allow_html=True)
        for _, row in recent_evaluations.iterrows():
            verdict_class = f"status-{row['verdict'].lower()}"
            st.markdown(f"""
            <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: #f8fafc; border-radius: 4px;">
                <strong>{row['resume_filename']}</strong> vs <strong>{row['job_title']}</strong><br>
                <span style="font-size: 0.875rem; color: #6b7280;">
                    {row['relevance_score']}% • <span class="{verdict_class}">{row['verdict']}</span>
                </span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Main application function."""
    display_header()
    
    # Sidebar navigation
    page = display_sidebar()
    
    # Route to appropriate page
    if page == "🏠 Home":
        home_page()
    elif page == "📤 Upload Resume":
        upload_resume_page()
    elif page == "📝 Upload Job Description":
        upload_job_description_page()
    elif page == "🔍 Evaluate":
        evaluate_page()
    elif page == "📊 Results":
        results_page()
    elif page == "📈 Analytics":
        analytics_page()


if __name__ == "__main__":
    main()
