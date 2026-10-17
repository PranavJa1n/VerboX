import spacy

nlp = spacy.load("en_core_web_sm")

text1 = "The database is offline."
text2 = "The database is not offline."

doc1 = nlp(text1)
list1 = []

doc2 = nlp(text2)
list2 = []

for chunk in doc1.noun_chunks:
        list1.append(chunk.root.text)
for chunk in doc2.noun_chunks:
        list2.append(chunk.root.text)

print(list1)
print(len(set(list1).intersection(set(list2))))
print(list2)


