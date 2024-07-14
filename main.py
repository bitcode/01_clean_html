import os
import shutil
import re
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pygments.lexers import guess_lexer, ClassNotFound

# Configure logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

def extract_metadata(soup, content):
    title = soup.title.string if soup.title else "N/A"
    date_meta = soup.find('meta', attrs={"name": "date"})
    date = date_meta['content'] if date_meta else str(datetime.now())
    projectname_div = soup.find('div', id='projectname')
    version_span = projectname_div.find('span', id='projectnumber') if projectname_div else None
    version = version_span.text.strip() if version_span else "N/A"
    library_name = projectname_div.text.strip().split()[0] if projectname_div else "N/A"
    try:
        lexer = guess_lexer(content)
        programming_language = lexer.name
    except ClassNotFound:
        programming_language = "N/A"

    metadata = {
        "title": title,
        "library": library_name,
        "version": version,
        "date": date,
        "programming_language": programming_language
    }
    
    return metadata

def extract_sections(soup):
    sections = {}
    for header in soup.find_all(re.compile('^h[1-6]$')):
        section_name = header.text.strip()
        next_node = header.find_next_sibling()
        section_content = []
        while next_node and next_node.name not in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            section_content.append(next_node)
            next_node = next_node.find_next_sibling()
        sections[section_name] = ' '.join(str(tag) for tag in section_content)
    return sections

def extract_links(soup):
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        context = link.get_text()
        links.append({"href": href, "context": context})
    return links

def extract_code(soup):
    code_blocks = []
    for code in soup.find_all('code'):
        code_text = code.get_text()
        context = code.find_previous(string=True)
        code_blocks.append({"code": code_text, "context": context})
    return code_blocks

def find_image_context(image_tag):
    current = image_tag
    while current:
        if current.name == "div" and "dyncontent" in current.get("class", []):
            dynheader = current.find_previous_sibling("div", class_="dynheader")
            if dynheader:
                return dynheader.get_text(strip=True)
        current = current.parent
    return ""

def clean_html(html_content, images_folder, output_folder):
    soup = BeautifulSoup(html_content, 'lxml')
    text_content = soup.get_text()
    metadata = extract_metadata(soup, text_content)
    sections = extract_sections(soup)
    links = extract_links(soup)
    code_blocks = extract_code(soup)
    
    image_data = []
    for img in soup.find_all('img'):
        img_src = img.get('src')
        if img_src:
            original_img_path = os.path.join(images_folder, os.path.basename(img_src))
            new_img_path = os.path.join(output_folder, os.path.basename(img_src))
            if os.path.exists(original_img_path):
                shutil.copy(original_img_path, new_img_path)
                context = find_image_context(img)
                image_data.append({"src": new_img_path, "context": context})
    
    for script in soup(["script", "style"]):
        script.extract()
    
    contents_div = soup.find('div', class_='contents')
    if contents_div:
        for tag in contents_div.find_all(True):
            tag.unwrap()
        content_text = contents_div.get_text(separator="\n", strip=True)
    else:
        content_text = ""

    mathjax_scripts = [str(script) for script in soup.find_all('script') if 'MathJax' in str(script)]
    
    return {
        "metadata": metadata,
        "sections": sections,
        "links": links,
        "code_blocks": code_blocks,
        "images": image_data,
        "content": content_text,
        "mathjax_scripts": mathjax_scripts
    }

def save_json(data, save_folder, filename):
    json_file = os.path.join(save_folder, f"{filename}.json")

    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

def process_directory(base_input_dir, base_output_dir, skipped_files, current_dir=""):
    input_dir = os.path.join(base_input_dir, current_dir)
    output_dir = os.path.join(base_output_dir, current_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for item in os.listdir(input_dir):
        input_path = os.path.join(input_dir, item)
        output_path = os.path.join(output_dir, item)

        if os.path.isdir(input_path):
            process_directory(base_input_dir, base_output_dir, skipped_files, os.path.join(current_dir, item))
        elif item.endswith('.html'):
            if os.path.getsize(input_path) > 15 * 1024 * 1024:  # Skip files larger than 15MB
                logging.warning(f"Skipping large file: {input_path}")
                print(f"Skipped file: {input_path}")
                skipped_files.append(input_path)
                continue
            try:
                with open(input_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                data = clean_html(html_content, input_dir, output_dir)

                # Save the data as JSON
                save_json(data, output_dir, os.path.splitext(item)[0])

                logging.info(f"Processed {input_path}")

            except Exception as e:
                logging.error(f"Error processing {input_path}: {e}")
                print(f"Error processing {input_path}: {e}")

# Example usage
base_input_dir = '/home/bit/00_scrape_docs_py_2_markdown/downloaded_html/docs.opencv.org/4.10.0'
base_output_dir = '/home/bit/clean_html'
skipped_files = []

process_directory(base_input_dir, base_output_dir, skipped_files)

# Print skipped files for further handling
print("Skipped files:")
for skipped_file in skipped_files:
    print(skipped_file)
