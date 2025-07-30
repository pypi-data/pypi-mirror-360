from presidio_analyzer import AnalyzerEngine
 
def pii_filter(text,entities):
    analyzer = AnalyzerEngine()
    results = analyzer.analyze(text=text, language="en",entities=entities)
    recognized_keywords = []
    keywords = []
    
    def remove_low_scores(result):
        if result.score > 0.2:
            return True
        return False

    recognized_keywords = filter(remove_low_scores, results)
    for item in recognized_keywords:
        if item.score > 0.2:
            start = item.start
            end = item.end
            word = text[start:end]
            keywords.append(word)
            
    keywords = list(set(keywords))
    
    for word in keywords:
        highlighted_word = f"<strong>{word}</strong>"
        text = text.replace(word, highlighted_word)
        
    return text