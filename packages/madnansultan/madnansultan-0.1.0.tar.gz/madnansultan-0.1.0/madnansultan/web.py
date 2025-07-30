from flask import Flask, render_template_string, request, jsonify
from .data import portfolio

app = Flask(__name__)

base_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Muhammad Adnan Sultan</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #2d3748;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .header .subtitle {
            font-size: 1.2rem;
            color: #718096;
            margin-bottom: 1.5rem;
        }

        .contact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .contact-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .contact-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }

        .contact-item a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .contact-item i {
            color: #667eea;
            font-size: 1.1rem;
        }

        nav {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 0.5rem;
        }

        nav a {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0.75rem 1rem;
            text-decoration: none;
            color: #4a5568;
            font-weight: 500;
            border-radius: 10px;
            transition: all 0.3s ease;
            background: rgba(102, 126, 234, 0.05);
        }

        nav a:hover, nav a.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }

        .content {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            animation: fadeInUp 0.6s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h2 {
            font-size: 2rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 1.5rem;
            position: relative;
        }

        h2::after {
            content: '';
            position: absolute;
            bottom: -0.5rem;
            left: 0;
            width: 60px;
            height: 3px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 2px;
        }

        .section-grid {
            display: grid;
            gap: 1.5rem;
        }

        .card {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
        }

        .card h3 {
            font-size: 1.3rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }

        .card .meta {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        .card .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .tech-tag {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .skill-category {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }

        .skill-category h3 {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 1rem;
        }

        .skill-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .skill-item {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 500;
        }

        ul {
            list-style: none;
        }

        li {
            margin-bottom: 0.5rem;
            padding-left: 1rem;
            position: relative;
        }

        li::before {
            content: '•';
            color: #667eea;
            font-weight: bold;
            position: absolute;
            left: 0;
        }

        a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        a:hover {
            color: #764ba2;
        }

        .export-section {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(102, 126, 234, 0.2);
        }

        .export-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .export-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 10px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }

        .export-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .nav-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ portfolio.name }}</h1>
            <div class="subtitle">{{ portfolio.location }}</div>
            <div class="contact-grid">
                <div class="contact-item">
                    <i class="fas fa-envelope"></i>
                    <a href="mailto:{{ portfolio.contact.email }}">{{ portfolio.contact.email }}</a>
                </div>
                <div class="contact-item">
                    <i class="fas fa-phone"></i>
                    <span>{{ portfolio.contact.phone }}</span>
                </div>
                <div class="contact-item">
                    <i class="fab fa-linkedin"></i>
                    <a href="{{ portfolio.contact.linkedin }}" target="_blank">LinkedIn</a>
                </div>
                <div class="contact-item">
                    <i class="fab fa-github"></i>
                    <a href="{{ portfolio.contact.github }}" target="_blank">GitHub</a>
                </div>
            </div>
        </div>

        <nav>
            <div class="nav-grid">
                <a href="/" class="{{ 'active' if request.endpoint == 'home' else '' }}">
                    <i class="fas fa-home"></i> Home
                </a>
                <a href="/education" class="{{ 'active' if request.endpoint == 'education' else '' }}">
                    <i class="fas fa-graduation-cap"></i> Education
                </a>
                <a href="/experience" class="{{ 'active' if request.endpoint == 'experience' else '' }}">
                    <i class="fas fa-briefcase"></i> Experience
                </a>
                <a href="/projects" class="{{ 'active' if request.endpoint == 'projects' else '' }}">
                    <i class="fas fa-code"></i> Projects
                </a>
                <a href="/skills" class="{{ 'active' if request.endpoint == 'skills' else '' }}">
                    <i class="fas fa-tools"></i> Skills
                </a>
                <a href="/awards" class="{{ 'active' if request.endpoint == 'awards' else '' }}">
                    <i class="fas fa-trophy"></i> Awards
                </a>
                <a href="/certifications" class="{{ 'active' if request.endpoint == 'certifications' else '' }}">
                    <i class="fas fa-certificate"></i> Certifications
                </a>
            </div>
        </nav>

        <div class="content">
            {{ content|safe }}
            
                    <div class="export-section">
            <h3>Export Portfolio</h3>
            <div class="export-buttons">
                <a href="/export/json" class="export-btn">
                    <i class="fas fa-download"></i> Export JSON
                </a>
                <a href="/export/csv" class="export-btn">
                    <i class="fas fa-download"></i> Export CSV
                </a>
                <a href="/export/text" class="export-btn">
                    <i class="fas fa-download"></i> Export Text
                </a>
                <a href="/export/pdf" class="export-btn">
                    <i class="fas fa-file-pdf"></i> Export PDF
                </a>
            </div>
        </div>
        </div>
    </div>
</body>
</html>
'''

def render_section(title, content):
    return render_template_string(base_template, title=title, content=content, portfolio=portfolio)

@app.route('/')
def home():
    content = f"""
    <h2>Welcome to My Portfolio</h2>
    <p>I'm a passionate Computer Science student and developer with expertise in web development, machine learning, and software engineering. Explore the sections above to learn more about my education, experience, projects, and skills.</p>
    
    <div class="section-grid">
        <div class="card">
            <h3><i class="fas fa-graduation-cap"></i> Education</h3>
            <p>Bachelor's in Computer Science from Quaid e Azam University with a strong foundation in programming, algorithms, and software development.</p>
        </div>
        <div class="card">
            <h3><i class="fas fa-briefcase"></i> Experience</h3>
            <p>Experience in web development, AI engineering, and front-end development with companies like The Daily Frontier and AITEC National Centre of Physics.</p>
        </div>
        <div class="card">
            <h3><i class="fas fa-code"></i> Projects</h3>
            <p>Diverse portfolio including AI applications, web development projects, and desktop applications using modern technologies.</p>
        </div>
    </div>
    """
    return render_section("Home", content)

@app.route('/education')
def education():
    content = "<h2>Education</h2><div class='section-grid'>"
    for edu in portfolio['education']:
        content += f"""
        <div class="card">
            <h3>{edu['degree']}</h3>
            <div class="meta">{edu['institution']} • {edu['duration']} • {edu['location']}</div>
            <p><strong>Relevant Courses:</strong></p>
            <ul>
        """
        for course in edu['courses']:
            content += f"<li>{course}</li>"
        content += "</ul></div>"
    content += "</div>"
    return render_section("Education", content)

@app.route('/experience')
def experience():
    content = "<h2>Experience</h2><div class='section-grid'>"
    for exp in portfolio['experience']:
        content += f"""
        <div class="card">
            <h3>{exp['title']}</h3>
            <div class="meta">{exp['company']} • {exp['duration']} • {exp['location']}</div>
            <ul>
        """
        for detail in exp['details']:
            content += f"<li>{detail}</li>"
        content += "</ul></div>"
    content += "</div>"
    return render_section("Experience", content)

@app.route('/projects')
def projects():
    content = "<h2>Projects</h2><div class='section-grid'>"
    for proj in portfolio['projects']:
        content += f"""
        <div class="card">
            <h3>{proj['name']}</h3>
            <div class="meta">{proj['date']} • <a href='{proj['url']}' target='_blank'>View Project</a></div>
            <ul>
        """
        for detail in proj['details']:
            content += f"<li>{detail}</li>"
        content += "</ul>"
        content += f"<div class='tech-stack'>"
        for tech in proj['technologies']:
            content += f"<span class='tech-tag'>{tech}</span>"
        content += "</div></div>"
    content += "</div>"
    return render_section("Projects", content)

@app.route('/skills')
def skills():
    content = "<h2>Skills</h2><div class='skills-grid'>"
    content += f"""
    <div class="skill-category">
        <h3>Core Skills</h3>
        <div class="skill-list">
    """
    for skill in portfolio['skills']['core']:
        content += f"<span class='skill-item'>{skill}</span>"
    content += "</div></div>"
    
    content += f"""
    <div class="skill-category">
        <h3>Technical Skills</h3>
        <div class="skill-list">
    """
    for skill in portfolio['skills']['technical']:
        content += f"<span class='skill-item'>{skill}</span>"
    content += "</div></div></div>"
    return render_section("Skills", content)

@app.route('/awards')
def awards():
    content = "<h2>Honours and Awards</h2><div class='section-grid'>"
    for award in portfolio['awards']:
        content += f"""
        <div class="card">
            <h3>{award['title']}</h3>
            <div class="meta">{award['date']} • {award['location']}</div>
            <p>{award['description']}</p>
        </div>
        """
    content += "</div>"
    return render_section("Awards", content)

@app.route('/certifications')
def certifications():
    content = "<h2>Certifications</h2><div class='section-grid'>"
    for cert in portfolio['certifications']:
        content += f"""
        <div class="card">
            <h3>{cert['title']}</h3>
            <div class="meta"><a href='{cert['url']}' target='_blank'>View Certificate</a></div>
            <p><strong>Details:</strong> {', '.join(cert['details'])}</p>
        </div>
        """
    content += "</div>"
    return render_section("Certifications", content)

@app.route('/export/<format>')
def export(format):
    from .cli import export_json, export_csv, export_text, export_pdf
    
    if format == 'json':
        return jsonify(portfolio)
    elif format == 'pdf':
        import io
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#667eea')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2d3748')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Title
        story.append(Paragraph("MUHAMMAD ADNAN SULTAN", title_style))
        story.append(Paragraph("Portfolio", title_style))
        story.append(Spacer(1, 20))
        
        # Contact Information
        story.append(Paragraph("Contact Information", heading_style))
        contact_data = [
            ['Location:', portfolio['location']],
            ['Phone:', portfolio['contact']['phone']],
            ['Email:', portfolio['contact']['email']],
            ['LinkedIn:', portfolio['contact']['linkedin']],
            ['GitHub:', portfolio['contact']['github']]
        ]
        contact_table = Table(contact_data, colWidths=[1.5*inch, 4*inch])
        contact_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(contact_table)
        story.append(Spacer(1, 20))
        
        # Education
        story.append(Paragraph("Education", heading_style))
        for edu in portfolio['education']:
            edu_text = f"<b>{edu['degree']}</b><br/>"
            edu_text += f"<i>{edu['institution']}</i><br/>"
            edu_text += f"Duration: {edu['duration']} | Location: {edu['location']}<br/>"
            edu_text += f"<b>Courses:</b> {', '.join(edu['courses'])}"
            story.append(Paragraph(edu_text, normal_style))
            story.append(Spacer(1, 12))
        
        # Experience
        story.append(Paragraph("Experience", heading_style))
        for exp in portfolio['experience']:
            exp_text = f"<b>{exp['title']}</b> at <b>{exp['company']}</b><br/>"
            exp_text += f"<i>{exp['duration']} | {exp['location']}</i><br/>"
            for detail in exp['details']:
                exp_text += f"• {detail}<br/>"
            story.append(Paragraph(exp_text, normal_style))
            story.append(Spacer(1, 12))
        
        # Projects
        story.append(Paragraph("Projects", heading_style))
        for proj in portfolio['projects']:
            proj_text = f"<b>{proj['name']}</b> [{proj['date']}]<br/>"
            proj_text += f"<i>Technologies: {', '.join(proj['technologies'])}</i><br/>"
            proj_text += f"<i>URL: {proj['url']}</i><br/>"
            for detail in proj['details']:
                proj_text += f"• {detail}<br/>"
            story.append(Paragraph(proj_text, normal_style))
            story.append(Spacer(1, 12))
        
        # Skills
        story.append(Paragraph("Skills", heading_style))
        skills_text = f"<b>Core Skills:</b> {', '.join(portfolio['skills']['core'])}<br/>"
        skills_text += f"<b>Technical Skills:</b> {', '.join(portfolio['skills']['technical'])}"
        story.append(Paragraph(skills_text, normal_style))
        story.append(Spacer(1, 20))
        
        # Awards
        story.append(Paragraph("Awards", heading_style))
        for award in portfolio['awards']:
            award_text = f"<b>{award['title']}</b> ({award['date']}, {award['location']})<br/>"
            award_text += f"{award['description']}"
            story.append(Paragraph(award_text, normal_style))
            story.append(Spacer(1, 12))
        
        # Certifications
        story.append(Paragraph("Certifications", heading_style))
        for cert in portfolio['certifications']:
            cert_text = f"<b>{cert['title']}</b><br/>"
            cert_text += f"<i>URL: {cert['url']}</i><br/>"
            cert_text += f"<b>Details:</b> {', '.join(cert['details'])}"
            story.append(Paragraph(cert_text, normal_style))
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=portfolio.pdf'}
    elif format == 'csv':
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Section', 'Field', 'Value'])
        
        # Education
        for edu in portfolio['education']:
            writer.writerow(['Education', 'Degree', edu['degree']])
            writer.writerow(['Education', 'Institution', edu['institution']])
            writer.writerow(['Education', 'Duration', edu['duration']])
            writer.writerow(['Education', 'Location', edu['location']])
            writer.writerow(['Education', 'Courses', '; '.join(edu['courses'])])
        
        # Experience
        for exp in portfolio['experience']:
            writer.writerow(['Experience', 'Title', exp['title']])
            writer.writerow(['Experience', 'Company', exp['company']])
            writer.writerow(['Experience', 'Duration', exp['duration']])
            writer.writerow(['Experience', 'Location', exp['location']])
            writer.writerow(['Experience', 'Details', '; '.join(exp['details'])])
        
        # Projects
        for proj in portfolio['projects']:
            writer.writerow(['Projects', 'Name', proj['name']])
            writer.writerow(['Projects', 'Date', proj['date']])
            writer.writerow(['Projects', 'Technologies', '; '.join(proj['technologies'])])
            writer.writerow(['Projects', 'URL', proj['url']])
            writer.writerow(['Projects', 'Details', '; '.join(proj['details'])])
        
        output.seek(0)
        return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=portfolio.csv'}
    elif format == 'text':
        content = []
        content.append("MUHAMMAD ADNAN SULTAN - PORTFOLIO")
        content.append("=" * 50)
        content.append(f"Location: {portfolio['location']}")
        content.append("Contact:")
        for k, v in portfolio['contact'].items():
            content.append(f"  {k.title()}: {v}")
        
        content.append("\nEDUCATION")
        content.append("-" * 20)
        for edu in portfolio['education']:
            content.append(f"{edu['degree']} at {edu['institution']}")
            content.append(f"Duration: {edu['duration']}, Location: {edu['location']}")
            content.append(f"Courses: {', '.join(edu['courses'])}")
            content.append("")
        
        content.append("EXPERIENCE")
        content.append("-" * 20)
        for exp in portfolio['experience']:
            content.append(f"{exp['title']} at {exp['company']}")
            content.append(f"Duration: {exp['duration']}, Location: {exp['location']}")
            for detail in exp['details']:
                content.append(f"  • {detail}")
            content.append("")
        
        content.append("PROJECTS")
        content.append("-" * 20)
        for proj in portfolio['projects']:
            content.append(f"{proj['name']} [{proj['date']}]")
            content.append(f"Technologies: {', '.join(proj['technologies'])}")
            content.append(f"URL: {proj['url']}")
            for detail in proj['details']:
                content.append(f"  • {detail}")
            content.append("")
        
        content.append("SKILLS")
        content.append("-" * 20)
        content.append(f"Core Skills: {', '.join(portfolio['skills']['core'])}")
        content.append(f"Technical Skills: {', '.join(portfolio['skills']['technical'])}")
        content.append("")
        
        content.append("AWARDS")
        content.append("-" * 20)
        for award in portfolio['awards']:
            content.append(f"{award['title']} ({award['date']}, {award['location']})")
            content.append(f"  {award['description']}")
            content.append("")
        
        content.append("CERTIFICATIONS")
        content.append("-" * 20)
        for cert in portfolio['certifications']:
            content.append(f"{cert['title']}")
            content.append(f"URL: {cert['url']}")
            content.append(f"Details: {', '.join(cert['details'])}")
            content.append("")
        
        return '\n'.join(content), 200, {'Content-Type': 'text/plain', 'Content-Disposition': 'attachment; filename=portfolio.txt'}

if __name__ == "__main__":
    app.run(debug=True) 