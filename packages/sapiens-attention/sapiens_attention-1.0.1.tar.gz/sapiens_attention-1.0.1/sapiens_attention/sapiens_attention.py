# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
# class to get keywords and textual elements of a string that deserve attention
class SapiensAttention:
    def __init__(self):
        from yake import KeywordExtractor
        from langdetect import detect
        from unicodedata import normalize, category
        from string import punctuation
        from collections import Counter
        from re import findall
        from re import search
        self.__KeywordExtractor = KeywordExtractor
        self.__detect = detect
        self.__normalize = normalize
        self.__punctuation = punctuation
        self.__Counter = Counter
        self.__findall = findall
        self.__search = search
        self.__category = category
    def __limit_vector(self, vector=[], maximum_length=0):
        vector_length = len(vector)
        if vector_length < 1 or maximum_length < 1: return []
        return vector[vector_length-min((max((1, maximum_length)), vector_length)):]
    def get_attention_words(self, text='', maximum_words=10):
        try:
            keywords = []
            text = str(text).strip()
            maximum_words = int(maximum_words) if type(maximum_words) in (bool, int, float) else 0
            if maximum_words <= 0: return []
            try: keyword_extractor = self.__KeywordExtractor(lan=self.__detect(text), n=1, dedupLim=0.7, top=maximum_words)
            except: keyword_extractor = self.__KeywordExtractor(n=1, dedupLim=0.7, top=maximum_words)
            def _clean_text(text=''): return ''.join(character for character in self.__normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII') if character not in self.__punctuation)
            keywords = [_clean_text(text=keyword[0]).lower().strip() for keyword in keyword_extractor.extract_keywords(text)]
            keyword_length = len(keywords)
            if keyword_length < 1: keywords = [_clean_text(text=keyword[0]).lower().strip() for keyword in self.__Counter(self.__findall(r'\b\w{5,}\b', text.lower())).most_common(maximum_words)]
            def _contains_mathematics(text=''): return self.__search(r'\d+\s*[\+\-\*/%]{1,2}\s*\d+', text) is not None
            if _contains_mathematics(text=text) and 'mathematics' not in keywords: keywords += ['mathematics']
            if keyword_length > maximum_words: keywords = self.__limit_vector(vector=keywords, maximum_length=maximum_words)
            return sorted(keywords)
        except Exception as error:
            print('ERROR in SapiensAttention.get_attention_words:', error)
            return []
    def get_textual_elements(self, text='', maximum_elements=10):
        try:
            elements = []
            text = str(text).strip()
            maximum_elements = int(maximum_elements) if type(maximum_elements) in (bool, int, float) else 0
            text = ''.join(character for character in self.__normalize('NFD', text) if self.__category(character) != 'Mn')
            words = self.__findall(r'\b\w{5,}\b', text)
            numbers = self.__findall(r'\b\d+(?:\.\d+)?\b', text)
            symbols = self.__findall(r'[\+\-\*/%=<>^]', text)
            elements = words + numbers + symbols
            if len(elements) > maximum_elements: elements = self.__limit_vector(vector=elements, maximum_length=maximum_elements)
            return sorted(elements)
        except Exception as error:
            print('ERROR in SapiensAttention.get_textual_elements:', error)
            return []
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
