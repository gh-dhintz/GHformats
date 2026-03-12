#!/usr/bin/env python3
"""
Generate 3x1 preview montages from PDF and Word documents.
Creates crisp preview images showing the first 3 pages of each template.
Also generates screenshots from HTML files.
"""

from PIL import Image
import glob
import os
import subprocess
import sys
import tempfile
import shutil
import zipfile

# Configuration
EXAMPLES_DIR = "resources/examples"
OUTPUT_DIR = "vignettes/images"
TEMP_DIR = tempfile.mkdtemp(prefix="ghformats_preview_")

# Montage settings (perfected for crispness)
DPI = 400
TARGET_WIDTH = 700
SPACING = 15
BORDER_PADDING = 40
BACKGROUND_COLOR = '#939393'

# Chrome path for screenshots
CHROME_PATHS = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    'google-chrome',
    'chromium',
    'chrome'
]

def extract_pdf_pages(pdf_path, output_prefix, num_pages=3):
    """Extract first N pages from PDF as PNG images at high DPI."""
    print(f"  Extracting pages from PDF...")
    cmd = [
        'pdftoppm',
        '-png',
        '-r', str(DPI),
        '-f', '1',
        '-l', str(num_pages),
        pdf_path,
        output_prefix
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Find generated pages
    pages = sorted(glob.glob(f"{output_prefix}-*.png"))
    return pages

def convert_word_to_pdf(docx_path, output_pdf):
    """Convert Word document to PDF using LibreOffice."""
    print(f"  Converting Word to PDF...")
    temp_output_dir = os.path.dirname(output_pdf)

    # Try to find LibreOffice/soffice
    soffice_paths = [
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '/usr/bin/soffice',
        '/usr/local/bin/soffice',
        'soffice',
        'libreoffice'
    ]

    soffice = None
    for path in soffice_paths:
        if os.path.exists(path) or shutil.which(path):
            soffice = path
            break

    if not soffice:
        raise FileNotFoundError("LibreOffice/soffice not found")

    cmd = [
        soffice,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', temp_output_dir,
        docx_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  WARNING: LibreOffice conversion failed. Skipping {os.path.basename(docx_path)}")
        print(f"  Error: {result.stderr}")
        return None

    # Find the generated PDF
    basename = os.path.splitext(os.path.basename(docx_path))[0]
    generated_pdf = os.path.join(temp_output_dir, f"{basename}.pdf")

    if os.path.exists(generated_pdf):
        return generated_pdf
    return None

def create_3x1_montage(page_images, output_path):
    """Create a 3x1 montage from page images."""
    if not page_images:
        print("  ERROR: No page images to process")
        return False

    # Take only first 3 pages
    page_images = page_images[:3]

    print(f"  Creating montage from {len(page_images)} pages...")

    # Load images
    images = [Image.open(page) for page in page_images]

    # Calculate montage dimensions
    total_width = (TARGET_WIDTH * len(images)) + (SPACING * (len(images) - 1)) + (BORDER_PADDING * 2)

    # Scale images to target width, maintaining aspect ratio
    scaled_images = []
    max_height = 0
    for img in images:
        aspect = img.height / img.width
        new_height = int(TARGET_WIDTH * aspect)
        scaled = img.resize((TARGET_WIDTH, new_height), Image.Resampling.LANCZOS)
        scaled_images.append(scaled)
        max_height = max(max_height, new_height)

    total_height = max_height + (BORDER_PADDING * 2)

    # Create montage with grey background
    montage = Image.new('RGB', (total_width, total_height), BACKGROUND_COLOR)

    # Paste images
    x_offset = BORDER_PADDING
    for img in scaled_images:
        # Center vertically
        y_offset = BORDER_PADDING + (max_height - img.height) // 2
        montage.paste(img, (x_offset, y_offset))
        x_offset += TARGET_WIDTH + SPACING

    # Save
    montage.save(output_path, 'PNG', optimize=True)
    file_size = os.path.getsize(output_path) / 1024
    print(f"  ✓ Saved: {os.path.basename(output_path)} ({montage.size[0]}x{montage.size[1]}, {file_size:.0f}KB)")

    return True

def process_pdf(pdf_path, output_name):
    """Process a PDF file and create montage."""
    output_path = os.path.join(OUTPUT_DIR, output_name)

    # Extract pages
    page_prefix = os.path.join(TEMP_DIR, os.path.splitext(os.path.basename(pdf_path))[0])
    page_images = extract_pdf_pages(pdf_path, page_prefix)

    # Create montage
    success = create_3x1_montage(page_images, output_path)

    # Cleanup temp images
    for page in page_images:
        try:
            os.remove(page)
        except:
            pass

    return success

def process_word(docx_path, output_name):
    """Process a Word document and create montage."""
    output_path = os.path.join(OUTPUT_DIR, output_name)

    # Convert to PDF first
    temp_pdf = os.path.join(TEMP_DIR, "temp_word.pdf")
    converted_pdf = convert_word_to_pdf(docx_path, temp_pdf)

    if not converted_pdf:
        return False

    # Extract pages from converted PDF
    page_prefix = os.path.join(TEMP_DIR, "word_page")
    page_images = extract_pdf_pages(converted_pdf, page_prefix)

    # Create montage
    success = create_3x1_montage(page_images, output_path)

    # Cleanup
    for page in page_images:
        try:
            os.remove(page)
        except:
            pass
    try:
        os.remove(converted_pdf)
    except:
        pass

    return success

def find_chrome():
    """Find Chrome executable."""
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
        if shutil.which(path):
            return shutil.which(path)
    return None

def screenshot_html(html_path, output_png, width=2100, height=1400):
    """Take a single crisp screenshot of an HTML file using Playwright."""
    from playwright.sync_api import sync_playwright

    # Convert to absolute path
    html_abs = os.path.abspath(html_path)
    html_url = f"file://{html_abs}"

    print(f"  Taking screenshot with Playwright...")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={'width': width, 'height': height},
            device_scale_factor=2  # 2x scaling for retina/crisp quality
        )

        # Navigate to page
        page.goto(html_url, wait_until='networkidle', timeout=30000)

        # Take screenshot (viewport only, not full page)
        page.screenshot(path=output_png, full_page=False)

        # Close browser
        browser.close()

    return output_png

def split_screenshot_into_3(screenshot_path, output_prefix):
    """Split a full screenshot into 3 roughly equal horizontal sections."""
    img = Image.open(screenshot_path)
    width, height = img.size

    # Split into 3 sections
    section_height = height // 3

    sections = []
    for i in range(3):
        top = i * section_height
        bottom = top + section_height if i < 2 else height  # Last section gets remainder

        section = img.crop((0, top, width, bottom))
        section_path = f"{output_prefix}_section_{i+1}.png"
        section.save(section_path, 'PNG')
        sections.append(section_path)

    return sections

def convert_ipynb_to_html(ipynb_path, output_html):
    """Convert Jupyter notebook to HTML using nbconvert."""
    print(f"  Converting notebook to HTML...")
    cmd = [
        'jupyter',
        'nbconvert',
        '--to', 'html',
        '--output', output_html,
        ipynb_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # Try alternative method
        print(f"  Jupyter nbconvert failed, trying python -m...")
        cmd = [
            'python3',
            '-m',
            'jupyter',
            'nbconvert',
            '--to', 'html',
            '--output', output_html,
            ipynb_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  WARNING: Jupyter conversion failed: {result.stderr}")
        return None

    # nbconvert adds .html extension, find the actual output
    expected = output_html if output_html.endswith('.html') else output_html + '.html'
    if os.path.exists(expected):
        return expected

    return None

def process_html(html_path, output_name):
    """Process an HTML file and create a single crisp screenshot."""
    output_path = os.path.join(OUTPUT_DIR, output_name)

    # Take single screenshot directly to output
    screenshot_html(html_path, output_path)

    # Print success info
    file_size = os.path.getsize(output_path) / 1024
    img = Image.open(output_path)
    print(f"  ✓ Saved: {os.path.basename(output_path)} ({img.size[0]}x{img.size[1]}, {file_size:.0f}KB)")

    return True

def process_jupyter_zip(zip_path, output_name):
    """Unzip, convert Jupyter notebook to HTML, and create screenshot."""
    output_path = os.path.join(OUTPUT_DIR, output_name)

    print(f"  Extracting zip file...")
    extract_dir = os.path.join(TEMP_DIR, "jupyter_extract")
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # Find the .ipynb file
    ipynb_files = glob.glob(os.path.join(extract_dir, "**/*.ipynb"), recursive=True)

    if not ipynb_files:
        print(f"  ERROR: No .ipynb file found in zip")
        return False

    ipynb_path = ipynb_files[0]
    notebook_dir = os.path.dirname(ipynb_path)
    print(f"  Found notebook: {os.path.basename(ipynb_path)}")

    # Convert to HTML (output to same directory as notebook so relative paths work)
    html_output = os.path.join(notebook_dir, "jupyter_notebook.html")
    html_path = convert_ipynb_to_html(ipynb_path, html_output)

    if not html_path:
        return False

    # Process the HTML (this will screenshot it)
    success = process_html(html_path, output_name)

    # Cleanup
    try:
        shutil.rmtree(extract_dir)
    except:
        pass

    return success

def main():
    print("\n" + "="*60)
    print("  GHformats Preview Montage Generator")
    print("="*60 + "\n")

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Define templates to process with their output names
    templates = [
        # RMarkdown PDFs
        ("demo_rmd_pdf_report.pdf", "img_preview_rmd_pdf_report.png", "pdf"),
        ("demo_rmd_pdf_simple.pdf", "img_preview_rmd_pdf_simple.png", "pdf"),
        ("demo_rmd_pdf_cheatsheet.pdf", "img_preview_rmd_pdf_cheatsheet.png", "pdf"),

        # Quarto PDFs
        ("demo_quarto_pdf_report.pdf", "img_preview_quarto_pdf_report.png", "pdf"),
        ("demo_quarto_pdf_simple.pdf", "img_preview_quarto_pdf_simple.png", "pdf"),

        # RMarkdown Word
        ("demo_rmd_word_doc.docx", "img_preview_rmd_word.png", "word"),

        # Quarto Word
        ("demo_quarto_word.docx", "img_preview_quarto_word.png", "word"),

        # HTML templates
        ("demo_rmd_html_simple.html", "img_preview_rmd_html_simple.png", "html"),
        ("demo_rmd_html_material.html", "img_preview_rmd_html_material.png", "html"),
        ("demo_quarto_html.html", "img_preview_quarto_html.png", "html"),

        # Jupyter notebook (special case - zip file)
        ("demo_rmd_to_jupyter.zip", "img_preview_rmd_jupyter.png", "jupyter"),
    ]

    success_count = 0
    fail_count = 0

    for template_file, output_name, file_type in templates:
        input_path = os.path.join(EXAMPLES_DIR, template_file)

        if not os.path.exists(input_path):
            print(f"⚠ Skipping {template_file} (not found)")
            fail_count += 1
            continue

        print(f"\nProcessing: {template_file}")

        try:
            if file_type == "pdf":
                success = process_pdf(input_path, output_name)
            elif file_type == "word":
                success = process_word(input_path, output_name)
            elif file_type == "html":
                success = process_html(input_path, output_name)
            elif file_type == "jupyter":
                success = process_jupyter_zip(input_path, output_name)
            else:
                print(f"  Unsupported file type: {file_type}")
                success = False

            if success:
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    # Cleanup temp directory
    try:
        shutil.rmtree(TEMP_DIR)
    except:
        pass

    print("\n" + "="*60)
    print(f"  Complete! {success_count} succeeded, {fail_count} failed")
    print("="*60 + "\n")

    return 0 if fail_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
