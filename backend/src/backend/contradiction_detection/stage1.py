import spacy 

class Stage1:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def chunk(self, sentence):
        list_ = []
        doc = self.nlp(sentence)
        for chunk in doc.noun_chunks:
            list_.extend([token.text for token in chunk if not token.is_stop])
        return set(list_)
    
    def check(self, sentences):
        s1 = sentences[0]
        s2 = sentences[1]
        # print("set1 : ", self.chunk(s1))
        # print("set2 : ", self.chunk(s2))
        # print("intersection : ", self.chunk(s1).intersection(self.chunk(s2)))
        return len(self.chunk(s1).intersection(self.chunk(s2))) > 0


if __name__=='__main__':
    obj = Stage1()
    print("Original :", ["frontend is offline", "the frontend database is not offline"])
    obj.check(["frontend is offline", "the frontend database is not offline"])