import argparse
import json
import csv
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from .data import portfolio

def print_section(section):
    if section == "education":
        print("\nEDUCATION:")
        for edu in portfolio["education"]:
            print(f"- {edu['degree']} at {edu['institution']} ({edu['duration']}, {edu['location']})")
            print(f"  Courses: {', '.join(edu['courses'])}")
    elif section == "experience":
        print("\nEXPERIENCE:")
        for exp in portfolio["experience"]:
            print(f"- {exp['title']} at {exp['company']} ({exp['duration']}, {exp['location']})")
            for d in exp['details']:
                print(f"  * {d}")
    elif section == "projects":
        print("\nPROJECTS:")
        for proj in portfolio["projects"]:
            print(f"- {proj['name']} [{proj['date']}] ({', '.join(proj['technologies'])})")
            print(f"  {proj['url']}")
            for d in proj['details']:
                print(f"  * {d}")
    elif section == "skills":
        print("\nSKILLS:")
        print("Core Skills:", ', '.join(portfolio['skills']['core']))
        print("Technical Skills:", ', '.join(portfolio['skills']['technical']))
    elif section == "awards":
        print("\nHONOURS AND AWARDS:")
        for award in portfolio["awards"]:
            print(f"- {award['title']} ({award['date']}, {award['location']})")
            print(f"  {award['description']}")
    elif section == "certifications":
        print("\nCERTIFICATIONS:")
        for cert in portfolio["certifications"]:
            print(f"- {cert['title']} [{cert['url']}] - {', '.join(cert['details'])}")
    else:
        print("\nMuhammad Adnan Sultan - Portfolio")
        print("Location:", portfolio["location"])
        print("Contact:")
        for k, v in portfolio["contact"].items():
            print(f"  {k.title()}: {v}")
        print("\nSections: education, experience, projects, skills, awards, certifications")
        print("Use --section <name> to view a section.")

def export_json(output_file=None):
    """Export portfolio data to JSON format"""
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, indent=2, ensure_ascii=False)
        print(f"Portfolio exported to {output_file}")
    else:
        print(json.dumps(portfolio, indent=2, ensure_ascii=False))

def export_csv(output_file=None):
    """Export portfolio data to CSV format"""
    if output_file:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
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
        
        print(f"Portfolio exported to {output_file}")
    else:
        print("CSV export requires an output file. Use --output <filename>")

def export_text(output_file=None):
    """Export portfolio data to plain text format"""
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
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"Portfolio exported to {output_file}")
    else:
        print('\n'.join(content))

def export_pdf(output_file=None):
    """Export portfolio data to PDF format"""
    if not output_file:
        output_file = "portfolio.pdf"
    
    doc = SimpleDocTemplate(output_file, pagesize=A4)
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
    print(f"Portfolio exported to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Muhammad Adnan Sultan Portfolio CLI")
    parser.add_argument('--section', type=str, help='Section to display')
    parser.add_argument('--export', action='store_true', help='Export portfolio data')
    parser.add_argument('--format', type=str, choices=['json', 'csv', 'text', 'pdf'], default='json', help='Export format (default: json)')
    parser.add_argument('--output', type=str, help='Output file for export')
    args = parser.parse_args()
    
    if args.export:
        if args.format == 'json':
            export_json(args.output)
        elif args.format == 'csv':
            export_csv(args.output)
        elif args.format == 'text':
            export_text(args.output)
        elif args.format == 'pdf':
            export_pdf(args.output)
    else:
        print_section(args.section if args.section else None)

if __name__ == "__main__":
    main() 