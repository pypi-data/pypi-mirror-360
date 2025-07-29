import spacy
from spacy.cli import download as spacy_download

class SpaCyDownloader:
    @staticmethod
    def model_name(language_code: str) -> str:
        SPACY_LANGUAGE_MODELS = {
            'ca': 'ca_core_news_sm',
            'zh': 'zh_core_web_sm',
            'da': 'da_core_news_sm',
            'nl': 'nl_core_news_sm',
            'en': 'en_core_web_sm',
            'fr': 'fr_core_news_sm',
            'de': 'de_core_news_sm',
            'el': 'el_core_news_sm',
            'it': 'it_core_news_sm',
            'ja': 'ja_core_news_sm',
            'lt': 'lt_core_news_sm',
            'mk': 'mk_core_news_sm',
            'nb': 'nb_core_news_sm',
            'pl': 'pl_core_news_sm',
            'pt': 'pt_core_news_sm',
            'ro': 'ro_core_news_sm',
            'ru': 'ru_core_news_sm',
            'es': 'es_core_news_sm',
            'sl': 'sl_core_news_sm',
            'sv': 'sv_core_news_sm',
            'uk': 'uk_core_news_sm',
            'xx': 'xx_ent_wiki_sm'  # Multi-language model
        }

        language_code = language_code.lower()
        model_name = SPACY_LANGUAGE_MODELS.get(language_code, None)
        return model_name
    
    @staticmethod
    def download_language(language_code: str) -> bool:
        model_name = SpaCyDownloader.model_name(language_code)
        if model_name is None: return False
        SpaCyDownloader.download(model_name)
        return True

    @staticmethod
    def download(model_name: str) -> bool:
        try:
            spacy_download(model_name)
        except Exception:
            return False
        return True
