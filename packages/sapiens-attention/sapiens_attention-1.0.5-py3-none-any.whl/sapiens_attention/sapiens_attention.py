# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
# class to get keywords and textual elements of a string that deserve attention
class SapiensAttention:
    def __init__(self):
        from unicodedata import normalize, category
        from re import sub, findall, search
        from yake import KeywordExtractor
        from langdetect import detect
        from string import punctuation
        from collections import Counter
        self.__normalize = normalize
        self.__category = category
        self.__sub = sub
        self.__KeywordExtractor = KeywordExtractor
        self.__detect = detect
        self.__punctuation = punctuation
        self.__Counter = Counter
        self.__findall = findall
        self.__search = search
    def __standard_list(self, text='', maximum_length=10, current_list=[]):
        standard_list = []
        normalized = self.__normalize('NFD', text)
        without_accents = ''.join(character for character in normalized if self.__category(character) != 'Mn')
        clean = self.__sub(r'[^a-zA-Z0-9\s]', '', without_accents).lower().strip()
        standard_list = clean.split()[:maximum_length]
        temporary_list = []
        for word in standard_list:
            if word not in current_list+temporary_list: temporary_list.append(word)
        standard_list = (current_list+temporary_list)[:maximum_length]
        return standard_list
    def get_attention_words(self, text='', maximum_length=10):
        try:
            keywords = []
            text = str(text).strip()
            maximum_length = int(maximum_length) if type(maximum_length) in (bool, int, float) else 0
            if maximum_length <= 0: return []
            try: keyword_extractor = self.__KeywordExtractor(lan=self.__detect(text), n=1, dedupLim=0.7, top=maximum_length)
            except: keyword_extractor = self.__KeywordExtractor(n=1, dedupLim=0.7, top=maximum_length)
            def _clean_text(text=''): return ''.join(character for character in self.__normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII') if character not in self.__punctuation)
            keywords = [_clean_text(text=keyword[0]).lower().strip() for keyword in keyword_extractor.extract_keywords(text)]
            keyword_length = len(keywords)
            if keyword_length < 1: keywords = [_clean_text(text=keyword[0]).lower().strip() for keyword in self.__Counter(self.__findall(r'\b\w{5,}\b', text.lower())).most_common(maximum_words)]
            def _contains_mathematics(text=''): return self.__search(r'\d+\s*[\+\-\*/%]{1,2}\s*\d+', text) is not None
            if _contains_mathematics(text=text) and 'mathematics' not in keywords: keywords += ['mathematics']
            if keyword_length > maximum_length: keywords = keywords[:maximum_length]
            elif keyword_length < maximum_length: keywords = self.__standard_list(text=text, maximum_length=maximum_length, current_list=keywords)
            return sorted(keywords)
        except Exception as error:
            print('ERROR in SapiensAttention.get_attention_words:', error)
            return []
    def get_textual_elements(self, text='', maximum_length=10):
        try:
            elements = []
            text = str(text).strip()
            maximum_length = int(maximum_length) if type(maximum_length) in (bool, int, float) else 0
            text = ''.join(character for character in self.__normalize('NFD', text) if self.__category(character) != 'Mn')
            words = self.__findall(r'\b\w{5,}\b', text)
            numbers = self.__findall(r'\b\d+(?:\.\d+)?\b', text)
            symbols = self.__findall(r'[\+\-\*/%=<>^]', text)
            elements = words + numbers + symbols
            elements_length = len(elements)
            if elements_length > maximum_length: elements = elements[:maximum_length]
            elif elements_length < maximum_length: elements = self.__standard_list(text=text, maximum_length=maximum_length, current_list=elements)
            return sorted([element.lower().strip() for element in elements])
        except Exception as error:
            print('ERROR in SapiensAttention.get_textual_elements:', error)
            return []
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
