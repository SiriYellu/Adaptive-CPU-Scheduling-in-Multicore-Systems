"""
Script to convert the Project Proposal Markdown file to PDF.
Uses markdown2 and pdfkit (or alternatively weasyprint).
"""
import os
import sys

def convert_with_pandoc():
    """Convert using Pandoc (recommended if available)."""
    try:
        import subprocess
        
        print("Converting Project_Proposal.md to PDF using Pandoc...")
        
        # Pandoc command with nice formatting
        cmd = [
            'pandoc',
            'Project_Proposal.md',
            '-o', 'Project_Proposal.pdf',
            '--pdf-engine=xelatex',
            '-V', 'geometry:margin=1in',
            '-V', 'fontsize=11pt',
            '-V', 'documentclass=article',
            '--toc',
            '--toc-depth=3',
            '--number-sections'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ PDF created successfully: Project_Proposal.pdf")
            return True
        else:
            print(f"Pandoc error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("Pandoc not found. Please install Pandoc:")
        print("  Windows: choco install pandoc")
        print("  Or download from: https://pandoc.org/installing.html")
        return False
    except Exception as e:
        print(f"Error using Pandoc: {e}")
        return False


def convert_with_markdown2pdf():
    """Convert using markdown2pdf library."""
    try:
        from markdown2 import markdown
        from weasyprint import HTML, CSS
        
        print("Converting Project_Proposal.md to PDF using markdown2 + weasyprint...")
        
        # Read markdown file
        with open('Project_Proposal.md', 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown(md_content, extras=[
            'tables',
            'fenced-code-blocks',
            'header-ids',
            'toc'
        ])
        
        # Add CSS styling
        css_style = CSS(string='''
            @page {
                size: letter;
                margin: 1in;
            }
            body {
                font-family: "Times New Roman", Times, serif;
                font-size: 11pt;
                line-height: 1.6;
            }
            h1 {
                font-size: 18pt;
                font-weight: bold;
                margin-top: 24pt;
                margin-bottom: 12pt;
                page-break-before: always;
            }
            h1:first-of-type {
                page-break-before: avoid;
            }
            h2 {
                font-size: 14pt;
                font-weight: bold;
                margin-top: 18pt;
                margin-bottom: 10pt;
            }
            h3 {
                font-size: 12pt;
                font-weight: bold;
                margin-top: 14pt;
                margin-bottom: 8pt;
            }
            code {
                font-family: "Courier New", Courier, monospace;
                background-color: #f5f5f5;
                padding: 2px 4px;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-left: 3px solid #ccc;
                overflow-x: auto;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 12pt 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f5f5f5;
                font-weight: bold;
            }
        ''')
        
        # Create full HTML document
        full_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Project Proposal - Adaptive CPU Scheduling</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        '''
        
        # Convert to PDF
        HTML(string=full_html).write_pdf('Project_Proposal.pdf', stylesheets=[css_style])
        
        print("✓ PDF created successfully: Project_Proposal.pdf")
        return True
        
    except ImportError as e:
        print(f"Required library not found: {e}")
        print("\nInstall with:")
        print("  pip install markdown2 weasyprint")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def convert_with_reportlab():
    """Simple conversion using reportlab (fallback option)."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
        
        print("Converting using ReportLab (basic formatting)...")
        
        # Read markdown file
        with open('Project_Proposal.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create PDF
        doc = SimpleDocTemplate(
            "Project_Proposal.pdf",
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        
        # Simple parsing (this is very basic)
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                elements.append(Paragraph(line[2:], styles['Heading1']))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], styles['Heading2']))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], styles['Heading3']))
            elif line.strip() == '---':
                elements.append(PageBreak())
            elif line.strip():
                elements.append(Paragraph(line, styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(elements)
        
        print("✓ PDF created successfully: Project_Proposal.pdf")
        print("  Note: Basic formatting only. For better results, use Pandoc.")
        return True
        
    except ImportError:
        print("ReportLab not found. Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main conversion function - tries methods in order of preference."""
    
    print("="*70)
    print("PROJECT PROPOSAL PDF CONVERTER")
    print("="*70)
    print()
    
    # Check if markdown file exists
    if not os.path.exists('Project_Proposal.md'):
        print("Error: Project_Proposal.md not found!")
        print("Please make sure you're running this from the project directory.")
        return 1
    
    # Try conversion methods in order of preference
    methods = [
        ("Pandoc (Best quality)", convert_with_pandoc),
        ("Markdown2 + WeasyPrint", convert_with_markdown2pdf),
        ("ReportLab (Basic)", convert_with_reportlab)
    ]
    
    for method_name, method_func in methods:
        print(f"\nTrying: {method_name}")
        print("-" * 70)
        if method_func():
            print()
            print("="*70)
            print("SUCCESS! PDF generated: Project_Proposal.pdf")
            print("="*70)
            return 0
        print()
    
    # If all methods failed
    print("="*70)
    print("All conversion methods failed!")
    print("="*70)
    print()
    print("Alternative options:")
    print("1. Install Pandoc (recommended):")
    print("   - Download from: https://pandoc.org/installing.html")
    print("   - Or: choco install pandoc (Windows)")
    print()
    print("2. Use online converter:")
    print("   - Upload Project_Proposal.md to https://dillinger.io/")
    print("   - Export as PDF")
    print()
    print("3. Open Project_Proposal.md in VS Code:")
    print("   - Install 'Markdown PDF' extension")
    print("   - Right-click > 'Markdown PDF: Export (pdf)'")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())

