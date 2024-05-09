import os
import shutil
import requests
from bs4 import BeautifulSoup
import html2text
import subprocess

# GitHub API URL for modal-labs repositories
github_api_url = "https://api.github.com/orgs/modal-labs/repos"
github_clone_base_url = "https://github.com/modal-labs/"

# Authentication token for GitHub API (if required)
# It's best practice to use environment variables for such sensitive information.
# Make sure to replace 'your_github_token' with your actual GitHub token.
# github_token = os.getenv('GITHUB_TOKEN')  # Uncomment and set your token in your environment variables.
headers = {}
# if github_token:
#     headers = {"Authorization": f"token {github_token}"}

# Clone or update repositories from modal-labs
def clone_or_update_repos():
    response = requests.get(github_api_url)
    
    if response.status_code == 200:
        repos = response.json()
        for repo in repos:
            repo_name = repo['name']
            repo_dir = f"repos/{repo_name}"
            
            # Check if the repository directory already exists
            if os.path.exists(repo_dir):
                print(f"Updating {repo_name}...")
                subprocess.run(["git", "-C", repo_dir, "pull"])
            else:
                clone_url = repo['clone_url']
                print(f"Cloning {clone_url}...")
                subprocess.run(["git", "clone", clone_url, repo_dir])
    else:
        print("Failed to fetch repositories.")

# Scrape modal docs
def scrape_modal_docs():
    doc_urls = [
        'https://modal.com/docs/examples',
        'https://modal.com/docs/guide',
        'https://modal.com/docs/reference'
    ]

    if not os.path.exists('doc'):
        os.mkdir('doc')

    for doc_url in doc_urls:
        doc_category = doc_url.split('/')[-1]
        
        if not os.path.exists(f'doc/{doc_category}'):
            os.mkdir(f'doc/{doc_category}')
        
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
                    
                    with open(f'docs/{doc_category}/{file_name}', 'w', encoding='utf-8') as file:
                        file.write(markdown_content)
                
                    print(f"Saved: {file_name}")
                else:
                    print(f"No article found for: {full_url}")
        else:
            print("No sidebar found.")
            
# Ensure the cloned_repos directory exists
if not os.path.exists('repos'):
    os.mkdir('repos')

clone_or_update_repos()  # Clone all repositories
scrape_modal_docs()  # Scrape documentation
