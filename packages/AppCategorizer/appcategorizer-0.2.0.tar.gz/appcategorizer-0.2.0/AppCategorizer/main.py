from transformers import pipeline
import sys


# Redirect stderr and stdout to suppress DevTools and other messages
class SuppressOutput:
    def write(self, s): pass
    def flush(self): pass
# Import data source modules
from .data_sources import snap, flathub, apple_store, gog, itch_io, myabandonware, wikidata

# Import category processing functions
# from category_processing.processor import (
#     select_main_category,
#     select_sub_categories,
#     assign_energy_tag
# )



# Import UI components
# from ui.interface import (
#     setup_page,
#     render_input_field,
#     display_raw_categories,
#     display_app_description,
#     display_results,
#     add_footer
# )

from .utils.helpers import normalize_labels

# from config import ENERGY_COLORS, ENERGY_TAGS

# Initialize the model
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Declare energy tag
# energy_tag_value = ENERGY_TAGS

def fetch_app_data(app_name):
    """Fetch application data from all sources."""
    # with st.spinner("Fetching app category data..."):
        # Fetch data from all sources
    snap_cats = snap.get_categories(app_name)
    flat_cats = flathub.get_categories(app_name)
    apple_cats = apple_store.get_categories(app_name)
    gog_cats = gog.get_categories(app_name)
    itch_cats = itch_io.get_categories(app_name)
    abandon_cats = myabandonware.get_categories(app_name)
    wiki_cats = wikidata.get_categories(app_name)

        # Organize all results in a dictionary
    raw_categories = {
        "Snapcraft": snap_cats,
        "Flathub": flat_cats,
        "Apple Store": apple_cats,
        "Gog": gog_cats,
        "Itch.io": itch_cats,
        "My Abandonware": abandon_cats,
    }

        # Filter empty results
    non_empty_results = {k: v for k, v in raw_categories.items() if v}

        # Use wikidata only when no other source data is available
    if len(non_empty_results) == 0 and wiki_cats:
        non_empty_results = {"Wikidata": wiki_cats}

    return non_empty_results


def fetch_app_descriptions(app_name):
    """Fetch application descriptions from all sources."""
    # with st.spinner("Fetching app descriptions..."):
    sources = [
            ("Apple Store", apple_store),
            ("Snapcraft", snap),
            ("Flathub", flathub),
            ("Gog", gog),
            ("Itch.io", itch_io),
            # ("My Abandonware", myabandonware),
            # ("Wikidata", wikidata),
        ]
    descs = []
    source_names = []
    for name, module in sources:
        if hasattr(module, "get_description"):
            desc = module.get_description(app_name)
            if desc:
                descs.append(desc.replace('\n', ' ').strip())
                source_names.append(name)

    if descs:
        return {', '.join(source_names): ' '.join(descs)}
    else:
        return {}


def categorize_app(classifier, tags, descriptions):
    """Categorize the application based on tags and descriptions."""
    all_tags = []
    all_descriptions = []

    for tag_list in tags.values():
        all_tags.extend(tag_list)

    for desc in descriptions.values():
        all_descriptions.append(desc)

    all_tags = list(set(all_tags))  # Remove duplicates
    # all_tags_str = ', '.join(all_tags)

    # labels = ["Productivity", "Entertainment", "Social Media", "Education", "Games", "Utilities"]
    # labels = normalize_labels(all_tags_str)
    results = []
    # with st.spinner("Model is processing..."):
    # with st.container():
        # my_bar = st.progress(0)
    for i, description in enumerate(all_descriptions):
            # my_bar.progress((i + 1) / len(all_descriptions))
            # outputs = classifier(description, labels, multi_label=True)
            outputs = classifier(description, normalize_labels(all_tags).split(', '), multi_label=True)
            results.append({"description": description, "labels": outputs['labels'], "scores": outputs['scores']})

    return results

# @st.cache_resource
def load_model():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")



def fetch_category():
    if len(sys.argv) > 1:
        app_name = ' '.join(sys.argv[1:])
        # Suppress unwanted output
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = SuppressOutput()
        sys.stderr = SuppressOutput()
        
        non_empty_results = fetch_app_data(app_name)
        descriptions = fetch_app_descriptions(app_name)
        classifier = load_model()
        tags = non_empty_results
        categorized_results = categorize_app(classifier, tags, descriptions)
        
        # Restore stdout and stderr for printing the result
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        for result in categorized_results:
            category = result['labels'][0]
            print(category)
    else:
        # Run the Streamlit app
        # import streamlit_app
        # streamlit_app.main()
        print("Opps, Try again! si vous play")

if __name__ == "__main__":
    fetch_category()