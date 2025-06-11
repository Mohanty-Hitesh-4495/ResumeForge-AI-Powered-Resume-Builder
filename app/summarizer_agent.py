import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM with LLaMA 3.3-70B
llm = ChatGroq(
    api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
)

# ------------------- Summary Generator -------------------

def generate_profile_summary(info: Dict[str, str]) -> str:
    prompt = f"""
        You are a professional resume writer. Generate a **first-person** profile summary (**aim for 40-50 words**) using the candidate's name and skills below.

        Name: {info.get('full_name', '')}
        Skills: {', '.join(info.get('skills', []))}

        Summary must:
        - Emphasize core strengths and technical focus
        - Be concise and job-targeted, aiming for 40-50 words.
        - Avoid location, education, LinkedIn, or third-person tone

        Write like:  
        "I'm a [role/profession] with experience in [skills/fields], skilled in [technical strengths], aiming to [career goal/value proposition]."
        """
    return llm.invoke(prompt).content.strip()

# ------------------- Project Description Generator -------------------

def generate_project_description(name: str, technologies: List[str]) -> str:
    prompt = f"""
        You are writing a resume bullet for a technical project.

        Project Name: {name}  
        Technologies: {', '.join(technologies)}

        Write a **concise 1-line project description (aim for 40-50 words)** that includes:
        - What the project does
        - Your contribution or key functionality
        - Tools used

        Avoid buzzwords. Be direct and technical.
        Example:  
        "Built a resume builder using Streamlit and LangChain to auto-generate tailored resumes from user inputs, reducing manual effort by 80%."
        """
    return llm.invoke(prompt).content.strip()

# ------------------- Job Description Generator -------------------

def generate_job_description(company: str, position: str, start: str, end: str) -> str:
    prompt = f"""
        You are writing a job experience bullet point for a resume.

        Company: {company}  
        Role: {position}  
        Duration: {start} to {end} # Do NOT mention the duration in the bullet point itself.

        Write **1-2 concise bullet points (aim for 40-50 words total)** focused on:
        - Technologies/tools used
        - Main responsibilities
        - Specific achievement or outcome with metrics (if any)

        Use action verbs (e.g., Developed, Built, Improved). Avoid filler language and do NOT include the duration in the bullet points.

        Example:
        - Developed machine learning models using TensorFlow to predict crop yield, improving accuracy by 20%.
        """
    return llm.invoke(prompt).content.strip()

# ------------------- Example Usage -------------------

if __name__ == "__main__":
    # Test Profile Summary
    personal_info = {
        "full_name": "John Doe",
        "skills": ["Python", "Machine Learning", "Data Analysis"]
    }
    print("🔹 Profile Summary:\n", generate_profile_summary(personal_info))

    # Test Project Description
    print("\n🔹 Project Description:\n", generate_project_description(
        "Resume Builder", ["HTML", "CSS", "LangChain", "Groq"]
    ))

    # Test Job Description
    print("\n🔹 Job Description:\n", generate_job_description(
        "TechCorp", "Software Engineer", "Jan 2022", "May 2024"
    ))
