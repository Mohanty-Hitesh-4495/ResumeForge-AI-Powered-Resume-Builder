import os
from typing import Dict, List
from datetime import datetime
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

def clean_generated_text(text: str) -> str:
    """Clean generated text by removing quotes and extra whitespace."""
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove surrounding quotes if present
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    elif text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    
    # Remove any remaining quotes at the beginning or end
    text = text.strip('"\'')
    
    return text.strip()

# ------------------- Summary Generator -------------------

def generate_profile_summary(info: Dict[str, str], skills: List[str], experience: List[Dict] = None, education: List[Dict] = None) -> str:
    # Determine primary role based on experience and skills
    primary_role = "Professional"
    if experience:
        # Get the most recent position
        latest_exp = experience[0] if experience else {}
        position = latest_exp.get('position', '').lower()
        if any(keyword in position for keyword in ['engineer', 'developer', 'programmer']):
            primary_role = "Software Engineer"
        elif any(keyword in position for keyword in ['scientist', 'analyst', 'ml', 'ai']):
            primary_role = "Data Scientist"
        elif any(keyword in position for keyword in ['manager', 'lead', 'architect']):
            primary_role = "Technical Leader"
        elif any(keyword in position for keyword in ['full-stack', 'fullstack', 'frontend', 'backend']):
            primary_role = "Full-Stack Developer"
    
    # Identify key technologies and achievements
    key_technologies = []
    achievements = []
    
    # Extract technologies from experience
    if experience:
        for exp in experience:
            tech = exp.get('technologies', '')
            if tech:
                key_technologies.extend([t.strip() for t in tech.split(',')])
    
    # Add skills if not already covered
    for skill in skills:
        if skill not in key_technologies:
            key_technologies.append(skill)
    
    # Limit to top 5-6 most relevant technologies
    key_technologies = key_technologies[:6]
    
    # Determine years of experience
    years_exp = 0
    if experience:
        for exp in experience:
            start = exp.get('start_date', '')
            end = exp.get('end_date', '')
            if start and end != 'Present':
                try:
                    start_year = int(start[:4])
                    end_year = int(end[:4]) if end != 'Present' else datetime.now().year
                    years_exp += (end_year - start_year)
                except:
                    pass
    
    # Build a more targeted prompt
    prompt = f"""
        You're a professional resume writer. Generate an impressive first-person profile summary (40–50 words) for a {primary_role}.

        Candidate Details:
        Name: {info.get('full_name', '')}
        Primary Role: {primary_role}
        Years of Experience: {years_exp} years
        Key Technologies: {', '.join(key_technologies)}
        
        Recent Experience: {experience[0].get('position', '') if experience else 'None'} at {experience[0].get('company', '') if experience else 'None'}
        
        Education: {education[0].get('degree', '') if education else 'None'} from {education[0].get('institution', '') if education else 'None'}

        Guidelines:
        - Start with "I'm a [role]" or "Experienced [role]"
        - Mention specific achievements or impact (e.g., "led teams", "improved performance by X%", "built scalable systems")
        - Include 2-3 key technologies that match the role
        - Show progression or specialization (e.g., "specializing in", "with expertise in")
        - Keep it 40-50 words, impactful and specific
        - Avoid generic phrases like "skilled in" or "proficient in"

        Examples:
        Software Engineer: "I'm a Software Engineer with 3+ years building scalable web applications using React and Node.js. Led development of microservices architecture improving system performance by 40%, specializing in cloud deployment and CI/CD pipelines."
        
        Data Scientist: "Experienced Data Scientist with expertise in machine learning and statistical analysis. Built predictive models for financial forecasting achieving 95% accuracy, proficient in Python, TensorFlow, and big data technologies."
        
        Full-Stack Developer: "I'm a Full-Stack Developer with 4+ years creating end-to-end solutions using React, Node.js, and cloud technologies. Delivered 15+ production applications, specializing in scalable architecture and user experience optimization."

        Generate a compelling summary that showcases specific achievements and technical expertise.
        IMPORTANT: Do not wrap your response in quotes. Return the summary directly without any quotation marks.
        """
    response = llm.invoke(prompt).content.strip()
    return clean_generated_text(response)

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
        IMPORTANT: Do not wrap your response in quotes. Return the description directly without any quotation marks.
        
        Example:  
        Built a resume builder using Streamlit and LangChain to auto-generate tailored resumes from user inputs, reducing manual effort by 80%; integrated PDF export and multiple template options for customizable outputs.
        """
    response = llm.invoke(prompt).content.strip()
    return clean_generated_text(response)

# ------------------- Job Description Generator -------------------

def generate_job_description(company: str, position: str, start: str, end: str, technologies: str = "") -> str:
    prompt = f"""
        You are writing a concise, impactful job experience summary for a resume.

        Company: {company}
        Role: {position}
        Technologies: {technologies}

        Write a single, direct 1–2 line summary (max 50 words) that includes:
        - What you did in this role (main responsibility or achievement)
        - The technologies/tools you used
        - Any specific impact, result, or metric (if available)

        Be specific, avoid generic phrases, and do not mention the duration. Use a first-person or active voice.
        IMPORTANT: Do not wrap your response in quotes. Return the description directly without any quotation marks.

        Example:
        Developed scalable REST APIs using Python and FastAPI, improving data processing speed by 30% for financial analytics. Led a team of 3 engineers and integrated CI/CD pipelines with Docker and GitHub Actions.
        """
    response = llm.invoke(prompt).content.strip()
    return clean_generated_text(response)

# ------------------- Example Usage -------------------

if __name__ == "__main__":
    # Test Profile Summary
    personal_info = {
        "full_name": "John Doe"
    }
    skills = ["Python", "Machine Learning", "Data Analysis"]
    experience = [
        {
            "position": "Data Scientist",
            "company": "TechCorp",
            "start_date": "2022-01",
            "end_date": "Present",
            "technologies": "Python, TensorFlow, SQL"
        }
    ]
    education = [
        {
            "degree": "Master of Science in Data Science",
            "institution": "University of Technology"
        }
    ]
    print("🔹 Profile Summary:\n", generate_profile_summary(personal_info, skills, experience, education))

    # Test Project Description
    print("\n🔹 Project Description:\n", generate_project_description(
        "Resume Builder", ["HTML", "CSS", "LangChain", "Groq"]
    ))

    # Test Job Description
    print("\n🔹 Job Description:\n", generate_job_description(
        "TechCorp", "Software Engineer", "Jan 2022", "May 2024"
    ))
