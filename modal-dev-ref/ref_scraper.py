import os
import requests
from bs4 import BeautifulSoup
import html2text

# GitHub API URL for modal-labs repositories
github_api_url = "https://api.github.com/orgs/modal-labs/repos"

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Scrape modal docs
def scrape_modal_docs():
    doc_urls = [
        'https://modal.com/docs/examples',
        'https://modal.com/docs/guide',
        'https://modal.com/docs/reference'
    ]

    docs_dir = os.path.join(script_dir, 'docs')

    if not os.path.exists(docs_dir):
        os.mkdir(docs_dir)

    for doc_url in doc_urls:
        doc_category = doc_url.split('/')[-1]
        category_dir = os.path.join(docs_dir, doc_category)
        
        if not os.path.exists(category_dir):
            os.mkdir(category_dir)
        
        page = requests.get(doc_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        sidebar = soup.find('div', class_='sidebar')
        if sidebar:
            side_bar_links = [link.get('href') for link in sidebar.find_all('a') if link.get('href')]
            side_bar_links = list(set(side_bar_links))
            
            for link in side_bar_links:
                full_url = f"https://modal.com{link}"
                
                sub_page = requests.get(full_url)
                sub_soup = BeautifulSoup(sub_page.content, 'html.parser')
                
                article = sub_soup.find('article')
                
                if article:
                    converter = html2text.HTML2Text()
                    converter.ignore_links = True
                    markdown_content = converter.handle(str(article))
                    
                    file_name = link.split('/')[-1] + '.md'
                    file_path = os.path.join(category_dir, file_name)
                    
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(markdown_content)
                
                    print(f"Saved: {file_name}")
                else:
                    print(f"No article found for: {full_url}")
        else:
            print("No sidebar found.")

scrape_modal_docs()  # Scrape documentation
