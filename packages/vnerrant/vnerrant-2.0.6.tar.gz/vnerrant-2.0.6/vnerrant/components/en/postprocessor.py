from typing import Optional

from vnerrant.components.en.constants import ChildrenErrorType, ParentErrorType, base_dir, language_resources
from vnerrant.components.postprocessor import BasePostprocessor
from vnerrant.constants import Operator, SeparatorTypes
from vnerrant.model.edit import EditCollection
from vnerrant.utils.replacing import ReplacingRule
from vnerrant.utils.wordlist import WordListAdapter


class Postprocessor(BasePostprocessor):

    def __init__(self):
        self.noun_wordlist = self._import(WordListAdapter, "wrong_nouns.txt")
        self.replacing_rule = self._import(ReplacingRule, "replacing.dat")

    @staticmethod
    def _import(obj_class, filename: Optional[str] = None):
        data_path = base_dir / "resources"
        if filename:
            data_path = data_path / filename

        if data_path.exists():
            return obj_class(data_path.absolute().as_posix())
        else:
            return None

    def process(self, edit_collection: EditCollection, **kwargs):
        self._postprocess_noun_number(edit_collection)
        self._postprocess_verb_choice(edit_collection)
        self._postprocess_adverb(edit_collection)
        self._postprocess_determiner(edit_collection)
        self._postprocess_verb_tense(edit_collection)
        self._postprocess_verb_form(edit_collection)
        self._postprocess_spelling(edit_collection)
        self._postprocess_question_tag(edit_collection)

    @staticmethod
    def __find_next_token_span(current_start_char: int, current_end_char: int, sequence: str, order: int = 1):
        """
        Find the next token span in the sequence based on the current start and end character indices.

        Args:
            current_start_char (int): The start character index of the current token.
            current_end_char (int): The end character index of the current token.
            sequence (str): The text sequence to search within.

        Returns:
            tuple: A tuple containing the start and end character indices of the next token.
        """
        start, end = current_start_char, current_end_char

        for _ in range(order):
            # find the very next token after the current span
            found_start = None
            for i, ch in enumerate(sequence[end:]):
                if found_start is None and not ch.isspace():
                    # mark the first non-space character
                    found_start = end + i
                elif found_start is not None and ch.isspace():
                    # we've reached the end of that token
                    start, end = found_start, end + i
                    break
            else:
                # hit end of string before another space
                if found_start is None:
                    # no more tokens at all
                    raise ValueError("No further token found")
                start, end = found_start, len(sequence)

        return start, end

    @staticmethod
    def __find_prev_token_span(current_start_char: int, sequence: str, order: int = 1) -> tuple[int, int]:
        """
        Find the span of the n-th previous token in the sequence.

        Args:
            current_start_char (int): start index of the current token
            sequence           (str): the full text
            order              (int): which previous token to find (1 = first previous, 2 = second previous, ...)

        Returns:
            (start, end) span of the requested previous token
        """
        end = current_start_char
        start = current_start_char

        for _ in range(order):
            found_end = None
            # scan backward from just before the current token start
            for i in range(start - 1, -1, -1):
                ch = sequence[i]
                # first non-space we encounter marks the end of the previous token
                if not ch.isspace() and found_end is None:
                    found_end = i + 1
                # once we've marked the end, the next space marks the start boundary
                elif found_end is not None and ch.isspace():
                    start, end = i + 1, found_end
                    break
            else:
                # reached the beginning of the string
                if found_end is None:
                    raise ValueError("No previous token found")
                start, end = 0, found_end

        return start, end

    def _postprocess_noun_number(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for noun number.
        Update NOUN_NUMBER -> NOUN_INFLECTION if the word is in the noun wordlist.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        if self.noun_wordlist is None:
            return

        noun_number = ParentErrorType.NOUN + SeparatorTypes.COLON + ChildrenErrorType.NUMBER
        noun_inflection = ParentErrorType.NOUN + SeparatorTypes.COLON + ChildrenErrorType.INFLECTION

        for edit in edit_collection.edits:
            if edit.is_space:
                continue
            if edit.edit_type[2:] != noun_number:
                continue

            text = edit.original.text.strip().lower()
            if self.noun_wordlist.check(text):
                edit.edit_type = edit.edit_type[:2] + noun_inflection

            # special case "every days" -> "every day"
            index = edit.original.start_token
            if text == "days" and index - 1 >= 0 and edit_collection.orig_doc[index - 1].lower_ == "every":
                edit.edit_type = edit.edit_type[:2] + noun_inflection

    def _postprocess_verb_choice(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for verb choice.
        Update VERB_CHOICE -> VERB_INFLECTION if the corrected word is in the replacing rule.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        if self.replacing_rule is None:
            return

        verb_choice = ParentErrorType.VERB
        verb_inflection = ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.INFLECTION

        for edit in edit_collection.edits:
            if edit.is_space:
                continue
            if edit.edit_type[2:] != verb_choice:
                continue

            text = edit.original.text.strip()
            corrected = edit.corrected.text.strip()
            replacing = self.replacing_rule.suggest(text)
            if corrected in replacing:
                edit.edit_type = edit.edit_type[:2] + verb_inflection

    def _postprocess_adverb(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for adverb.
        Update ADV -> ADJECTIVE_FORM if the word is in {more, most} and place before an adj.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """

        def _is_next_token_adj(doc, index):
            if index < len(doc):
                return doc[index].pos_ == "ADJ"
            return False

        adverb_choice = ParentErrorType.ADVERB
        adjective_form = ParentErrorType.ADJECTIVE + SeparatorTypes.COLON + ChildrenErrorType.FORM

        for edit in edit_collection.edits:
            if edit.is_space:
                continue
            if edit.edit_type[2:] != adverb_choice:
                continue

            original = edit.original.text.strip().lower()
            corrected = edit.corrected.text.strip().lower()

            if original in ["more", "most"]:
                next_token_index = edit.original.start_token + 1
                if _is_next_token_adj(edit_collection.orig_doc, next_token_index):
                    edit.edit_type = edit.edit_type[:2] + adjective_form

            if corrected in ["more", "most"]:
                next_token_index = edit.corrected.start_token + 1
                if _is_next_token_adj(edit_collection.cor_doc, next_token_index):
                    edit.edit_type = edit.edit_type[:2] + adjective_form

    def _postprocess_determiner(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for determiner.
        Update DET -> PRONOUN because the wrong pos mapping.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        determiner = ParentErrorType.DETERMINER
        pronoun = ParentErrorType.PRONOUN

        for edit in edit_collection.edits:
            if edit.is_space:
                continue
            if edit.edit_type[2:] != determiner:
                continue

            relative_pronouns = [
                "that",
                "which",
                "who",
                "whom",
                "whose",
                "where",
                "whoever",
                "whomever",
            ]

            if edit.original.end_token - edit.original.start_token == 1 and edit.original.tokens:
                if edit.original.tokens[0].pos_ == "PRON" and edit.original.text.strip().lower() in relative_pronouns:
                    edit.edit_type = edit.edit_type[:2] + pronoun

            if edit.corrected.end_token - edit.corrected.start_token == 1 and edit.corrected.tokens:
                if edit.corrected.tokens[0].pos_ == "PRON" and edit.corrected.text.strip().lower() in relative_pronouns:
                    edit.edit_type = edit.edit_type[:2] + pronoun

    def _postprocess_verb_tense(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for verb tense.
        Update VERB_TENSE -> VERB_CHOICE if both original and corrected are verb, have same tag and different lemma.

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        verb_tense = ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.TENSE
        verb_choice = ParentErrorType.VERB

        for edit in edit_collection.edits:
            if edit.is_space:
                continue
            if edit.edit_type[2:] != verb_tense:
                continue
            if edit.original.end_token - edit.original.start_token != 1:
                continue
            if edit.corrected.end_token - edit.corrected.start_token != 1:
                continue
            if not edit.original.tokens or not edit.corrected.tokens:
                continue

            o_token = edit.original.tokens[0]
            c_token = edit.corrected.tokens[0]

            if o_token.tag_ == c_token.tag_ and o_token.lemma_ != c_token.lemma_:
                edit.edit_type = edit.edit_type[:2] + verb_choice

    def _postprocess_verb_form(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for verb form.
        Update VERB_FORM -> VERB_TENSE if either original or corrected is verb, and tag is in [VBN, VBD]
        Update VERB_FORM -> SUBJECT_VERB_AGREEMENT because the wrong pos in special case "has/have"

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        verb_form = ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.FORM
        verb_tense = ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.TENSE
        subject_verb_agreement = ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.SUBJECT_VERB_AGREEMENT

        for edit in edit_collection.edits:
            if edit.is_space:
                continue
            if edit.edit_type[2:] != verb_form:
                continue
            if edit.original.end_token - edit.original.start_token != 1:
                continue
            if edit.corrected.end_token - edit.corrected.start_token != 1:
                continue
            if not edit.original.tokens or not edit.corrected.tokens:
                continue

            o_token = edit.original.tokens[0]
            c_token = edit.corrected.tokens[0]

            # VERB_FORM -> VERB_TENSE
            if (o_token.tag_ in ["VBN", "VBD"] or c_token.tag_ in ["VBN", "VBD"]) and o_token.tag_ != c_token.tag_:
                edit.edit_type = edit.edit_type[:2] + verb_tense
                continue

            # VERB_FORM -> SUBJECT_VERB_AGREEMENT
            if (
                edit.original.text.strip().lower() in ["has", "have"]
                and edit.corrected.text.strip().lower() in ["has", "have"]
                and c_token.tag_ in ["VB", "VBZ"]
            ):
                edit.edit_type = edit.edit_type[:2] + subject_verb_agreement

    def _postprocess_spelling(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for spelling.
        Update SPELLING -> SUBJECT_VERB_AGREEMENT because the wrong pos in special case "like/likes"
        Update SPELLING -> NOUN_INFLECTION because the wrong lemma of some special wrong nouns (technologys, studys).

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        spelling = ParentErrorType.SPELLING
        subject_verb_agreement = ParentErrorType.VERB + SeparatorTypes.COLON + ChildrenErrorType.SUBJECT_VERB_AGREEMENT
        noun_inflection = ParentErrorType.NOUN + SeparatorTypes.COLON + ChildrenErrorType.INFLECTION

        for edit in edit_collection.edits:
            if edit.is_space:
                continue
            if edit.edit_type[2:] != spelling:
                continue
            if edit.original.end_token - edit.original.start_token != 1:
                continue
            if edit.corrected.end_token - edit.corrected.start_token != 1:
                continue
            if not edit.original.tokens or not edit.corrected.tokens:
                continue

            # SPELLING -> SUBJECT_VERB_AGREEMENT
            if (
                edit.original.text.strip().lower() in ["like", "likes"]
                and edit.corrected.text.strip().lower() in ["like", "likes"]
                and edit.corrected.tokens[0].tag_ in ["VB", "VBZ"]
            ):
                edit.edit_type = edit.edit_type[:2] + subject_verb_agreement
                continue

            # SPELLING -> NOUN_INFLECTION
            if (
                edit.original.text.strip().isalpha()
                and edit.original.tokens[0].text not in language_resources.spell
                and edit.original.tokens[0].lower_ not in language_resources.spell
                and edit.corrected.tokens[0].pos_ == "NOUN"
                and edit.corrected.text.strip() in self.replacing_rule.suggest(edit.original.text.strip())
            ):
                edit.edit_type = edit.edit_type[:2] + noun_inflection
                continue

    def _postprocess_question_tag(self, edit_collection: EditCollection):
        """
        Postprocess the edit collection for contraction.
        Update CONTRACTION -> QUESTION TAG

        Args:
            edit_collection (EditCollection): An EditCollection object

        Returns:
            None
        """
        QUESTION_TAG_AUXES = {
            "am",
            "is",
            "are",
            "was",
            "were",
            "do",
            "does",
            "did",
            "have",
            "has",
            "had",
            "can",
            "could",
            "will",
            "would",
            "shall",
            "should",
            "may",
            "might",
            "must",
            "ought",
            # ",",  # punctuation is also considered as an auxiliary verb in question tags
            "isn't",
            "aren't",
            "wasn't",
            "weren't",
            "don't",
            "doesn't",
            "didn't",
            "haven't",
            "hasn't",
            "hadn't",
            "can't",
            "couldn't",
            "won't",
            "wouldn't",
            "shan't",
            "shouldn't",
            "mayn't",
            "mightn't",
            "mustn't",
            "oughtn't",
        }

        QUESTION_TAG_PRONOUN = {
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "myself",
            "yourself",
            "himself",
            "herself",
            "itself",
            "ourselves",
            "yourselves",
            "themselves",
        }

        # question have pattern
        # aux[not] + proun + ?/EOF
        for edit in edit_collection.edits:
            if edit.is_space:
                continue

            parent_error = edit.edit_type.split(":")[1]
            orig_text = edit.original.text.strip().lower()
            corr_text = edit.corrected.text.strip().lower()
            orig_start_char = edit.original.start_char
            orig_end_char = edit.original.end_char
            corr_start_char = edit.corrected.start_char
            corr_end_char = edit.corrected.end_char

            if parent_error == ParentErrorType.CONTRACTION:  # For mising and unnecessary contractions
                try:
                    orig_next_start, orig_next_end = self.__find_next_token_span(
                        orig_start_char, orig_end_char, edit_collection.orig_doc.text
                    )
                    orig_prev_start, orig_prev_end = self.__find_prev_token_span(
                        orig_start_char, edit_collection.orig_doc.text
                    )
                    corr_next_start, corr_next_end = self.__find_next_token_span(
                        corr_start_char, corr_end_char, edit_collection.cor_doc.text
                    )
                    corr_prev_start, corr_prev_end = self.__find_prev_token_span(
                        corr_start_char, edit_collection.cor_doc.text
                    )
                except:
                    # if we cannot find the next or previous token, skip this edit
                    continue
                # check if the next token is a pronoun
                if (
                    edit_collection.orig_doc.text[orig_next_start:orig_next_end].lower() in QUESTION_TAG_PRONOUN
                    and edit_collection.orig_doc.text[orig_prev_start:orig_prev_end].lower() in QUESTION_TAG_AUXES
                    and edit_collection.cor_doc.text[corr_next_start:corr_next_end].lower() in QUESTION_TAG_PRONOUN
                    and edit_collection.cor_doc.text[corr_prev_start:corr_prev_end].lower() in QUESTION_TAG_AUXES
                ):
                    # if so, change the edit type to QUESTION_TAG
                    edit.edit_type = edit.edit_type[:2] + ParentErrorType.QUESTION_TAG

            elif orig_text.lower() in QUESTION_TAG_AUXES or corr_text.lower() in QUESTION_TAG_AUXES:  # For wrong auxiliary verbs in question tags
                try:
                    orig_first_next_start, orig_first_next_end = self.__find_next_token_span(
                        orig_start_char,
                        orig_end_char,
                        edit_collection.orig_doc.text,
                        order=1,
                    )
                    orig_second_next_start, orig_second_next_end = self.__find_next_token_span(
                        orig_start_char,
                        orig_end_char,
                        edit_collection.orig_doc.text,
                        order=2,
                    )

                    corr_first_next_start, corr_first_next_end = self.__find_next_token_span(
                        corr_start_char,
                        corr_end_char,
                        edit_collection.cor_doc.text,
                        order=1,
                    )
                    corr_second_next_start, corr_second_next_end = self.__find_next_token_span(
                        corr_start_char,
                        corr_end_char,
                        edit_collection.cor_doc.text,
                        order=2,
                    )
                except:
                    # if we cannot find the next or previous token, skip this edit
                    continue

                if (
                    edit_collection.orig_doc.text[orig_first_next_start:orig_first_next_end].lower()
                    in QUESTION_TAG_PRONOUN
                    or (
                        edit_collection.orig_doc.text[orig_first_next_start:orig_first_next_end].lower()
                        in ["not", "n't"]
                        and edit_collection.orig_doc.text[orig_second_next_start:orig_second_next_end].lower()
                        in QUESTION_TAG_PRONOUN
                    )
                ) and (
                    edit_collection.cor_doc.text[corr_first_next_start:corr_first_next_end].lower()
                    in QUESTION_TAG_PRONOUN
                    or (
                        edit_collection.cor_doc.text[corr_first_next_start:corr_first_next_end].lower()
                        in ["not", "n't"]
                        and edit_collection.cor_doc.text[corr_second_next_start:corr_second_next_end].lower()
                        in QUESTION_TAG_PRONOUN
                    )
                ):
                    # if so, change the edit type to QUESTION_TAG
                    edit.edit_type = edit.edit_type[:2] + ParentErrorType.QUESTION_TAG

            elif parent_error == ParentErrorType.PRONOUN:  # For wrong pronouns in question tags
                try:
                    orig_first_prev_start, orig_first_prev_end = self.__find_prev_token_span(
                        orig_start_char, edit_collection.orig_doc.text, order=1
                    )
                    orig_second_prev_start, orig_second_prev_end = self.__find_prev_token_span(
                        orig_start_char, edit_collection.orig_doc.text, order=2
                    )
                    corr_first_prev_start, corr_first_prev_end = self.__find_prev_token_span(
                        corr_start_char, edit_collection.cor_doc.text, order=1
                    )
                    corr_second_prev_start, corr_second_prev_end = self.__find_prev_token_span(
                        corr_start_char, edit_collection.cor_doc.text, order=2
                    )
                except:
                    # if we cannot find the next or previous token, skip this edit
                    continue
                if (
                    edit_collection.orig_doc.text[orig_first_prev_start:orig_first_prev_end].lower()
                    in QUESTION_TAG_AUXES
                    or (
                        edit_collection.orig_doc.text[orig_first_prev_start:orig_first_prev_end].lower()
                        in ["not", "n't"]
                        and edit_collection.orig_doc.text[orig_second_prev_start:orig_second_prev_end].lower()
                        in QUESTION_TAG_AUXES
                    )
                ) and (
                    edit_collection.cor_doc.text[corr_first_prev_start:corr_first_prev_end].lower()
                    in QUESTION_TAG_AUXES
                    or (
                        edit_collection.cor_doc.text[corr_first_prev_start:corr_first_prev_end].lower()
                        in ["not", "n't"]
                        and edit_collection.cor_doc.text[corr_second_prev_start:corr_second_prev_end].lower()
                        in QUESTION_TAG_AUXES
                    )
                ):
                    # if so, change the edit type to QUESTION_TAG
                    edit.edit_type = edit.edit_type[:2] + ParentErrorType.QUESTION_TAG
