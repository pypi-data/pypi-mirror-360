import gzip, os, re
from math import log


__version__ = '3.0.0'


# Original idea on how to split strings is from:
# http://stackoverflow.com/a/11642687/2449774
# Thanks Generic Human!


NO_SPACE_BEFORE_BASE = {'.', ',', ';', ':', '!', '?', ')', ']', '}', '%', "'", "’", "s", '»', '›', '-'}
NO_SPACE_AFTER_BASE = {'(', '[', '{', '«', '‹', '¡', '¿', '-', '$', '€', '£'}


class LanguageModel(object):
    """
    Splits, analyzes, and rejoins text based on real-world word frequencies
    for a specified pre-defined language or a custom dictionary file.
    """
    def __init__(self, language='en', word_file=None, add_words=None, blacklist=None, add_to_top=False):
        """
        Initializes a LanguageModel.

        Args:
                language (str): The language code ('en', 'de', etc.) OR 'custom'. Defaults to 'en'.
                word_file (str, optional): Path to a custom gzipped word frequency file.
                                            **Required if language is 'custom'**.
                add_words (list, optional): Words to add to the dictionary.
                blacklist (list, optional): Words to remove from the dictionary.
                add_to_top (bool, optional): If True, add_wordsed words are made common.
        """

        if language == 'custom':
            if not word_file or not os.path.exists(word_file):
                raise ValueError("If language is 'custom', a valid 'word_file' path must be provided.")
        else:
            module_dir = os.path.dirname(os.path.abspath(__file__))

            LANGUAGE_FILES = {
                'en': 'en_dict.txt.gz',
                'de': 'de_dict.txt.gz',
                'fr': 'fr_dict.txt.gz',
                'es': 'es_dict.txt.gz',
                'it': 'it_dict.txt.gz',
                'pt': 'pt_dict.txt.gz'
            }

            if language not in LANGUAGE_FILES:
                raise ValueError(f"Language '{language}' not supported. Use 'custom' and provide a word_file.")

            # For pre-defined languages, construct the path
            word_file = os.path.join(module_dir, 'resources', LANGUAGE_FILES[language])

        with gzip.open(word_file) as f:
            words = f.read().decode('utf-8').split()

        if blacklist:
            blacklist_set = set(blacklist)
            words = [word for word in words if word not in blacklist_set]

        if add_words:
            existing_words = set(words)
            new_words = [w.lower() for w in add_words if w.lower() not in existing_words]
            if add_to_top:
                words = new_words + words
            else:
                words = words + new_words

        self._wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
        self._maxword = max(len(x) for x in words)

        self._no_space_before = NO_SPACE_BEFORE_BASE.copy()
        self._no_space_after = NO_SPACE_AFTER_BASE.copy()

        # Language-specific overrides and additions
        if language == 'de':
            for char in ['%', '-']:
                self._no_space_before.discard(char)
            for char in ['-', '$', '€', '£']:
                self._no_space_after.discard(char)
        elif language == 'fr':
            for char in [':', ';', '!', '?', '»', '%']:
                self._no_space_before.discard(char)
            self._no_space_after.discard('«')
        elif language == 'es':
            self._no_space_before.discard('%')

        self._SPLIT_RE = re.compile(r"\s+")
        self._SPLIT_RE_FOR_CANDIDATES = re.compile(r"(\s+)")


    def split(self, s):
        """
        Uses dynamic programming to infer the location of spaces in a string without spaces.
        """
        delimiters = self._SPLIT_RE.findall(s)
        texts = self._SPLIT_RE.split(s)
        new_texts = [self._split(x) for x in texts]
        
        for i, delimiter in reversed(list(enumerate(delimiters))):
            if delimiter:
                new_texts.insert(i + 1, [delimiter])

        return [item for sublist in new_texts for item in sublist if sublist]


    def _split(self, s):
        # Find the best match for the i first characters, assuming cost has
        # been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length).
        def best_match(i):
            candidates = enumerate(reversed(cost[max(0, i-self._maxword):i]))
            min_cost = float('inf')
            best_k = 0

            for k, c in candidates:
                word = s[i-k-1:i].lower()
                word_cost = self._wordcost.get(word)

                if word_cost is None:
                    if len(word) == 1:
                        # Use a high (but not infinite) penalty for unknown single characters to allow continuation of the algorithm.
                        word_cost = 25
                    else:
                        # Use a a very high penalty for unknown longer words to force splitting into known words.
                        word_cost = 9e999

                current_total_cost = c + word_cost

                if current_total_cost < min_cost:
                    min_cost = current_total_cost
                    best_k = k + 1

            return min_cost, best_k

        # Build the cost array.
        cost = [0]
        for i in range(1,len(s)+1):
            c,k = best_match(i)
            cost.append(c)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(s)
        while i>0:
            c,k = best_match(i)
            assert c == cost[i]
            # Apostrophe and digit handling
            newToken = True
            if not s[i-k:i] == "'": # ignore a lone apostrophe
                if len(out) > 0:
                    # re-attach split 's and split digits
                    if out[-1] == "'s" or (s[i-1].isdigit() and out[-1][0].isdigit()): # digit followed by digit
                        out[-1] = s[i-k:i] + out[-1] # combine current token with previous token
                        newToken = False

            if newToken:
                out.append(s[i-k:i])

            i -= k

        return reversed(out)


    def _post_process_candidate(self, split: list) -> list:
        if not split: return []
        processed_split = [split[0]]
        for i in range(1, len(split)):
            token, prev_token = split[i], processed_split[-1]
            should_merge = (token == "'s" and not prev_token.endswith("'")) or \
                            (token and prev_token and token[0].isdigit() and prev_token[-1].isdigit())
            if should_merge:
                processed_split[-1] += token
            else:
                processed_split.append(token)
        return processed_split


    def _beam_search_on_chunk(self, s_chunk: str, beam_width: int) -> list:
        """
        Runs beam search on a single contiguous string of letters/numbers.
        """
        dp = [[] for _ in range(len(s_chunk) + 1)]
        dp[0] = [([], 0)]

        for i in range(1, len(s_chunk) + 1):
            candidates_for_i = []
            for j in range(max(0, i - self._maxword), i):
                word = s_chunk[j:i]
                word_cost = self._wordcost.get(word)

                if word_cost is None:
                    if len(word) == 1:
                        word_cost = 25    # High but manageable penalty for single unknown chars
                    else:
                        word_cost = 9e999 # Massive penalty for longer unknown words

                if word_cost < 1e100:
                    for prev_split, prev_cost in dp[j]:
                        new_cost = prev_cost + word_cost
                        candidates_for_i.append((prev_split + [word], new_cost))

            dp[i] = sorted(candidates_for_i, key=lambda x: x[1])[:beam_width]

        return dp[len(s_chunk)]


    def candidates(self, s: str, top_n=10) -> list:
        """
        The main public function. It orchestrates the splitting of a complex string
        containing letters, numbers, spaces, and punctuation.
        """
        s = s.lower()
        final_result_count = top_n
        beam_width = max(top_n, 10)
        beam = [([], 0)]

        chunks = [c for c in self._SPLIT_RE_FOR_CANDIDATES.split(s) if c]

        for chunk in chunks:
            new_beam = []
            if self._SPLIT_RE_FOR_CANDIDATES.fullmatch(chunk):
                for prev_split, prev_cost in beam:
                    new_beam.append((prev_split + [chunk], prev_cost))
            else:
                chunk_candidates = self._beam_search_on_chunk(chunk, beam_width)
                if not chunk_candidates:
                    chunk_candidates = [([chunk], 9e999)]

                for prev_split, prev_cost in beam:
                    for chunk_split, chunk_cost in chunk_candidates:
                        new_beam.append((prev_split + chunk_split, prev_cost + chunk_cost))

            beam = sorted(new_beam, key=lambda x: x[1])[:beam_width]

        raw_candidates = [split for split, _ in beam]
        processed_candidates = [self._post_process_candidate(s) for s in raw_candidates]

        return processed_candidates[:final_result_count]


    def rejoin(self, text_string: str) -> str:
        """
        Takes a string, splits it into words using the split() method, and rejoins it
        with typographically correct, multi-language spacing.
        """
        tokens = self.split(text_string)

        if not tokens:
            return ""

        result_parts = []
        in_quotes = False

        # TODO: Expand qoute rules also to single qoutes while keeping german words like "Elias' Haus" intact.
        #        Do not apply special spacing to a double qoute if a second one is never following
        for i, token in enumerate(tokens):
            is_opening_quote = token == '"' and not in_quotes

            result_parts.append(token)

            if token == '"':
                in_quotes = not in_quotes

            # Decide if a space is needed AFTER the current token by looking ahead
            if i < len(tokens) - 1:
                next_token = tokens[i+1]

                add_space = True

                # --- Apply Spacing Rules ---
                # Rule 1: No space if it's an opening quote
                if is_opening_quote:
                    add_space = False
                # Rule 2: No space if the next token is a closing quote
                elif next_token == '"' and in_quotes:
                    add_space = False
                # Rule 3: Standard rules for punctuation and existing spaces
                elif token in self._no_space_after or next_token in self._no_space_before:
                    add_space = False
                elif token.isspace() or next_token.isspace():
                    add_space = False

                if add_space:
                    result_parts.append(" ")

        return "".join(result_parts)


DEFAULT_LANGUAGE_MODEL = LanguageModel(language='en')

def split(s):
    """Splits a string using the default English model."""
    return DEFAULT_LANGUAGE_MODEL.split(s)

def candidates(s, top_n=10):
    """Finds candidates for a string using the default English model."""
    return DEFAULT_LANGUAGE_MODEL.candidates(s, top_n=top_n)

def rejoin(s):
    """Rejoins a string using the default English model's spacing rules."""
    return DEFAULT_LANGUAGE_MODEL.rejoin(s)
