# Yad2 Apartment Scraper

## Overview
The Yad2 Apartment Scraper is a Python-based application designed to automate the process of scraping apartment listings from the Yad2 real estate website. This tool is particularly useful for individuals or businesses looking to gather real estate data efficiently. The application not only scrapes listings but also enriches them with additional details and sends notifications via email. It leverages Selenium for web scraping and the Gmail API for email notifications.

## Features
- **Web Scraping**: Utilizes Selenium to navigate the Yad2 website and extract relevant data from apartment listings
- **Data Enrichment**: Enhances the scraped data with additional information such as floor details, features, and contact information
- **Email Notifications**: Automatically sends email alerts for listings that meet certain criteria using the Gmail API
- **Street Validation**: Ensures that the listings are located on supported streets by validating against a predefined list

## Prerequisites
To run the Yad2 Apartment Scraper, you will need:
- Python 3.7 or higher
- Google Chrome and ChromeDriver installed on your machine
- A Google Cloud project with the Gmail API enabled
- Environment variables set up for Yad2 login credentials and email recipients

## Setup Instructions
1. **Clone the Repository**: Start by cloning the repository to your local machine and navigating into the project directory
2. **Install Dependencies**: The project uses pip-tools for managing dependencies. You can install the required packages using the requirements.txt file
3. **Environment Configuration**: Create a .env file in the root directory of the project. This file should contain the necessary environment variables for Yad2 login credentials and email recipients
4. **Gmail API Setup**: Set up the Gmail API by creating a project in the Google Cloud Console. Enable the Gmail API and download the client_secret.json file. Place this file in the src/email directory
5. **Initialize Gmail Credentials**: Run the init_credentials.py script located in the src/mail_sender directory to initialize Gmail API credentials
6. **Run the Application**: Execute the main.py script to start the scraper. This will begin the process of scraping, enriching, and sending notifications for apartment listings

## Usage
Once the application is running, it will automatically scrape listings from the Yad2 website, enrich them with additional details, and send email notifications for listings that meet the specified criteria. This process is designed to be seamless and requires minimal user intervention once set up.

## Development

### Project Structure
The project is organized into several key directories:
- **src**: Contains the main application code, including subdirectories for:
  - Address matching
  - CLI components
  - Email sending
  - Utility functions
  - Core Yad2 scraping logic
- **tests**: Includes test cases for various components of the application
- **.vscode**: Contains configuration files for Visual Studio Code
- **Makefile**: Automates common development tasks
- **requirements.txt**: Lists all project dependencies

### Testing
The project includes a comprehensive test suite using pytest. To run the tests, simply execute: