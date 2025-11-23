import requests
import streamlit as st
from bs4 import BeautifulSoup
import re
from gpt_data import get
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import base64

with open("background.png", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <style>
    [data-testid=stAppViewContainer] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

lst = []
def scrape_with_scrapingbee(url):
    """Use ScrapingBee API for reliable scraping"""
    try:
        # Get API key from Streamlit secrets
        api_key = ""
        
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': api_key,
                'url': url,
                'render_js': 'false',  # Amazon doesn't need JS rendering for basic info
                'premium_proxy': 'true',  # Use premium proxies for better success rate
                'country_code': 'us',  # Use US proxies for Amazon
                'block_ads': 'true',  # Block ads for faster loading
                'block_resources': 'true'  # Block images/CSS for faster loading
            },
            timeout=70  # ScrapingBee can take longer
        )
        
        if response.status_code == 200:
            return response.text
        else:
            api_key1 = ""
        
            response1 = requests.get(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': api_key1,
                'url': url,
                'render_js': 'false',  # Amazon doesn't need JS rendering for basic info
                'premium_proxy': 'true',  # Use premium proxies for better success rate
                'country_code': 'us',  # Use US proxies for Amazon
                'block_ads': 'true',  # Block ads for faster loading
                'block_resources': 'true'  # Block images/CSS for faster loading
            },
            timeout=60  # ScrapingBee can take longer
        )
            if response1.status_code == 200:
                return response1.text
            else:
                text="Unable to fetch the data from the API"
                return text
                
            
            
    except Exception as e:
        st.error(f"ScrapingBee error: {str(e)}")
        return None

def get_data(url):
    """Modified get_data function using ScrapingBee instead of urllib"""
    global lst
    
    try:
        # Use ScrapingBee instead of urllib
        html_content = scrape_with_scrapingbee(url)
        
        if html_content is None:
            return {}, "Error", "0.0 out of 5"
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Clear and reopen the specify.txt file for this product
        sp = open("specify.txt", "w", encoding="utf-8")  # Changed from "a" to "w" to overwrite
        
        # Extract title
        title = soup.find(id='productTitle')
        title1 = ["Unknown Product"]  # Default value
        
        if title:
            title_text = title.get_text(strip=True)
            ptrn = r"([a-zA-Z0-9 ]*) \("
            title1_matches = re.findall(ptrn, title_text)
            if title1_matches:
                title1 = title1_matches
            else:
                # If pattern doesn't match, use the full title
                title1 = [title_text[:50]]  # Limit to 50 chars
            
            lst.append(title1)
            sp.write(f"Product: {title_text}\n\n")
        
        # Extract description from feature bullets
        description = soup.find('div', {'id': 'feature-bullets'})
        if description:
            description_text = description.get_text(strip=True)
            sp.write(f"Description: {description_text}\n\n")
        
        # Extract technical specifications
        details = {}
        tech_details_section = soup.find(id='productDetails_techSpec_section_1')
        if tech_details_section:
            rows = tech_details_section.find_all('tr')
            sp.write("Technical Specifications:\n")
            for row in rows:
                th_element = row.find('th')
                td_element = row.find('td')
                if th_element and td_element:
                    th = th_element.get_text(strip=True)
                    td = td_element.get_text(strip=True)
                    details[th] = td
                    sp.write(f'{th}: {td}\n')
            sp.write("\n")
        
        # Try alternative tech details section
        tech_details_div = soup.find('div', class_='content-grid-alternate-styles', id='tech')
        if tech_details_div:
            text = tech_details_div.text
            combined_string = ' '.join(text.split())
            sp.write("Additional Specifications:\n")
            sp.write(combined_string + "\n\n")
        
        # Try additional details table
        additional_details = soup.find('table', {'id': 'productDetails_detailBullets_sections1'})
        if additional_details:
            rows = additional_details.find_all('tr')
            sp.write("Additional Details:\n")
            for row in rows:
                th_element = row.find('th')
                td_element = row.find('td')
                if th_element and td_element:
                    th = th_element.get_text(strip=True)
                    td = td_element.get_text(strip=True)
                    if th and td:
                        sp.write(f'{th}: {td}\n')
            sp.write("\n")
        
        # Extract rating
        rating = "0.0 out of 5"  # Default value
        rating_element = soup.find('span', {'class': 'a-icon-alt'})
        if rating_element:
            rating = rating_element.get_text(strip=True)
            sp.write(f"Rating: {rating}\n")
        else:
            # Try alternative rating selector
            rating_alt = soup.find('span', {'data-hook': 'rating-out-of-text'})
            if rating_alt:
                rating = rating_alt.get_text(strip=True)
                sp.write(f"Rating: {rating}\n")
        
        sp.close()
        return details, title1[0] if title1 else "Unknown Product", rating
   

        
    except Exception as e:
        st.error(f"Error in get_data: {str(e)}")
        return {}, "Error", "0.0 out of 5"

def d_prompt(data):
    """Your existing d_prompt function - no changes needed"""
    prompt = '''I have a list of product descriptions and specifications for several products. I want to extract and compare the key features from each product and create a single dictionary that contains the best specifications. The output should be in the format of a Python dictionary, such as {"os": "android 13"}.
    Here are the descriptions and specifications for each product:'''
    
    for i in range(len(data)):
        # Handle the case where lst might be empty or have different structure
        product_name = "Product"
        if i < len(lst) and lst[i]:
            if isinstance(lst[i], list) and lst[i]:
                product_name = lst[i][0]
            else:
                product_name = str(lst[i])
        
        prompt += f'\nproduct{i+1}->{product_name}:\nhere are the description and specifications:\n"""{data[i]}"""'
    
    prompt += """\nConsider the following criteria for determining the "best" specifications:
- Latest technology or version (e.g., the newest operating system)
- Highest performance metrics (e.g., CPU speed, RAM)
- Largest capacity (e.g., storage space, battery life)
- Most features or advanced options (e.g., camera quality, display resolution)
extract only from the given data.
Please provide a single dictionary that consists the 10 best specifications from all the products, prioritizing the most important features as described above.give overal best specifications.just gimme what i ask , dont explain anything and avoid giving programming scrips.in the output give me only dictionary."""
    
    try:
        my_text = get(prompt)
        
        # Combine texts for vectorization
        all_texts = data + [my_text]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
        
        similarity_list = []
        # Display similarity percentages
        for idx, similarity in enumerate(similarities[0]):
            similarity_list.append(similarity * 100)
        
        return my_text, all_texts, similarity_list
        
    except Exception as e:
        st.error(f"Error in d_prompt: {str(e)}")
        return "Error processing data", data, [0] * len(data)

# Additional helper function to check API status
def check_scrapingbee_status():
    """Check ScrapingBee API status and remaining credits"""
    try:
        import os
        api_key = ""
        response = requests.get(
            'https://app.scrapingbee.com/api/v1/usage',
            params={'api_key': api_key}
        )
        if response.status_code == 200:
            usage_data = response.json()
            return {
                'status': 'connected',
                'used_calls': usage_data.get('used_api_calls', 0),
                'max_calls': usage_data.get('max_api_calls', 1000)
            }
        else:
            return {'status': 'error', 'message': f"API Error: {response.status_code}"}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
