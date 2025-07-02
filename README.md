<div align="center">
  <h1> ResumeForge: AI-Powered Resume Builder </h1>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-412991?style=for-the-badge&logo=groq&logoColor=white" />
  <img src="https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black" />
  <img src="https://img.shields.io/badge/jinja-white.svg?style=for-the-badge&logo=jinja&logoColor=black" />
  <img src="https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white" />

  <h3>ResumeForge is an intelligent resume builder that helps you create professional resumes with AI-powered suggestions and beautiful templates. 🚀</h3>
</div>

## Features

- Smart Resume Builder with intuitive form interface
- Multiple professional templates (Classic, Modern, Minimalist)
- AI-powered content suggestions using Groq
- Easy export to PDF
- Real-time preview
- Automatic backup system

## Prerequisites

- Python 3.12 or higher
- pip (Python package installer)
- A Groq API key (for AI features)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Mohanty-Hitesh-4495/ResumeForge-AI-Powered-Resume-Builder.git
cd resume_builder
```

2. Create a virtual environment (recommended):
```bash
# Windows
python -m venv myenv
myenv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Directory Structure

```
resume_builder/
├── app/
│   ├── form.py
│   ├── resume_generator.py
│   └── summarizer_agent.py
├── templates/
│   ├── classic.html
│   ├── modern.html
│   └── minimalist.html
├── assets/
├── backups/
├── output/
├── preview/
├── .env
├── requirements.txt
└── README.md
```

## Running the Application

1. Make sure your virtual environment is activated

2. Run the Streamlit app:
```bash
streamlit run app/Home.py
```

3. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

## Usage

1. Start at the home page and click "Start Building Your Resume"
2. Fill out your information in the form sections:
   - Personal Information
   - Experience
   - Education
   - Skills
   - Projects
   - Certifications
   - Languages
3. Use the AI-powered suggestions to enhance your content
4. Choose a template and generate your resume
5. Download your resume as a PDF

## Notes

- The application automatically saves backups of your resume data
- You can load sample data to see how the resume builder works
- The AI features require a valid Groq API key
- Generated resumes are saved in the `output` directory
- Preview files are stored in the `preview` directory

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed correctly
2. Verify your Groq API key is valid and properly set in the `.env` file
3. Check that all required directories exist (assets, backups, output, preview)
4. Ensure you have write permissions in the application directory

## License

This project is licensed under the MIT License - see the [MIT LICENSE](https://github.com/Mohanty-Hitesh-4495/ResumeForge-AI-Powered-Resume-Builder/blob/main/LICENSE) file for details.
