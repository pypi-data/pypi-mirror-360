import subprocess
from os.path import dirname
import os
import time

test_combos = [
    ['OWAbstractiveSummary', 'book-excerpts', '1', 'selected_framework', 'BART'],
    ['OWAbstractiveSummary', 'book-excerpts', '1', 'selected_framework', 'T5'],
    ['OWAbstractiveSummary', 'book-excerpts', '1', 'selected_framework', 'FLAN-T5'],
    ['OWAbstractiveSummary', 'book-excerpts', '1', 'selected_framework', 'Pegasus'],
    ['OWExtractiveSummary', 'book-excerpts', '1', 'selected_framework', 'Sumy'],
    ['OWExtractiveSummary', 'book-excerpts', '1', 'selected_framework', 'Summa'],
    ['OWExtractiveSummary', 'book-excerpts', '1', 'selected_framework', 'BART'],
    ['OWNERWidget', 'friends-transcripts', '10', 'selected_framework', 'NLTK'],
    ['OWNERWidget', 'friends-transcripts', '10', 'selected_framework', 'spaCy'],
    ['OWNERWidget', 'friends-transcripts', '10', 'selected_framework', 'Flair'],
    ['OWPOSTagger', 'friends-transcripts', '10', 'selected_framework', 'spaCy'],
    ['OWPOSTagger', 'friends-transcripts', '10', 'selected_framework', 'Stanza'],
    ['OWPOSTagger', 'friends-transcripts', '10', 'selected_framework', 'UDPipe'],
    ['OWQuestionAnswer', 'andersen', '1', 'question', "Who's the bad guy?"], # times out
    ['OWReferenceLibrary', 'book-excerpts', '1', 'embedder', 'SBERTEmbedder', 'query', 'farming'],
    ['OWAnalizaSentymentu', 'datasets/recenzja_produktu.tab', '10'],
    # I do the Ollama models together since the server component will cache the model between processes, but only for a few minutes
    ['OWAbstractiveSummary', 'book-excerpts', '1', 'selected_framework', 'Ollama', 'selected_model', 'phi:latest'],
    ['OWExtractiveSummary', 'book-excerpts', '1', 'selected_framework', 'Ollama', 'selected_model', 'phi:latest'],
    ['OWNERWidget', 'friends-transcripts', '10', 'selected_framework', 'Ollama', 'selected_model', 'phi:latest'],
    ['OWOllamaRAG', 'book-excerpts', '1', 'model', 'phi:latest', 'prompt', 'who died?']
]

embedders = [
    #"Doc2VecEmbedder",
    "E5Embedder",
    "FastTextEmbedder",
    "GeminiEmbedder",
    "NomicEmbedder",
    "OpenAIEmbedder",
    "SBERTEmbedder",
    "SpacyEmbedder",
    "USEEmbedder",
]

test_combos = []
for emb in embedders:
    test_combos.append( ['OWTextEmbedder', 'book-excerpts', '1', 'embedder', emb] )

for combo in test_combos:
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print(" ".join([now]+combo))
    cmd = ["python"]
    args = [dirname(__file__)+os.sep+"test_single.py"]+combo
    p = subprocess.run(cmd+args, capture_output=True)
    print(p.stdout.decode('utf-8'))
    print(p.stderr.decode('utf-8'))