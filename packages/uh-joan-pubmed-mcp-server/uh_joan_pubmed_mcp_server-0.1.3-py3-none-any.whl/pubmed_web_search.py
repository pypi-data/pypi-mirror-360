import xml.etree.ElementTree as ET
from urllib.parse import quote
import os
from collections import Counter
import re
import requests
import httpx
import logging
import sys
import asyncio

# Set up logging to stderr to avoid interfering with JSON-RPC
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def generate_pubmed_search_url(term=None, title=None, author=None, journal=None, 
                               start_date=None, end_date=None, num_results=10):
    """Generate PubMed search URL based on user input fields"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    query_parts = []
    
    if term:
        query_parts.append(quote(term))
    if title:
        query_parts.append(f"{quote(title)}[Title]")
    if author:
        query_parts.append(f"{quote(author)}[Author]")
    if journal:
        query_parts.append(f"{quote(journal)}[Journal]")
    if start_date and end_date:
        query_parts.append(f"{start_date}:{end_date}[Date - Publication]")
    
    query = " AND ".join(query_parts)
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": num_results,
        "retmode": "xml"
    }
    
    return f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

def search_pubmed(search_url):
    """Parse article IDs from PubMed search results"""
    response = requests.get(search_url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        id_list = root.find("IdList")
        if id_list is not None:
            return [id.text for id in id_list.findall("Id")]
        else:
            logger.warning("No results found.")
            return []
    else:
        logger.error(f"Error: Unable to fetch data (status code: {response.status_code})")
        return []

def get_pubmed_metadata(pmid):
    """Get detailed article metadata using PubMed API by PMID"""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    response = requests.get(url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        article = root.find(".//Article")
        if article is not None:
            title = article.find(".//ArticleTitle")
            title = title.text if title is not None else "No title available"
            
            abstract = article.find(".//Abstract/AbstractText")
            abstract = abstract.text if abstract is not None else "No abstract available"
            
            authors = []
            for author in article.findall(".//Author"):
                last_name = author.find(".//LastName")
                if last_name is not None and last_name.text:
                    authors.append(last_name.text)
            authors = ", ".join(authors) if authors else "No authors available"
            
            journal = article.find(".//Journal/Title")
            journal = journal.text if journal is not None else "No journal available"
            
            pub_date = article.find(".//PubDate/Year")
            pub_date = pub_date.text if pub_date is not None else "No publication date available"
            
            return {
                "PMID": pmid,
                "Title": title,
                "Authors": authors,
                "Journal": journal,
                "Publication Date": pub_date,
                "Abstract": abstract
            }
        else:
            logger.warning(f"No article data found for PMID: {pmid}")
            return None
    else:
        logger.error(f"Error: Unable to fetch metadata (status code: {response.status_code})")
        return None

def download_full_text_pdf(pmid):
    """Try to download full text PDF or provide article link"""
    logger.info(f"Attempting to access full text for PMID: {pmid}")
    
    # First, we need to check if this article has a PMC ID
    efetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(efetch_url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Error: Unable to fetch article data (status code: {response.status_code})")
        return f"Error: Unable to fetch article data (status code: {response.status_code})"
    
    root = ET.fromstring(response.content)
    pmc_id = root.find(".//ArticleId[@IdType='pmc']")
    
    if pmc_id is None:
        logger.warning(f"No PMC ID found for PMID: {pmid}")
        pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        logger.info(f"You can check the article availability at: {pubmed_url}")
        return f"No PMC ID found for PMID: {pmid}" + "\n" + f"You can check the article availability at: {pubmed_url}"
    
    pmc_id = pmc_id.text
    
    # Check if the article is open access
    pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
    pmc_response = requests.get(pmc_url, headers=headers)
    
    if pmc_response.status_code != 200:
        logger.error(f"Error: Unable to access PMC article page (status code: {pmc_response.status_code})")
        logger.info(f"You can check the article availability at: {pmc_url}")
        return f"Error: Unable to access PMC article page (status code: {pmc_response.status_code})" + "\n" + f"You can check the article availability at: {pmc_url}"
    
    if "This article is available under a" not in pmc_response.text:
        logger.warning(f"The article doesn't seem to be fully open access.")
        logger.info(f"You can check the article availability at: {pmc_url}")
        return f"The article doesn't seem to be fully open access." + "\n" + f"You can check the article availability at: {pmc_url}"
    
    # Try to download PDF
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf"
    pdf_response = requests.get(pdf_url, headers=headers)
    
    if pdf_response.status_code != 200:
        logger.error(f"Error: Unable to download PDF (status code: {pdf_response.status_code})")
        logger.info(f"You can try accessing the article directly at: {pmc_url}")
        return f"Error: Unable to download PDF (status code: {pdf_response.status_code})" + "\n" + f"You can try accessing the article directly at: {pmc_url}"
    
    # Save PDF file
    filename = f"PMID_{pmid}_PMC_{pmc_id}.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf_response.content)
    
    logger.info(f"PDF for PMID {pmid} has been downloaded as {filename}")
    return f"PDF for PMID {pmid} has been downloaded as {filename}"

def deep_paper_analysis(paper_metadata):
    """
    Generate a prompt for deep paper analysis
    
    Parameters:
    paper_metadata (dict): A dictionary containing paper metadata
    
    Returns:
    str: A prompt for deep analysis
    """
    title = paper_metadata['Title']
    authors = paper_metadata['Authors']
    journal = paper_metadata['Journal']
    pub_date = paper_metadata['Publication Date']
    abstract = paper_metadata['Abstract']
    
    prompt = f"""
As an expert in scientific paper analysis, please provide a comprehensive analysis of the following paper:

Title: {title}
Authors: {authors}
Journal: {journal}
Publication Date: {pub_date}
Abstract: {abstract}

Please address the following aspects in your analysis:

1. Research Background and Significance:
2. Main Research Questions or Hypotheses:
3. Methodology Overview:
4. Key Findings and Results:
5. Conclusions and Implications:
6. Limitations of the Study:
7. Future Research Directions:
8. Relationship to Other Studies in the Field:
9. Overall Evaluation of the Research:

Ensure your analysis is thorough, objective, and based on the information provided in the paper. If certain information is missing from the abstract, please note this and provide possible inferences or suggestions based on your expertise.
    """
    
    return prompt

def search_key_words(key_words, num_results=10):
    # Generate search URL
    search_url = generate_pubmed_search_url(term=key_words, num_results=num_results)
    logger.info(f"Generated URL: {search_url}")

    # Get and parse search results
    pmids = search_pubmed(search_url)
    
    articles = []
    for pmid in pmids:
        metadata = get_pubmed_metadata(pmid)
        if metadata:
            articles.append(metadata)
    
    return articles

async def async_search_key_words(key_words, num_results=10):
    """Async version of search_key_words using httpx"""
    # Generate search URL
    search_url = generate_pubmed_search_url(term=key_words, num_results=num_results)
    logger.info(f"Generated URL: {search_url}")

    # Get and parse search results asynchronously
    pmids = await async_search_pubmed(search_url)
    
    articles = []
    for pmid in pmids:
        metadata = await async_get_pubmed_metadata(pmid)
        if metadata:
            articles.append(metadata)
    
    return articles

async def async_search_pubmed(search_url):
    """Async version of search_pubmed"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(search_url)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                id_list = root.find("IdList")
                if id_list is not None:
                    return [id.text for id in id_list.findall("Id")]
                else:
                    logger.warning("No results found.")
                    return []
            else:
                logger.error(f"Error: Unable to fetch data (status code: {response.status_code})")
                return []
        except Exception as e:
            logger.error(f"Error in async_search_pubmed: {e}")
            return []

async def async_get_pubmed_metadata(pmid):
    """Async version of get_pubmed_metadata"""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                article = root.find(".//Article")
                if article is not None:
                    title = article.find(".//ArticleTitle")
                    title = title.text if title is not None else "No title available"
                    
                    abstract = article.find(".//Abstract/AbstractText")
                    abstract = abstract.text if abstract is not None else "No abstract available"
                    
                    authors = []
                    for author in article.findall(".//Author"):
                        last_name = author.find(".//LastName")
                        if last_name is not None and last_name.text:
                            authors.append(last_name.text)
                    authors = ", ".join(authors) if authors else "No authors available"
                    
                    journal = article.find(".//Journal/Title")
                    journal = journal.text if journal is not None else "No journal available"
                    
                    pub_date = article.find(".//PubDate/Year")
                    pub_date = pub_date.text if pub_date is not None else "No publication date available"
                    
                    return {
                        "PMID": pmid,
                        "Title": title,
                        "Authors": authors,
                        "Journal": journal,
                        "Publication Date": pub_date,
                        "Abstract": abstract
                    }
                else:
                    logger.warning(f"No article data found for PMID: {pmid}")
                    return None
            else:
                logger.error(f"Error: Unable to fetch metadata (status code: {response.status_code})")
                return None
        except Exception as e:
            logger.error(f"Error in async_get_pubmed_metadata: {e}")
            return None

def search_advanced(term, title, author, journal, start_date, end_date, num_results):
    # Generate search URL
    search_url = generate_pubmed_search_url(term=term, title=title, author=author, 
                                            journal=journal, start_date=start_date, 
                                            end_date=end_date, num_results=num_results)
    logger.info(f"Generated URL: {search_url}")

    # Get and parse search results
    pmids = search_pubmed(search_url)
    
    articles = []
    for pmid in pmids:
        metadata = get_pubmed_metadata(pmid)
        if metadata:
            articles.append(metadata)
    
    return articles

if __name__ == "__main__":
    print("PubMed Search and Analysis Example")
    
    # 1. Search for articles
    print("\n1. Searching for articles about 'COVID-19 vaccine'")
    articles = search_key_words("COVID-19 vaccine", num_results=5)
    
    print("\nSearch Results:")
    for i, article in enumerate(articles, 1):
        print(f"{i}. Title: {article['Title']}")
        print(f"   Authors: {article['Authors']}")
        print(f"   PMID: {article['PMID']}")
        print(f"   Journal: {article['Journal']}")
        print(f"   Publication Date: {article['Publication Date']}")
        print(f"   Abstract: {article['Abstract'][:200]}...")  # Print first 200 characters of abstract
        print("---")

    # 2. Search for articles using advanced search
    print("\n2. Searching for articles using advanced search")
    articles = search_advanced(term="COVID-19", title="vaccine", author="Smith", 
                               journal="Nature", start_date="2020", end_date="2021", num_results=5)
    for i, article in enumerate(articles, 1):
        print(f"{i}. Title: {article['Title']}")
        print(f"   Authors: {article['Authors']}")
        print(f"   PMID: {article['PMID']}")
        print(f"   Journal: {article['Journal']}")
        print(f"   Publication Date: {article['Publication Date']}")
        print(f"   Abstract: {article['Abstract'][:200]}...")
    
    # 3. Download full text PDF
    if articles:
        print("\n2. Attempting to download the full text PDF of the first article")
        download_full_text_pdf(articles[0]['PMID'])

    # 4. Deep Paper Analysis
    if articles:
        print("\n3. Generating prompt for deep analysis of the first article")
        try:
            analysis_prompt = deep_paper_analysis(articles[0])
            print("\nDeep Paper Analysis Prompt:")
            print(analysis_prompt)
            
            # Save analysis prompt to file
            filename = f"analysis_prompt_PMID_{articles[0]['PMID']}.txt"
            with open(filename, 'w') as f:
                f.write(analysis_prompt)
            print(f"\nAnalysis prompt saved to {filename}")
        except Exception as e:
            print(f"An error occurred while generating the analysis prompt: {str(e)}")
    else:
        print("No articles available for analysis.")

    print("\nExample completed. You can modify the search terms and parameters in the script to explore different results.")
