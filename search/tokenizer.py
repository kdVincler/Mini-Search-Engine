import re

STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he", "in", "is", "it", "its", "of", "on", "or", "she", "that", "the", "to", "was", "were", "will", "with",}

# Regex pattern for a string containing only one or more consecuive letters or digits.
_TOKEN_REGEX = re.compile(r"[a-z0-9]+")

def tokenize(text: str) -> list[str]:
    """    
      Simple function that converts a string into a list of 
      lowercased, non-punctuated and non-stopword strings.

      Only module that will handle language specific decisions
      to ensure it is easy to change this tokenizer for a heavy 
      duty one if needed.
   """
    tokens = _TOKEN_REGEX.findall(text.lower())
    return [
         t 
         for t in tokens 
         if t not in STOPWORDS and len(t) > 1
        ]
