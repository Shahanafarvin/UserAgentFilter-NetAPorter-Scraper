"""
This script demonstrates how to use the UserAgentFilter package to test and filter user agents
against a specific website. The UserAgentTester class provides functionality to test user agents 
by sending HTTP requests and checking their acceptance based on the HTTP status code.
"""
from UserAgentFilter import UserAgentTester

# Define the target URL 
test_url = 'https://www.net-a-porter.com/en-in/'


# Create an instance of UserAgentTester
tester = UserAgentTester(
    test_url=test_url,
    proxy= {
  "https": "scraperapi.retry_404=true.country_code=us.device_type=desktop.session_number=125.keep_headers=true:458fa92f5567092c5d9d9f6e863ed38d@proxy-server.scraperapi.com:8001"
},
    
    delay_range=(20,30),
    timeout=20
    
)

"""
    UserAgentTester:A class to test user agents against a specified URL with optional proxy support.

    Default Parameters for HTTP Requests:
    -------------------------------------
    1.**test_url**
        -the website url to test
    
    2. **Timeout:**
       - `timeout`: 10 seconds by default- Max time to wait for a server response.
       - **Note**: You can increase the timeout if the website is slow to respond.

    3. **Proxy:**
       - `proxy`: None by default - Routes requests through a proxy if specified.
       - **Note**: You can add a proxy if the website shows a 403 error.

    4. **Retries and Delays:**
       - `max_retries`: 3 - Retries for transient errors like timeouts.
       - `delay_range`: (3, 8) - Random delay between requests to mimic human behavior.
       - **Note**: Increase the delay range if the website is detecting bots with small request intervals.
    """

# Filter user agents from the input file and save the successful ones to the output file
tester.filter_user_agents(
    user_agents_file='user_agents.txt',
    output_file='filtered_user_agents.txt'
)
print("User agents have been filtered and saved to 'filtered_user_agents.txt'")

"""
    Filter user agents by testing them against a specific website and save successful ones to a file.

    This method reads a list of user agents from an input file, tests each user agent by sending a request to 
    the specified `test_url`, and writes the successful user agents (those that receive an HTTP status code 200) 
    to an output file.

    Args:
        user_agents_file (str): Path to the input file containing user agents, with one user agent per line.
        output_file (str): Path to the output file where successful user agents will be saved.

    Returns:
        List[str]: A list of successful user agents that were able to access the website.

    Method Details:
    ---------------
    1. **File Reading:**
       - Reads user agents from the specified `user_agents_file`.
       - Each user agent is tested individually.

    2. **Testing User Agents:**
       - Sends HTTP requests to the `test_url` with each user agent.
       - Uses specified proxies and headers to handle requests.

    3. **Error Handling:**
       - Retries on transient errors like timeouts and server errors.
       - Logs errors and skips user agents that cause repeated failures.

    4. **Writing Output:**
       - Writes successful user agents to the specified `output_file`.
       - Includes each user agent only once.

    """