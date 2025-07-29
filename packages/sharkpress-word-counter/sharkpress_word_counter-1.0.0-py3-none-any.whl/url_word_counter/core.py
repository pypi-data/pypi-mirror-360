from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time

class URLWordCounter:
    """A class to count words in the main content of web pages."""
    
    def __init__(self, headless=True):
        """Initialize the URLWordCounter.
        
        Args:
            headless (bool): Whether to run the browser in headless mode.
        """
        self.driver = self._setup_driver(headless)
        
    def _setup_driver(self, headless):
        """Set up and return a Chrome WebDriver.
        
        Args:
            headless (bool): Whether to run in headless mode.
            
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance.
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Chrome WebDriver: {e}")
    
    def get_word_count(self, url):
        """Get the word count of the main content of a webpage.
        
        Args:
            url (str): The URL of the webpage to analyze.
            
        Returns:
            tuple: A tuple containing (word_count, content_preview, error)
                  word_count (int): Number of words in the main content.
                  content_preview (str): Preview of the extracted content.
                  error (str): Error message if any, otherwise None.
        """
        try:
            content = self._get_main_content(url)
            if not content:
                return 0, "", "No content could be extracted from the page"
                
            word_count = self._count_words(content)
            preview = content[:200] + ('...' if len(content) > 200 else '')
            return word_count, preview, None
            
        except Exception as e:
            return 0, "", f"Error processing {url}: {str(e)}"
    
    def _get_main_content(self, url):
        """Fetch and extract the main content from a URL.
        
        Args:
            url (str): The URL to fetch content from.
            
        Returns:
            str: The extracted main content.
        """
        try:
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # Give some time for JavaScript to execute
            time.sleep(2)
            
            # Get the page source after JavaScript execution
            page_source = self.driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "iframe"]):
                element.decompose()
                
            # Try to find the main content area
            main_content = None
            
            # Try different selectors to find the main content
            selectors = [
                'main',
                'article',
                '.main-content',
                '#main',
                '#content',
                '.content',
                'body'
            ]
            
            for selector in selectors:
                if selector.startswith(('.', '#')):
                    main_content = soup.select_one(selector)
                else:
                    main_content = soup.find(selector)
                if main_content:
                    break
            
            # If we found some content, get the text
            if main_content:
                # Get text and clean it up
                text = main_content.get_text(separator=' ', strip=True)
                # Remove extra whitespace and newlines
                text = re.sub(r'\s+', ' ', text)
                return text
                
            return ""
            
        except Exception as e:
            raise Exception(f"Error fetching content: {str(e)}")
    
    def _count_words(self, text):
        """Count the number of words in the given text.
        
        Args:
            text (str): The text to count words in.
            
        Returns:
            int: The number of words.
        """
        if not text:
            return 0
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def close(self):
        """Close the WebDriver."""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """Run the URL Word Counter as a command-line application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Count words in the main content of a webpage.')
    parser.add_argument('url', nargs='?', help='URL to analyze (optional, can be entered interactively)')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in non-headless mode')
    args = parser.parse_args()
    
    print("\n🛠️  Advanced URL Word Counter (with JavaScript support)")
    print("=" * 60)
    
    counter = None
    try:
        print("\n🚀 Initializing browser...")
        counter = URLWordCounter(headless=not args.no_headless)
        
        while True:
            url = args.url
            if not url:
                print("\n" + "-" * 60)
                url = input("\n🌐 Enter URL (or 'q' to quit): ").strip()
            
            if url.lower() == 'q':
                break
                
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            print(f"\n🔍 Analyzing {url}...")
            
            word_count, preview, error = counter.get_word_count(url)
            
            if error:
                print(f"\n❌ {error}")
            else:
                print(f"\n📊 Word count (main content only): {word_count:,}")
                if preview:
                    print(f"\n📝 Content preview: {preview}")
            
            # Clear the URL after first use if it was provided as an argument
            if args.url:
                args.url = None
                
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        if counter:
            counter.close()
            print("\n✨ Browser closed. Goodbye!")


if __name__ == "__main__":
    main()
