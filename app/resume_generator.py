from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import streamlit as st
import os
from pathlib import Path
from typing import Dict, Any
import tempfile
import base64
from datetime import datetime

class ResumeGenerator:
    def __init__(self):
        # Initialize Jinja2 environment
        self.template_dir = Path("templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Available templates
        self.templates = {
            "classic": "classic.html",
            "modern": "modern.html",
            "minimalist": "minimalist.html"
        }
        
        # Create output directories if they don't exist
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.preview_dir = Path("preview")
        self.preview_dir.mkdir(exist_ok=True)

    def _prepare_resume_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and format resume data for template rendering."""
        # Format dates
        for exp in data.get('experience', []):
            if exp.get('start_date'):
                exp['start_date'] = self._format_date(exp['start_date'])
            if exp.get('end_date'):
                exp['end_date'] = self._format_date(exp['end_date'])
        
        # Format education dates
        for edu in data.get('education', []):
            if edu.get('year'):
                edu['year'] = self._format_date(edu['year'])
        
        return data

    def _format_date(self, date_str: str) -> str:
        """Format date string to a more readable format."""
        if date_str.lower() == 'present':
            return 'Present'
        
        try:
            # Try parsing as YYYY-MM
            if len(date_str) == 7:
                date = datetime.strptime(date_str, '%Y-%m')
                return date.strftime('%B %Y')
            # Try parsing as YYYY
            elif len(date_str) == 4:
                return date_str
        except ValueError:
            return date_str
        
        return date_str

    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render the selected template with the provided data."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.env.get_template(self.templates[template_name])
        formatted_data = self._prepare_resume_data(data)
        return template.render(**formatted_data)

    def generate_pdf(self, html_content: str, output_filename: str) -> str:
        """Generate PDF from HTML content."""
        output_path = self.output_dir / output_filename
        
        try:
            # Generate PDF with proper encoding
            HTML(string=html_content.encode('utf-8')).write_pdf(output_path)
            return str(output_path)
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            return None

    def generate_preview(self, html_content: str) -> str:
        """Generate a preview HTML file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        preview_path = self.preview_dir / f"preview_{timestamp}.html"
        
        # Add base64 encoding for any images
        if 'profile_pic' in st.session_state.resume_data.get('personal_info', {}):
            profile_pic_path = st.session_state.resume_data['personal_info']['profile_pic']
            if os.path.exists(profile_pic_path):
                with open(profile_pic_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    html_content = html_content.replace(
                        f'src="{profile_pic_path}"',
                        f'src="data:image/png;base64,{img_data}"'
                    )
        
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Return absolute path for Streamlit
        return str(preview_path.absolute())

    def get_pdf_download_link(self, pdf_path: str) -> tuple:
        """Generate a download link for the PDF file."""
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                return pdf_bytes, f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        except Exception as e:
            st.error(f"Error creating download link: {str(e)}")
            return None, None

def show_resume_preview(generator: ResumeGenerator, template_name: str, resume_data: Dict[str, Any]):
    """Show resume preview in Streamlit UI."""
    try:
        # Render the template
        html_content = generator.render_template(template_name, resume_data)
        
        # Generate preview
        preview_path = generator.generate_preview(html_content)
        
        # Store the preview path in session state
        st.session_state.last_generated_resume = preview_path
        
        # Show preview in iframe with proper URL encoding
        preview_url = f"file://{preview_path}"
        st.components.v1.iframe(
            preview_url,
            height=800,
            scrolling=True
        )
        
        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"resume_{timestamp}.pdf"
        pdf_path = generator.generate_pdf(html_content, pdf_filename)
        
        if pdf_path:
            # Create download button with direct file bytes
            pdf_bytes, download_filename = generator.get_pdf_download_link(pdf_path)
            if pdf_bytes:
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=download_filename,
                    mime="application/pdf"
                )
            else:
                st.error("Failed to create PDF download link")
        else:
            st.error("Failed to generate PDF file")
    except Exception as e:
        st.error(f"Error in resume generation: {str(e)}")

# Example usage in Streamlit app
def render_resume_section():
    """Render the resume generation section in Streamlit."""
    st.markdown("### 📄 Resume Generation")
    
    # Initialize generator
    generator = ResumeGenerator()
    
    # Template selection
    template_name = st.selectbox(
        "Choose a template",
        options=list(generator.templates.keys()),
        format_func=lambda x: x.capitalize()
    )
    
    # Get resume data from session state
    if 'resume_data' in st.session_state:
        resume_data = st.session_state.resume_data
        
        # Show preview and download options
        if st.button("Generate Resume"):
            with st.spinner("Generating your resume..."):
                show_resume_preview(generator, template_name, resume_data)
    else:
        st.warning("Please fill out the resume form first!") 