import requests
from xml.etree import ElementTree

### Pubmed search
# Getting pubmed articles IDs
def pubmed_search(search):

    parameters_id = {
        "tool": "MyTool",
        "email":" MyEmail",
        "db": "pubmed",
        "retmode": "xml",
        "retmax": 20,
        "term": search
    }

    response_id = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params = parameters_id) # getting the data in XML format

    tree_id = ElementTree.fromstring(response_id.content) # transforming the data from XML into a Python object

    ids = []

    for child in tree_id.find("IdList"):
        ids.append(child.text)

    ids_as_string = ",".join(ids)

    # Getting pubmed information from articles IDs
    parameters_fetch = {
        "tool": "MyTool",
        "email":" MyEmail",
        "db": "pubmed",
        "retmode": "xml",
        "id": ids_as_string
    }

    response_fetch = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", params = parameters_fetch)

    tree_fetch = ElementTree.fromstring(response_fetch.content)

    # Extracting information from the summary XML
    pubmed_results = []
    for article in tree_fetch.findall("DocSum"):
        id = article.find("Id").text
        date = article.find('Item[@Name="PubDate"]').text
        authors = []
        for author in article.findall('./Item[@Name="AuthorList"]/Item[@Name="Author"]'):
            authors.append(author.text)
        authors_as_string = ", ".join(authors)
        title = article.find('Item[@Name="Title"]').text
        if article.find('./Item[@Name="PubTypeList"]/Item[@Name="PubType"]') != None:
            type = article.find('./Item[@Name="PubTypeList"]/Item[@Name="PubType"]').text
        else:
            type = "-"
        if article.find('Item[@Name="DOI"]') != None:
            doi = article.find('Item[@Name="DOI"]').text
        else:
            doi = "-"
        # Appending to list
        pubmed_results.append({"id": id, "date": date, "authors": authors_as_string, "title": title, "type": type, "doi": doi})

    return pubmed_results

    '''Bibliography:
    https://docs.python.org/2/library/xml.etree.elementtree.html
    https://www.ncbi.nlm.nih.gov/books/NBK25499/
    '''
