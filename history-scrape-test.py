import requests
from bs4 import BeautifulSoup

# Global Keyword Config
KEYWORDS = {
    'physicist': 5, 'academic': 8, 'composer': 7, 'politician': 4,
    'pianist': 11, 'author': 7, 'poet': 4, 'emperor': 7, 'empress': 7,
    'king': 7, 'queen': 7, 'prince': 7, 'princess': 7, 'actor': 4,
    'actress': 4, 'nobel': 6, 'president': 9, 'independence': 10,
    'revolution': 8, 'diplomacy': 4, 'treaty': 7, 'world war': 8,
    'scientist': 6, 'general': 5, 'pope': 7
}

def get_section_content(soup, section_id):
    """Extracts all list items under a specific section heading."""
    results = []
    header = soup.find(id=section_id)
    if not header:
        return []

    # Move to the parent container (usually an h2) then iterate through siblings
    current = header.parent
    while True:
        current = current.find_next_sibling()
        if not current or current.name in ['h2', 'h1']:
            break
        if current.name == 'ul':
            results.extend(current.find_all('li'))
    return results

def score_and_sort(items, weight_dict, threshold=1):
    """Calculates relevance score and sorts items."""
    scored_list = []
    for item in items:
        text = item.get_text()
        text_lower = text.lower()
        
        score = sum(weight for kw, weight in weight_dict.items() if kw.lower() in text_lower)
        
        if score >= threshold:
            scored_list.append((score, text))
            
    return sorted(scored_list, key=lambda x: x[0], reverse=True)

def scrape_wikipedia_today(month, day):
    """Fetches and parses the Wikipedia page for a specific date."""
    url = f"https://en.wikipedia.org/wiki/{month}_{day}"
    # Adding a User-Agent is polite and prevents blocks
    headers = {'User-Agent': 'HistoryScraperBot/1.0 (contact@example.com)'}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return [], [], []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Scrape each section using the optimized traversal logic
    events = score_and_sort(get_section_content(soup, "Events"), KEYWORDS, threshold=4)
    births = score_and_sort(get_section_content(soup, "Births"), KEYWORDS, threshold=6)
    deaths = score_and_sort(get_section_content(soup, "Deaths"), KEYWORDS, threshold=5)

    return events, births, deaths

def create_history_content(events, births, deaths, month, day):
    """Formats the collected data into a clean Markdown string."""
    sections = {"Events": events, "Births": births, "Deaths": deaths}
    markdown_content = f"# Today In History: {month} {day}\n\n"

    for title, data in sections.items():
        markdown_content += f"## {title}\n"
        if not data:
            markdown_content += "*No entries met the relevance threshold.*\n"
        for score, text in data:
            markdown_content += f"- **[{score}]** {text}\n"
        markdown_content += "\n"
            
    return markdown_content

if __name__ == "__main__":
    # 1. Configuration for the test
    TEST_MONTH = "December"
    TEST_DAY = "24"
    OUTPUT_FILE = "history_report.txt"

    print(f"--- Starting Scraper for {TEST_MONTH} {TEST_DAY} ---")

    # 2. Run the scraper
    ev, bi, de = scrape_wikipedia_today(TEST_MONTH, TEST_DAY)

    # 3. Generate the content
    report_text = create_history_content(ev, bi, de, TEST_MONTH, TEST_DAY)

    # 4. Write to text file
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Success! Report generated and saved to: {OUTPUT_FILE}")
        
        # Also print a small preview to the console
        print(f"Found {len(ev)} events, {len(bi)} births, and {len(de)} deaths.")
    except Exception as e:
        print(f"An error occurred while writing the file: {e}")