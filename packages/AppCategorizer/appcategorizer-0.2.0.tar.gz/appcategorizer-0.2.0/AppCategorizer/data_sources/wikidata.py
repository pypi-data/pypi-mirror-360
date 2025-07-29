"""
Wikidata integration for fetching application categories.
"""
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from ..utils.helpers import title_case

def get_categories(app_name):
    """
    Fetch categories (instanceOfLabel) from Wikidata for a given application name.
    
    Args:
        app_name (str): Name of the application
        
    Returns:
        list: List of categories for the application
    """
    app_name = title_case(app_name)
    endpoint_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?instanceOfLabel WHERE {{
      ?software rdfs:label "{app_name}"@en .
      OPTIONAL {{ ?software wdt:P31 ?instanceOf }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    """
    
    # Setup SPARQL query
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute query and parse results
    try:
        results = sparql.query().convert()
        categories = [
            result["instanceOfLabel"]["value"]
            for result in results["results"]["bindings"]
            if "instanceOfLabel" in result
        ]
        return categories
    except Exception:
        return []