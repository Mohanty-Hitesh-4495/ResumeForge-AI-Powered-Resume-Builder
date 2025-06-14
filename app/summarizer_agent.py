import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM with LLaMA 3.3-70b-versatile
llm = ChatGroq(
    api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
)

# ------------------- Summary Generator -------------------

def generate_profile_summary(info: Dict[str, str]) -> str:
    prompt = f"""
        You're a professional resume writer. Generate a first-person profile summary (40–50 words) based on the candidate's name and skills below:

        Name: {info.get('full_name', '')}
        Skills: {', '.join(info.get('skills', []))}

        Guidelines:
        -Use a first-person tone (e.g., "I'm a...")
        -Focus on core technical strengths and role-relevant capabilities
        -Keep it concise, targeted, and within 40–50 words
        -Do not include location, education, or LinkedIn
        -Avoid third-person language or generic filler

        Examples for reference:
        Data Scientist:
        "I'm a Data Scientist skilled in extracting actionable insights from complex datasets using machine learning, statistical analysis, and data visualization. Experienced in building end-to-end predictive models and deploying them in real-world applications."
        Software Engineer:
        "I'm a Software Engineer skilled in building scalable and efficient web applications using Python, Django, and PostgreSQL. Experienced in developing RESTful APIs and implementing security measures to ensure data integrity."
        Full-Stack Developer:
        "I'm a Full-Stack Developer proficient in designing and building scalable web applications with expertise in both frontend and backend technologies. Adept at developing RESTful APIs, managing databases, and delivering responsive, user-friendly interfaces."

        """
    return llm.invoke(prompt).content.strip()

# ------------------- Project Description Generator -------------------

def generate_project_description(name: str, technologies: List[str]) -> str:
    prompt = f"""
        You are writing a resume project description for a technical or non-technical project.

        Project Name: {name}  
        Technologies: {', '.join(technologies)}

        Write a **concise 1-line project description (aim for 40-50 words)** that includes:
        - What the project does
        - Your contribution or key functionality
        - Tools used

        Avoid buzzwords. Be direct and technical.
        Example:  
        "Built a resume builder using Streamlit and LangChain to auto-generate tailored resumes from user inputs, reducing manual effort by 80%; integrated PDF export and multiple template options for customizable outputs."
        """
    return llm.invoke(prompt).content.strip()

# ------------------- Job Description Generator -------------------

def generate_job_description(company: str, position: str, start: str, end: str) -> str:
    prompt = f"""
        You are writing a job experience description for a resume.

        Company: {company}  
        Role: {position}  
        Duration: {start} to {end} # Do NOT mention the duration in the bullet point itself.

        Write **2 concise bullet points (aim for 40-50 words total)** focused on:
        - Technologies/tools used
        - Main responsibilities
        - Specific achievement or outcome with metrics (if any)

        Use action verbs (e.g., Developed, Built, Improved). Avoid filler language and do NOT include the duration in the bullet points.

        Example:
        - Led backend development using Java and Spring Boot, integrating RESTful APIs and optimizing database performance with PostgreSQL.
        - Mentored junior developers and implemented CI/CD pipelines with Jenkins and Docker, reducing deployment time by 30%.
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
