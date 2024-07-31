# UserAgentFilter-NetAPorter-Scraper
The NetAPorter-Scraper is a Python-based tool designed to scrape product details from the NET-A-PORTER website. It fetches product information such as name,color,designer,category etc from the already fetched urls URLs. The data is saved into a CSV file for further analysis or usage.the main part is UserAgentFilter library is used before fetching to filter user agents for this website.
## Features:
- **User Agent Filtering**: Filters user agents to ensure that only those that can access the website are used.
- **Product Data Scraping**: Scrapes product details from the already extracted product URLs.
- **Asynchronous Execution**:Utilizes the asyncio library to manage asynchronous operations, though in the provided code, asyncio is not fully leveraged. The script's main function is defined as async, but there are no asynchronous I/O operations in the code. To fully utilize asyncio, you would need to incorporate asynchronous libraries or operations.
- **User-Agent Rotation**:Reads user agents from a user_agents.txt file and selects a random user agent for each request to avoid detection and blocking by the website.
- **Proxy Configuration**:Includes a proxy configuration to route requests through a proxy server, which helps to avoid IP bans and control the scraping rate.
- **Request Handling**:Uses the requests library to fetch HTML content from URLs, with support for setting cookies and headers to mimic a real browser.
- **Error Handling and Retrying**:Implements retry logic for failed requests, with a maximum of 3 attempts per URL. If all attempts fail, the error is logged, and the URL is saved in an error_urls table in the database.
- **Delay Between Requests**:Introduces a random delay between requests (20 to 40 seconds) to reduce the likelihood of being detected as a bot.
- **HTML Parsing**:Parses HTML content using BeautifulSoup to extract product details such as name, stock type, brand, price, discount, sale price, color, description, size and fit, details and care, and product code.
- **Database Interaction**:Creates and interacts with an SQLite database to store scraped data. It creates two tables: product_data for storing product details and error_urls for logging errors.
- **Checkpointing**:Maintains a checkpoint file (checkpoint.txt) to keep track of the last successfully processed URL. This allows the script to resume from where it left off in case of an interruption.
- **Logging**:Configures logging to provide information on the status of the scraping process and errors encountered.
- **Cookie Management**:Sets cookies for requests to maintain session state and handle websites that require authentication or session management.
- **File Handling**:Reads URLs and categories from a CSV file (netaporter_urls.csv) and stores the checkpoint index in a text file to resume scraping later if needed.

## Prerequisites
To run this project, you need the following:

Python 3.6 or higher
Required Python libraries - requests, beautifulsoup4 ,urllib3,UserAgentFilter

## Project Structure

- `user_agent_filtering.py` :Filters user agents that can successfully access a specific website.
- `netaporter_data.py`:Scrapes product details from each product URL which is already extracted and saves the data to database
