import re
import json

# Multipliers for the get_score method - allows fine tuning of the suggestions
## exact match vs substring -> 2:1
EXACT_MATCH_MULTI = 2
## matches in the data["name"] vs in the data["description"] -> 5:1    
NAME_MATCH_MULTI = 5 

with open('data.json', 'r') as json_data:
    data: list[dict] = json.load(json_data)

class TextureSuggester():
    """
    A class that provides texture suggestions based on an input string.
    """

    def __init__(self) -> None:
        self.exact_match_multi = EXACT_MATCH_MULTI
        self.name_match_multi = NAME_MATCH_MULTI


    def get_score(self, i_words: list[str], d_words: list[str], multiplier: int = 1) -> int:
        """
        Computes the score of matching words between two lists of strings.
        First an exact match is search for (2X multiplier), then check for substrings both ways.
        Args:
            i_words (list[str]): A list of input words to be matched.
            d_words (list[str]): A list of reference words to match against.
            multiplier (int, optional): A multiplier value to apply to matching scores. (1X) for description and (5X) for name.
        Returns:
            int: The final matching score.
        """
        score = 0
        for i_word in i_words:
            if len(i_word) < 2: continue
            i_word = i_word.lower()
            for d_word in d_words:
                if len(d_word) < 2: continue
                d_word = d_word.lower()
                ## check for exact match
                if i_word == d_word: score += (self.exact_match_multi*multiplier) 
                ## check for substring match - (check "in" both ways to ensure still matches if extra characters in input string compared to data - e.g input: "greenn" should match "green")
                elif i_word in d_word or d_word in i_word : score += multiplier
        return score
        

    def get_suggestions(self, input: str, limit: int = 5) -> list[dict]:
        """
        Retrieves a list of dictionary objects that match a given input string.
        Both Name and Description string matches are evaluated, (5X) multiplier for name matches
        Args:
            input (str): The input string to match against.
            limit (int): The maximum number of matches to return.
        Returns:
            list[dict]: A list of dictionary objects containing matching data entries.
        """
        input_words = re.findall(r"[\w']+", input) #split input string into words and remove punctuation
        if len(input_words) == 0:  return []

        for i, entry in enumerate(data):
            score = 0
            name_words = re.findall(r"[\w']+", entry["name"])   #split name into words and remove punctuation
            desc_words = re.findall(r"[\w']+", entry["description"])    #split desc into words and remove punctuation
            score += self.get_score(input_words, name_words, multiplier=self.name_match_multi)
            score += self.get_score(input_words, desc_words)
            data[i]["score"] = score

        response = [entry for entry in data if entry["score"]>0]
        response = sorted(response, key=lambda entry: entry['score'], reverse=True)
        return response[:limit]