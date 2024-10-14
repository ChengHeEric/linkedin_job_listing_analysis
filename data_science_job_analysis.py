import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from collections import Counter
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# my key word is data analyst, location is McLean, filters include distance less than 16 kms, and experience levels is one of the list ['Entry Level', 'internship', 'associate']
url = "https://www.linkedin.com/jobs/search/?currentJobId=3976163471&distance=10&f_E=1%2C2%2C3&geoId=106504367&keywords=data%20analyst&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true"

# Set up your LinkedIn credentials
USERNAME = 'example.com'
PASSWORD = 'example password'

# Setup WebDriver 
driver = webdriver.Edge()

# Navigate to LinkedIn
driver.get('https://www.linkedin.com/login')

# Wait for the email input and fill it
email_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'username'))
)
email_input.send_keys(USERNAME)

# Wait for the password input and fill it
password_input = driver.find_element(By.ID, 'password')
password_input.send_keys(PASSWORD)

# Submit the login form
password_input.send_keys(Keys.RETURN)

# Wait until the login process is complete (check for some element on the homepage)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'global-nav__me'))
)

# Log into LinkedIn manually or use Selenium to automate it.
driver.get(url)


#there are 25 job listings on each page, i need to make a list of pages that contains all the job listings

#add the first page to the list
urls = [url]

#find out the number of job listings 
number_of_results = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.jobs-search-results-list__subtitle'))
).text.strip().split()[0]

#divde the number of job listings by 25 and then we have the number of pages
number_of_pages = int(number_of_results) // 25 + 1

#add the urls to the list
for i in range(1, number_of_pages):
    link = url + "&start=" + str(i*25)
    urls.append(link)

print('total number of pages: ', number_of_pages)

#create a empty list to store the job links
jobs = []

counter = 1

print('total number of pages: ', len(urls))
print('estimated time: ' + str(len(urls)*2.5) + ' seconds')

#go through each page and scrape the job links
for i in urls:
    
    driver.get(i)
    
    # Wait for the job listings to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.scaffold-layout__list-container'))
    )
    
    # Scrape job listings
    job_lists = driver.find_element(By.CSS_SELECTOR, 'ul.scaffold-layout__list-container').find_elements(By.CSS_SELECTOR, 'li.jobs-search-results__list-item')
        
    # Extract job information
    for job in job_lists:
        try:
            link = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            jobs.append(link)
        except:
            pass
    
    print(f'Finished scraping page {counter}')
    counter += 1
    
print(f'total number of jobs scraped: {len(jobs)}')



#create a list to store the job description
job_descriptions = []

for i in range(len(jobs)):
    
    print(f'Finished scraping job {i}')
    
    try:
        driver.get(jobs[i])

        time.sleep(2)

        # Wait for the job description to load and expand the content
        expand = driver.find_element(By.CSS_SELECTOR, 'button.jobs-description__footer-button').click()

        # select the content from the job description
        content = driver.find_element(By.CSS_SELECTOR, 'article.jobs-description__container').find_elements(By.CSS_SELECTOR, 'span,li,strong')

        full_content = []
        
        # add the content to the list
        for i in content:
            full_content.append(i.text)
            
        #combine the content
        full_content = ' '.join(full_content)
        
        # add the content to the list
        job_descriptions.append(full_content)
    except:
        print("error")
    #print the progress




nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')  # POS tagging model

full_job_description = ' '.join(job_descriptions)

# Function to preprocess text (lowercase, remove punctuation)
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    
    # Tokenize using nltk
    words = word_tokenize(text)
    
    return words

# Function to remove stopwords
def remove_stopwords(words):
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word not in stop_words]
    
    return filtered_words

# Function to remove verbs using POS tagging
def remove_verbs(words):
    # POS tagging
    tagged_words = pos_tag(words)
    
    # Keep only words that are not verbs (excluding 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ')
    non_verbs = [word for word, tag in tagged_words if not tag.startswith('VB')]
    
    return non_verbs

# Function to calculate word frequency without verbs
def word_frequency(text):
    # Preprocess and tokenize the text
    words = preprocess_text(text)
    
    # Remove stopwords
    words_filtered = remove_stopwords(words)
    
    # Remove verbs
    words_no_verbs = remove_verbs(words_filtered)
    
    # Count word frequencies
    word_counts = Counter(words_no_verbs)
    
    return word_counts

# Function to generate a word cloud
def generate_word_cloud(text):
    # Preprocess and tokenize the text
    words = preprocess_text(text)
    
    # Remove stopwords
    words_filtered = remove_stopwords(words)
    
    # Remove verbs
    words_no_verbs = remove_verbs(words_filtered)
    
    # Join the words back into a single string for the word cloud
    clean_text = ' '.join(words_no_verbs)
    
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(clean_text)
    
    # Display the word cloud using matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # No axis for word cloud visualization
    plt.show()

# Get word frequency after removing verbs
word_freq = word_frequency(full_job_description)

# Display the top N most common words
top_n = 20
print(word_freq.most_common(top_n))

generate_word_cloud(full_job_description)

