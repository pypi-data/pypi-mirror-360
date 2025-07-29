from AnyQt.QtWidgets import QLabel
from AnyQt.QtCore import QThread, pyqtSignal
from Orange.widgets import widget, settings
from Orange.widgets.widget import Input, Output
from Orange.data import Domain, StringVariable, Table
from orangecontrib.text.corpus import Corpus
import numpy as np

class TokenCorpusWorker(QThread):
    result = pyqtSignal(Corpus)
    progress = pyqtSignal(int)

    def __init__(self, corpus: Corpus):
        super().__init__()
        self.corpus = corpus
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        corpus = self.corpus
        title = None
        for col in corpus.domain.metas:
            if 'title' in col.name.lower():
                title = col

        documents = []
        titles = []

        n_docs = len(corpus.tokens)
        for idx, doc in enumerate(corpus.tokens):
            for token in doc:
                if title:
                    titles.append(corpus[idx][title.name].value)
                documents.append(token)
            self.progress.emit(int((idx + 1) / n_docs * 100))

        token_var = StringVariable("Token")
        if title:
            domain = Domain([], metas=[token_var, title])
            metas_array = np.array(list(zip(documents, titles)), dtype=object)
        else:
            domain = Domain([], metas=[token_var])
            metas_array = np.array(list(zip(documents,)), dtype=object)
        table = Table.from_numpy(domain, X=np.empty((len(metas_array), 0)), metas=metas_array)

        token_corpus = Corpus.from_table(domain, table)
        token_corpus.attributes = corpus.attributes.copy()
        token_corpus.set_text_features([token_corpus.domain["Token"]])

        self.result.emit(token_corpus)


class OWTokenCorpus(widget.OWWidget):
    name = "Tokens to Corpus"
    description = "Takes tokens from Preprocess Text and outputs them as a Corpus."
    icon = "icons/nlp-token2corpus.svg"
    priority = 100

    class Inputs:
        data = Input("Corpus", Corpus)

    class Outputs:
        data = Output("Tokenized Corpus", Corpus)

    chunk_size = settings.Setting(256)
    want_main_area = False

    def __init__(self):
        super().__init__()

        self.corpus = None
        self.worker = None
        self.controlArea.layout().addWidget(QLabel("Tip: If you want to split on paragraphs, use regexp: [^\\.\\!\\?]+"))

    @Inputs.data
    def set_data(self, data: Corpus):
        self.corpus = data
        self.apply()

    def apply(self):
        if not self.corpus:
            self.Outputs.data.send(None)
            return

        self.progressBarInit()
        self.worker = TokenCorpusWorker(self.corpus)
        self.worker.progress.connect(self.progressBarSet)
        self.worker.result.connect(self.finished)
        self.setStatusMessage("Converting Tokens to Corpus...")
        self.setBlocking(True)
        self.worker.start()


    def finished(self, result: Corpus):
        self.progressBarFinished()
        self.setStatusMessage("")
        self.setBlocking(False)
        if result:
            self.Outputs.data.send(result)
        else:
            self.Outputs.data.send(None)


if __name__ == "__main__":
    import unittest
    from Orange.widgets.tests.base import WidgetTest
    from orangecontrib.text.widgets.owpreprocess import OWPreprocess

    class TestOWTokenCorpusWidget(WidgetTest):
        def setUp(self):
            super().setUp()
            self.corpus = Corpus("andersen")
            self.preprocess_widget = self.create_widget(OWPreprocess)
            self.token_corpus_widget = self.create_widget(OWTokenCorpus)

        def test_sentence_tokenization_flow(self):
            # Simulate a tiny corpus
            corpus = self.corpus
            # Send corpus to OWPreprocess and enable sentence tokenization
            self.widget = self.preprocess_widget
            self.send_signal(self.preprocess_widget.Inputs.corpus, corpus)
            settings = {'name': '', 'preprocessors': [('preprocess.tokenize', {'method': 2, 'pattern': '\\w+'})]}
            self.preprocess_widget.storedsettings = settings
            self.preprocess_widget.load(settings)
            self.preprocess_widget.apply()  # Apply settings if needed

            # Get the output from OWPreprocess
            processed_corpus = self.get_output("Corpus", self.preprocess_widget)
            self.assertIsNotNone(processed_corpus)

            # Send processed corpus to OWTokenCorpus
            self.widget = self.token_corpus_widget
            self.send_signal(self.token_corpus_widget.Inputs.data, processed_corpus)

            # Get the output from OWTokenCorpus
            token_output = self.get_output("Tokenized Corpus", self.token_corpus_widget)
            self.assertIsNotNone(token_output)

            # Optional: Check that tokens are sentence-level
            for doc in token_output.documents:
                print(doc)

    unittest.main()