"""
UI components for the App Category Analyzer.
"""
import streamlit as st
from config import ENERGY_COLORS

def setup_page():
    """
    Set up the Streamlit page configuration.
    """
    st.set_page_config(page_title="BEHAVE- AI App Categorizer", page_icon="📱")
    st.title("BEHAVE - AI App Categorizer")

def render_input_field():
    """
    Render the application name input field.
    
    Returns:
        str: Application name entered by the user
    """
    return st.text_input("Enter application name:", placeholder="e.g. Google Chrome")

def display_raw_categories(non_empty_results):
    """
    Display raw category data from sources in an expandable section.
    
    Args:
        non_empty_results (dict): Dictionary of categories from different sources
    """
    with st.expander("View raw category data from sources"):
        for label, value in non_empty_results.items():
            if isinstance(value, list):
                display_value = ", ".join(value) if value else "No categories found"
            else:
                display_value = value or "No categories found"
            st.markdown(f"**{label}**: {display_value}")

def display_app_description(descriptions):
    """
    Display application descriptions from sources in an expandable section.
    
    Args:
        descriptions (dict): Dictionary of descriptions from different sources
    """
    if not descriptions:
        return
        
    with st.expander("View app descriptions from sources"):
        for source, description in descriptions.items():
            if description:
                st.markdown(f"**{source}**:")
                st.markdown(description.replace("\n\n", "\n\n> "))

def display_results(app_name, main_category, sub_categories, energy_tag):
    """
    Display processed results.
    
    Args:
        main_category (str): Selected main category
        sub_categories (list): Selected subcategories
        energy_tag (str): Assigned energy tag
    """
  
    # Display main category
    st.success(f"**Main Category**: {main_category}")
    
    # Display subcategories
    st.info(f"**Sub Categories**: {', '.join(sub_categories) if sub_categories else 'None'}")
    
    # Energy tag with visual feedback
    # color = ENERGY_COLORS.get(energy_tag.split('-')[0], "blue")
    # st.markdown(f"**Energy Consumption**: :{color}[{energy_tag.replace('-', ' ').title()}]")

def add_footer():
    """
    Add footer information to the page.
    """
    st.markdown("""
    <style>
    .small-text { font-size:0.9em; color:#666; margin-top:15px; }
    </style>
    <div class="small-text">
    * Fetching categories data from SnapCraft, Flathub, Apple Store, Gog, Itch.io, My Abandonware...<br>
    * Energy estimates are based on category averages - actual usage may vary.
    </div>
    """, unsafe_allow_html=True)
