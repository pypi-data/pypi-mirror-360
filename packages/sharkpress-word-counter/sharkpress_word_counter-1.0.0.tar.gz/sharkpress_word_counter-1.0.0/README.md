# URL Word Counter

A Python tool that counts words in the main content of web pages, ignoring cookie banners, headers, and footers. It uses Selenium with a headless Chrome browser to properly render JavaScript-heavy websites.

## Features

- Extracts main content from web pages
- Ignores cookie banners, headers, and footers
- Handles JavaScript-rendered content
- Provides word count and content preview
- Simple command-line interface

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Chrome (required for Selenium)

### Option 1: Install from source

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd url-word-counter
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Option 2: Install directly from GitHub

```bash
pip install git+https://github.com/yourusername/url-word-counter.git
```

### Option 3: Install with pip

```bash
pip install url-word-counter
```

## Usage

### Command Line Interface

After installation, you can run the URL Word Counter from the command line:

```bash
url-word-counter [URL] [--no-headless]
```

- `URL`: (Optional) The URL to analyze. If not provided, you'll be prompted to enter one.
- `--no-headless`: (Optional) Run the browser in non-headless mode (visible browser window).

Example:
```bash
url-word-counter https://www.example.com/
```

### Python API

You can also use the URL Word Counter in your Python code:

```python
from url_word_counter import URLWordCounter

# Initialize the counter
counter = URLWordCounter()

# Get word count for a URL
word_count, preview, error = counter.get_word_count("https://www.example.com/")

if error:
    print(f"Error: {error}")
else:
    print(f"Word count: {word_count:,}")
    print(f"Preview: {preview}")

# Don't forget to close the browser when done
counter.close()
```

## Example

```
🛠️  Advanced URL Word Counter (with JavaScript support)
============================================================

🚀 Initializing browser...

🌐 Enter URL (or 'q' to quit): https://www.example.com/

🔍 Analyzing https://www.example.com/...

📊 Word count (main content only): 1,234

📝 Content preview: This is a preview of the extracted content from the webpage...
```

## How It Works

The script uses:
- Selenium WebDriver with Chrome in headless mode
- BeautifulSoup for HTML parsing
- Smart content extraction that focuses on the main content area
- Word counting that ignores HTML tags and scripts

## Requirements

- Python 3.8+
- Google Chrome
- ChromeDriver (automatically installed by webdriver-manager)

## License

MIT

---

# Lovable Project

## Project info

**URL**: https://lovable.dev/projects/87abc578-1123-4e3e-8c3e-44d646a171db

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/87abc578-1123-4e3e-8c3e-44d646a171db) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/87abc578-1123-4e3e-8c3e-44d646a171db) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)
