from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Set up ChromeDriver path and initialize the WebDriver
service = Service('./chromedriver.exe')  # Ensure this path points to your chromedriver
driver = webdriver.Chrome(service=service)

# Handle Google cookie consent pop-up
def handle_cookie_consent():
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept all")]'))
        ).click()
        print("Accepted cookies.")
    except TimeoutException:
        print("Cookie consent not found or already handled.")

# Search Google and scrape results
def google_search(query):
    driver.get('https://www.google.com')
    handle_cookie_consent()

    # Perform search
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'q'))
        )
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
    except TimeoutException:
        print("Error: Unable to find search box.")
        return []

    # Wait for search results to load
    time.sleep(3)

    # Scrape results
    results = []
    try:
        search_results = driver.find_elements(By.XPATH, '//div[@class="g"]')[:10]  # Limit to top 10 results
        for result in search_results:
            try:
                title = result.find_element(By.XPATH, './/h3').text
                url = result.find_element(By.XPATH, './/a').get_attribute('href')
                try:
                    # Optimized XPath for snippet extraction
                    snippet = result.find_element(By.XPATH, './/div[@class="VwiC3b"]').text
                except NoSuchElementException:
                    snippet = "Snippet not available"
                results.append({'title': title, 'url': url, 'snippet': snippet})
            except Exception as e:
                print(f"Error extracting result: {e}")
                continue
    except Exception as e:
        print(f"Error fetching search results: {e}")
    return results

# Function to generate HTML output from the results
def generate_html(data, filename="google_results.html"):
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Google Search Results</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container my-4">
            <h1 class="text-center">Google Search Results</h1>
            <table class="table table-striped table-bordered">
                <thead class="thead-dark">
                    <tr>
                        <th scope="col">Title</th>
                        <th scope="col">Snippet</th>
                        <th scope="col">URL</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    '''

    rows = ""
    for entry in data:
        row = f'''
        <tr>
            <td>{entry['title']}</td>
            <td>{entry['snippet']}</td>
            <td><a href="{entry['url']}" target="_blank">View Post</a></td>
        </tr>
        '''
        rows += row

    # Write the HTML content to a file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content.format(rows=rows))
    print(f"Data exported to {filename}")

# Main function to perform search and generate the HTML document
def main():
    keywords = [
        "Affordable website design",
        "SEO services for small businesses",
        "Custom web design packages"
    ]

    all_results = []
    
    for keyword in keywords:
        print(f"Searching for: {keyword}")
        results = google_search(keyword)
        if results:
            all_results.extend(results)

    # Generate the HTML document with the collected data
    generate_html(all_results)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
