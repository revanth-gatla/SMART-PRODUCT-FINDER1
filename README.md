# Smart Product Finder (Product OptiChoice)



## Project Description

Smart Product Finder is a Python-based web application built using **Streamlit** that helps users compare multiple Amazon products and identify the best option based on specifications and customer ratings.
Users can paste multiple Amazon product URLs into the application. The system scrapes product details such as title, description, technical specifications, and ratings using the **ScrapingBee API** and **BeautifulSoup**.  
It then analyzes and compares products using NLP techniques and ranks them based on similarity and ratings.
The application also uses a **Large Language Model (LLM)** to extract the best overall specifications across all compared products.
This project demonstrates real-world usage of **web scraping, data processing, NLP, and interactive web application development** using Python.

---

## Live Demo

🔗 **End-User Application Link**  
https://comparision-guru.streamlit.app/

*(Users can directly access and use the application through this link without setting up the project locally.)
---

## Features

- Compare multiple Amazon products using product URLs  
- Scrape product title, description, specifications, and ratings  
- Rank products based on specification similarity  
- Rank products based on customer ratings  
- Extract best overall specifications using a Large Language Model  
- Interactive Streamlit-based web interface  
- Data visualization using charts  
---
## Technologies Used

- Python  
- Streamlit  
- Requests  
- BeautifulSoup  
- ScrapingBee API  
- Scikit-learn (TF-IDF and cosine similarity)  
- Transformers  
- Groq LLM API  
- Pandas and NumPy  
- Plotly  
---
## Project Structure
SMART-PRODUCT-FINDER1/
├── find_product.py
├── product_app.py
├── gpt_data.py
├── pycode/
│ └── background.png
├── requirements.txt
├── README.md
└── .gitignore


---

## How to Run the Project (Local Setup)

### Step 1: Clone the repository

```bash
git clone https://github.com/revanth-gatla/SMART-PRODUCT-FINDER1.
cd SMART-PRODUCT-FINDER1
pip install -r requirements.txt
--configure API keys--
[keys]
scrappingbee = "YOUR_SCRAPINGBEE_API_KEY"
groqapi = "YOUR_GROQ_API_KEY"
----run the application----
streamlit run product_app.py
----------------
Usage:
->Open the live application link or run the project locally
->Paste multiple Amazon product URLs in the sidebar
->Click Compare
->View:
->Product ranking by specifications
->Product ranking by ratings
->Best overall specifications
->Visual comparison charts

## Author
**Revanth Gatla**  
B.Tech Computer Science Engineering


