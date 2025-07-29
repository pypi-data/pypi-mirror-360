from AnyQt.QtWidgets import QLabel, QVBoxLayout, QRadioButton, QButtonGroup, QPushButton, QLineEdit, QComboBox, QWidget
from AnyQt.QtCore import QThread, pyqtSignal, Qt
from Orange.widgets import widget, settings
from Orange.widgets.widget import Input, Output
from Orange.data import StringVariable
from orangecontrib.text.corpus import Corpus
from orangecontrib.nlp.util.sentence_truncate import truncate_at_sentence
import requests

class SummaryWorker(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(list)

    def __init__(self, texts):
        super().__init__()
        self.texts = texts
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        pass  # Implemented in subclass

class SumyWorker(SummaryWorker):
    def run(self):
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer

        results = []
        for i, text in enumerate(self.texts):
            if self._is_cancelled:
                return
            try:
                parser = PlaintextParser.from_string(text, Tokenizer("english"))
                summarizer = LsaSummarizer()
                summary = summarizer(parser.document, 2)
                results.append(" ".join(str(sentence) for sentence in summary))
            except Exception as e:
                results.append(f"Error: {e}")
            self.progress.emit(int((i + 1) / len(self.texts) * 100))
        self.result.emit(results)


class SummaWorker(SummaryWorker):
    def run(self):
        from summa.summarizer import summarize

        results = []
        for i, text in enumerate(self.texts):
            if self._is_cancelled:
                return
            try:
                summary = summarize(text)
                results.append(summary)
            except Exception as e:
                results.append(f"Error: {e}")
            self.progress.emit(int((i + 1) / len(self.texts) * 100))
        self.result.emit(results)

class BartWorker(SummaryWorker):
    def run(self):
        from transformers import pipeline
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        SUMMARY_LENGTH = 130

        results = []
        for i, text in enumerate(self.texts):
            if self._is_cancelled:
                return
            try:
                if len(text) < SUMMARY_LENGTH:
                    results.append(text)
                else:
                    if len(text) > 3700:
                        text = truncate_at_sentence(text, 3700)
                    summary = summarizer(text, max_length=SUMMARY_LENGTH, min_length=30, do_sample=False)
                    results.append(summary[0]['summary_text'])
            except Exception as e:
                results.append(f"Error: {e}")
            self.progress.emit(int((i + 1) / len(self.texts) * 100))
        self.result.emit(results)

class OllamaSummaryWorker(SummaryWorker):
    def __init__(self, texts, ollama_host, ollama_port, model_name="mistral"):
        super().__init__(texts)
        self.host = ollama_host
        self.port = ollama_port
        self.model_name = model_name

    def run(self):
        results = []
        for i, text in enumerate(self.texts):
            if self._is_cancelled:
                return
            try:
                prompt = (
                    "Summarize the following text using extractive summarization.\n"
                    f"Text: {text}"
                )
                response = requests.post(
                    f"http://{self.host}:{self.port}/api/generate",
                    json={"model": self.model_name, "prompt": prompt, "stream": False},
                    headers={"Content-Type": "application/json"}
                )
                content = response.json().get("response", "")
                results.append(content.strip())
            except Exception as e:
                results.append(f"Error: {e}")
            self.progress.emit(int((i + 1) / len(self.texts) * 100))
        self.result.emit(results)


class OWExtractiveSummary(widget.OWWidget):
    name = "Extractive Summary"
    description = "Extract summaries from text using various frameworks."
    icon = "icons/nlp-extract.svg"
    priority = 120

    class Inputs:
        data = Input("Corpus", Corpus)

    class Outputs:
        data = Output("Corpus with Summaries", Corpus)

    want_main_area = False

    selected_framework = settings.Setting("Sumy")
    ollama_host = settings.Setting("localhost")
    ollama_port = settings.Setting("11434")
    selected_model = settings.Setting("")

    def __init__(self):
        super().__init__()
        self.corpus = None
        self.frameworks = ["Sumy", "Summa", "BART", "Ollama"]

        self.worker = None
        self.layout_control_area()

    def layout_control_area(self):
        a = self.controlArea.layout().addWidget
        self.framework_buttons = QButtonGroup(self)
        for i, fw in enumerate(self.frameworks):
            btn = QRadioButton(fw)
            if fw == self.selected_framework:
                btn.setChecked(True)
            a(btn)
            self.framework_buttons.addButton(btn, i)
        self.framework_buttons.buttonClicked[int].connect(self.select_framework)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_processing)
        a(self.cancel_button)
        self.infoLabel = QLabel("No data on input yet.", self)
        a(self.infoLabel, Qt.AlignmentFlag.AlignLeft)

        self.layout_ollama_config()
        a(self.ollama_panel)
        self.ollama_panel.setVisible(self.selected_framework == "Ollama")
        self.controlArea.layout().setAlignment(Qt.AlignTop)

    def layout_ollama_config(self):
        # Ollama host/port config panel (initially hidden)
        self.ollama_panel = QWidget()
        ollama_layout = QVBoxLayout()
        self.ollama_panel.setLayout(ollama_layout)

        self.host_input = QLineEdit(self.ollama_host)
        self.port_input = QLineEdit(self.ollama_port)
        self.model_selector = QComboBox()
        self.host_input.setPlaceholderText("Ollama Host")
        self.port_input.setPlaceholderText("Ollama Port")

        ollama_layout.addWidget(QLabel("Ollama Host:"))
        ollama_layout.addWidget(self.host_input)
        ollama_layout.addWidget(QLabel("Ollama Port:"))
        ollama_layout.addWidget(self.port_input)
        ollama_layout.addWidget(QLabel("Ollama Model:"))
        ollama_layout.addWidget(self.model_selector)
        self.host_input.editingFinished.connect(self.update_model_list)
        self.port_input.editingFinished.connect(self.update_model_list)
        self.update_model_list()

    def update_model_list(self):
        host, port = self.host_input.text(), self.port_input.text()
        try:
            r = requests.get(f"http://{host}:{port}/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                self.model_selector.clear()
                for m in models:
                    self.model_selector.addItem(m['name'])
                if self.selected_model:
                    index = self.model_selector.findText(self.selected_model)
                    if index >= 0:
                        self.model_selector.setCurrentIndex(index)
        except Exception as e:
            print("Failed to fetch models from Ollama server:", e)
        
    def select_framework(self, index):
        if self.worker and self.worker.isRunning():
            self.cancel_processing()
        self.selected_framework = self.frameworks[index]
        self.ollama_panel.setVisible(self.selected_framework == "Ollama")
        if self.corpus is not None:
            self.start_processing()

    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
            self.infoLabel.setText("Processing cancelled.")
            self.progressBarInit()

    @Inputs.data
    def set_data(self, data):
        self.corpus = data
        if self.corpus is not None:
            self.infoLabel.setText(f"Received {len(self.corpus)} documents.")
            self.start_processing()
        else:
            self.infoLabel.setText("No data on input yet.")
            self.Outputs.data.send(None)

    def start_processing(self):
        if self.worker and self.worker.isRunning():
            self.cancel_processing()
        text_var = next((var for var in self.corpus.text_features), None)
        if text_var is None:
            self.infoLabel.setText("No text attribute found.")
            self.Outputs.data.send(None)
            return

        texts = self.corpus.documents
        framework = self.selected_framework
        if framework == "Sumy":
            self.worker = SumyWorker(texts)
        elif framework == "Summa":
            self.worker = SummaWorker(texts)
        elif framework == "BART":
            self.worker = BartWorker(texts)
        elif framework == "Ollama":
            self.worker = OllamaSummaryWorker(texts, self.ollama_host, self.ollama_port, self.selected_model)
        else:
            self.infoLabel.setText("Unknown framework selected.")
            return

        self.progressBarInit()
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.process_result)
        self.worker.start()
        self.save_ollama_config()
            
    def save_ollama_config(self):
        self.ollama_host = self.host_input.text()
        self.ollama_port = self.port_input.text()
        self.selected_model = self.model_selector.currentText()
        
    def update_progress(self, value):
        self.progressBarSet(value)

    def process_result(self, summary_list):
        summary_var = StringVariable("Extractive Summary")
        new_data = self.corpus.add_column(summary_var, summary_list, to_metas=True)
        self.infoLabel.setText("Summarization complete.")
        self.progressBarFinished()
        self.Outputs.data.send(new_data)

if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    import random

    full_corpus = Corpus("election-tweets-2016")
    indices = random.sample(range(len(full_corpus)), 10)
    sample_corpus = full_corpus[indices]
    WidgetPreview(OWExtractiveSummary).run(sample_corpus)