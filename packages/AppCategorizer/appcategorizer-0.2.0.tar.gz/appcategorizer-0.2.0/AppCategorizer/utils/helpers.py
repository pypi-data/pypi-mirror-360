"""
Utility functions for the App Category Analyzer.
"""

def normalize_category(category):
    """
    Normalize category string by converting to lowercase and replacing spaces with underscores.
    
    Args:
        category (str): The category string to normalize
        
    Returns:
        str: Normalized category string
    """
    return category.lower().replace(" ", "_")

def title_case(s, exceptions=None):
    """
    Convert string to title case with specified exceptions.
    
    Args:
        s (str): The string to convert
        exceptions (set, optional): Set of words to keep lowercase. Defaults to None.
        
    Returns:
        str: Title-cased string
    """
    if not s.strip():
        return ""
    if exceptions is None:
        exceptions = {'a','an','the','and','or','but','nor','at','by','for','in','of','on','to','up','as','it','with'}
    words = s.strip().split()
    if not words:
        return ""
    processed = []
    for i, word in enumerate(words):
        lower_word = word.lower()
        if i == 0 or i == len(words) - 1:
            processed.append(lower_word.capitalize())
        else:
            processed.append(lower_word if lower_word in exceptions 
                            else lower_word.capitalize())
    return ' '.join(processed)

# def normalize_labels(labels):
#     normalized_labels = []
#     for label in labels:
#         # Remove inverted commas if present
#         label = label.strip("'").strip('"')
        
#         # Add space before capital letters inside a word
#         label = ''.join(' ' + char if char.isupper() and i != 0 else char for i, char in enumerate(label))
        
#         normalized_labels.append(label)
    
#     # Join the labels into a single string
#     return ', '.join(normalized_labels)

# # Example usage:
# labels = ['Action', 'Network', 'Utilities', 'WebBrowser']
# print(normalize_labels(labels))  # Output: Action, Network, Utilities, Web Browser



# def normalize_labels(labels):
#     return ', '.join(
#         ''.join(' ' + char if char.isupper() and i != 0 else char for i, char in enumerate(label.strip("'").strip('"')))
#         for label in labels
#     )


def normalize_labels(labels):
    def process_label(label):
        result = []
        for i, char in enumerate(label.strip("'").strip('"')):
            if char.isupper() and i != 0 and result[-1].isalpha():
                result.append(' ')
            result.append(char)
        return ''.join(result)

    return ', '.join(process_label(label) for label in labels)