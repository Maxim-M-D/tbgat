class Language:
    def __init__(self, start: int, end: int, lang: str, text: str):
        """Initializes the Language class.

        Args:
            start (int): The start character index of the language inside a sentence.
            end (int): The end character index of the language inside a sentence.
            lang (str): The language of the text.
            text (str): The text of the language.
        """
        self.start = start
        self.end = end
        self.lang = lang
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Language(start={self.start}, end={self.end}, lang={self.lang}, text={self.text})"