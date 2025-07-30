import os, importlib.resources
os.environ['NLTK_DATA'] = str(importlib.resources.files('strive').joinpath('resources/nltk_data'))

import re, string, unicodedata, faiss, fasttext, numpy as np, bm25s, copy, pickle
from sklearn.feature_extraction.text import HashingVectorizer
from nltk.stem import RSLPStemmer, PorterStemmer
from collections import defaultdict
from model2vec import StaticModel
from functools import lru_cache
from enum import Enum

langdetect_model_path = str(importlib.resources.files('strive').joinpath('resources/lid.176.ftz'))
en_stopwords_path = str(importlib.resources.files('strive').joinpath('resources/en_stopwords.pkl'))
pt_stopwords_path = str(importlib.resources.files('strive').joinpath('resources/pt_stopwords.pkl'))

PUNCTUATION_TABLE = str.maketrans('', '', string.punctuation)
NON_PRINTABLE = set(string.printable)
REGEX_X = re.compile(r'\\x[0-9a-fA-F]{2}')
REGEX_WHITESPACE = re.compile(r'\s+')

def deduplicate_results(ranked_results, top_k=100):
    # Convert ranked results to a dictionary with weights
    results_dict = defaultdict(list)
    for result in ranked_results:
        results_dict[result[0]].append(result[1])

    # Get the max score for each sentence
    max_scores = {}
    for sentence, scores in results_dict.items():
        max_scores[sentence] = max(scores)
    
    # Sort the sentences by their max score, descending
    sorted_sentences = sorted(max_scores.items(), key=lambda x: x[1], reverse=True)

    # Cut to top_k
    deduplicated_results = sorted_sentences[:top_k]

    return deduplicated_results

class EmbeddingType(Enum):
    textual = 1
    semantic = 2

class Reranker:
    """ Semantic Tokenized Re-Ranking via Vectorization & Embeddings """

    def __init__(self, embedding_type: EmbeddingType = EmbeddingType.textual):
        self.langdetect_model = fasttext.load_model(langdetect_model_path)

        self.embedding_type = embedding_type

        self.portuguese_stemmer = RSLPStemmer()
        self.english_stemmer = PorterStemmer()

        self.pt_stopwords = pickle.load(open(pt_stopwords_path, 'rb'))
        self.en_stopwords = pickle.load(open(en_stopwords_path, 'rb'))

        if embedding_type == EmbeddingType.semantic:
            self.vectorizer = StaticModel.from_pretrained("cnmoro/static-nomic-eng-ptbr-tiny")
            self.dimension = self.vectorizer.dim
        else:
            self.dimension = 128
            self.vectorizer = HashingVectorizer(
                analyzer='char_wb',
                ngram_range=(1, 4), # Capture longer subword patterns
                n_features=self.dimension,
                alternate_sign=False # Better for similarity matching
            )

    def _detect_language(self, text):
        detected_lang = self.langdetect_model.predict(text.replace('\n', ' '), k=1)[0][0]
        result = str(detected_lang).replace('__label__', '')
        if result == 'pt':
            return 'pt'
        return 'en'
    
    @lru_cache(maxsize=500000)
    def _stemming(self, word, lang):
        return self.portuguese_stemmer.stem(word) if lang == 'pt' else self.english_stemmer.stem(word)

    @lru_cache(maxsize=500000)
    def _normalize_text(self, text):
        text = unicodedata.normalize('NFKD', text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        text = text.translate(PUNCTUATION_TABLE)
        text = ''.join(c for c in text if c in NON_PRINTABLE)
        text = REGEX_X.sub('', text)
        text = REGEX_WHITESPACE.sub(' ', text).strip()
        return text

    @lru_cache(maxsize=500000)
    def _remove_punctuation_only(self, text):
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def _vectorize_sentences(self, texts):
        if self.embedding_type == EmbeddingType.semantic:
            return self.vectorizer.encode(texts)
        else:
            X = self.vectorizer.transform(texts)
            dense_matrix = X.toarray()
            return dense_matrix

    def _is_stopword(self, word, lang):
        return word in self.pt_stopwords if lang == 'pt' else word in self.en_stopwords
    
    def rerank_documents(self, query, documents, top_k=100):
        try:
            query = query.lower()
            original_documents = copy.deepcopy(documents)
            documents = [document.lower() for document in documents]
            tokenized_corpus = {}
            corpus = documents
            corpus_lang = self._detect_language(' '.join(corpus))
            
            # Track which documents have been included in results
            included_docs = set()
            
            # Build the tokenized corpus
            for corpus_index, sentence in enumerate(corpus):
                sentence_tokens = self._remove_punctuation_only(sentence).split()
                for token_index, token in enumerate(sentence_tokens):
                    stemmed_token = self._stemming(token, corpus_lang)
                    normalized_stemmed_token = self._normalize_text(stemmed_token)
                    if not normalized_stemmed_token or self._is_stopword(token, corpus_lang) or len(normalized_stemmed_token) <= 2:
                        continue
                    tokenized_corpus[f"{corpus_index}_{token_index}"] = normalized_stemmed_token
            
            corpus_tokens = list(tokenized_corpus.values())
            faiss_index = faiss.IndexFlatIP(self.dimension)
            index_map = {}
            counter = 0
            vectors = []
            for key, sentence in tokenized_corpus.items():
                index_map[counter] = key
                vectors.append(sentence)
                counter += 1
            
            if not vectors:  # Handle edge case of empty corpus
                return []
                
            vectors = self._vectorize_sentences(vectors)
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            vectors = vectors / norms
            faiss_index.add(vectors)
            
            # Prepare query tokens
            query_tokens = self._remove_punctuation_only(query).split()
            original_query_tokens = copy.deepcopy(query_tokens)
            
            # Remove stopwords from query tokens
            query_tokens = [token for token in query_tokens if self._normalize_text(token) and not self._is_stopword(token, corpus_lang)]
            
            # Handle edge case of query being a stopword and query_tokens empty
            if not query_tokens:
                query_tokens = [token for token in original_query_tokens if self._normalize_text(token)]
            
            query_tokens = [self._stemming(token, corpus_lang) for token in query_tokens]
            query_tokens = [self._normalize_text(token) for token in query_tokens]
            
            normalized_query_tokens = copy.deepcopy(query_tokens)
            
            query_tokens = [t for t in query_tokens if len(t) > 2]
            
            # Handle edge case where we ONLY have tiny query tokens
            if not query_tokens:
                query_tokens = normalized_query_tokens
            
            # Calculate term frequencies
            term_frequencies = {}
            for qt in query_tokens:
                term_frequencies[qt] = corpus_tokens.count(qt)
                
            # Remove terms with zero frequency
            original_term_frequencies = copy.deepcopy(term_frequencies)
            term_frequencies = {term: freq for term, freq in term_frequencies.items() if freq > 0}
            if not term_frequencies:
                term_frequencies = original_term_frequencies
                term_frequencies = {k: 1 for k in term_frequencies.keys()}
                
            power_factor = 1.2  # Adjust this value to increase the emphasis on lower frequency terms
            # Calculate the inverse of term frequencies with a power factor
            inverse_frequencies = {term: (1/freq) ** power_factor for term, freq in term_frequencies.items()}
            # Normalize the weights so they sum to 1
            total_weight = sum(inverse_frequencies.values())
            normalized_weights = {term: weight / total_weight for term, weight in inverse_frequencies.items()} if total_weight > 0 else {term: 1.0 / len(inverse_frequencies) for term in inverse_frequencies}
            
            seen_base_ids = set()
            results = []
            
            # Step 1: Original token-based search
            for qt in list(term_frequencies.keys()):
                token_vector = self._vectorize_sentences([qt])
                token_score_multiplier = normalized_weights[qt]
                # Normalize
                norm = np.linalg.norm(token_vector)
                token_vector = token_vector / norm
                search_results = faiss_index.search(token_vector, top_k // (len(query_tokens) * 2) if query_tokens else top_k)
                search_result_indexes = search_results[1][0].tolist()
                search_result_scores = search_results[0][0].tolist()
                
                # Interpolate both
                for sri, score in zip(search_result_indexes, search_result_scores):
                    if sri == -1:
                        continue
                    true_id = index_map[sri]
                    recovered_id = int(true_id.split("_")[0])
                    if recovered_id not in seen_base_ids:
                        results.append((recovered_id, score * token_score_multiplier))
                        seen_base_ids.add(recovered_id)
                        included_docs.add(recovered_id)
            
            # Sort results by score, descending
            results.sort(key=lambda x: x[1], reverse=True)
            
            # If we don't have enough results, try fallback 1: original_query_tokens
            if len(results) < top_k and len(documents) >= top_k:
                # Prepare original query tokens (without stemming/filtering)
                original_processed_tokens = []
                for token in original_query_tokens:
                    norm_token = self._normalize_text(token)
                    if norm_token and len(norm_token) > 1:  # Less strict filtering
                        original_processed_tokens.append(norm_token)
                
                fallback_results = []
                min_score = min([score for _, score in results]) if results else 0.5
                fallback_weight = min_score * 0.9  # Slightly lower than the lowest current score
                
                # Use original tokens for search
                for token in original_processed_tokens:
                    if not token:
                        continue
                    token_vector = self._vectorize_sentences([token])
                    # Normalize
                    norm = np.linalg.norm(token_vector)
                    if norm > 0:
                        token_vector = token_vector / norm
                        search_results = faiss_index.search(token_vector, top_k)
                        search_result_indexes = search_results[1][0].tolist()
                        search_result_scores = search_results[0][0].tolist()
                        
                        for sri, score in zip(search_result_indexes, search_result_scores):
                            if sri == -1:
                                continue
                            true_id = index_map[sri]
                            recovered_id = int(true_id.split("_")[0])
                            if recovered_id not in included_docs:
                                fallback_results.append((recovered_id, fallback_weight * score))
                                included_docs.add(recovered_id)
                
                # Add fallback results
                fallback_results.sort(key=lambda x: x[1], reverse=True)
                results.extend(fallback_results)
                results.sort(key=lambda x: x[1], reverse=True)
            
            # If we still don't have enough results, try fallback 2: generic FAISS search
            if len(results) < top_k and len(documents) >= top_k:
                # Prepare complete document vectors for generic search
                doc_vectors = []
                complete_doc_ids = []
                
                for doc_id, doc in enumerate(documents):
                    if doc_id not in included_docs:
                        doc_vector = self._vectorize_sentences([doc])
                        doc_vectors.append(doc_vector[0])
                        complete_doc_ids.append(doc_id)
                
                if doc_vectors:
                    # Build a new FAISS index for complete documents
                    doc_vectors = np.array(doc_vectors)
                    norms = np.linalg.norm(doc_vectors, axis=1, keepdims=True)
                    normalized_doc_vectors = doc_vectors / norms
                    
                    doc_faiss_index = faiss.IndexFlatIP(self.dimension)
                    doc_faiss_index.add(normalized_doc_vectors)
                    
                    # Query vector - use the full query
                    query_vector = self._vectorize_sentences([query])
                    query_norm = np.linalg.norm(query_vector)
                    if query_norm > 0:
                        query_vector = query_vector / query_norm
                        
                        # Find similar documents
                        missing_count = top_k - len(results)
                        search_results = doc_faiss_index.search(query_vector, len(complete_doc_ids))
                        search_result_indexes = search_results[1][0].tolist()
                        search_result_scores = search_results[0][0].tolist()
                        
                        min_score = min([score for _, score in results]) if results else 0.5
                        fallback_weight = min_score * 0.8  # Even lower than the first fallback
                        
                        generic_results = []
                        for i, (idx, score) in enumerate(zip(search_result_indexes, search_result_scores)):
                            if idx == -1:
                                continue
                            doc_id = complete_doc_ids[idx]
                            if doc_id not in included_docs:
                                generic_results.append((doc_id, fallback_weight * score))
                                included_docs.add(doc_id)
                                if len(generic_results) >= missing_count:
                                    break
                        
                        # Add generic results
                        results.extend(generic_results)
            
            # Sort results by score, descending
            results.sort(key=lambda x: x[1], reverse=True)
            filtered_results = results[:top_k]
            
            # Retrieve the sentences from the index map
            final_results = [(corpus[corpus_index], score) for corpus_index, score in filtered_results]

            # Replace the final result documents with the original
            for i, (doc, score) in enumerate(final_results):
                # Find the index of the text in the "documents" list
                doc_index = documents.index(doc)
                final_results[i] = (original_documents[doc_index], score)

            return final_results
            
        except Exception:
            try:
                # Fallback to BM25
                corpus_lang = self._detect_language(' '.join(corpus))
                corpus_tokens = bm25s.tokenize(documents, stopwords=corpus_lang)
                # Create the BM25 model and index the corpus
                retriever = bm25s.BM25()
                retriever.index(corpus_tokens)
                query_tokens = bm25s.tokenize(query)
                results, scores = retriever.retrieve(query_tokens, k=top_k)
                
                # Format results
                final_results = []
                for i in range(results.shape[1]):
                    doc, score = results[0, i], scores[0, i]
                    sentence = corpus[doc]
                    final_results.append((sentence, score))
                
                return final_results
            except Exception:
                return []
