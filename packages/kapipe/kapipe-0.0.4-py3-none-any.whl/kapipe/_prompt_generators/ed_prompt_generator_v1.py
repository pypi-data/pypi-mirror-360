import logging
import os
# import random

from .. import utils


logger = logging.getLogger(__name__)


class EDPromptGeneratorV1:

    def __init__(
        self,
        prompt_template_name_or_path,
        knowledge_base_name_prompt,
        path_entity_dict,
        path_demonstration_pool,
        path_candidate_entities_pool,
        verbose=True
    ):
        """
        Parameters
        ----------
        prompt_template_name : str
        knowledge_base_name_prompt: str
        path_entity_dict : str
        path_demonstration_pool : str
        path_candidate_entities_pool : str
        verbose : bool
            by default True
        """
        self.prompt_template_name_or_path = prompt_template_name_or_path
        self.knowledge_base_name_prompt = knowledge_base_name_prompt
        self.path_entity_dict = path_entity_dict
        self.path_demonstration_pool = path_demonstration_pool
        self.path_candidate_entities_pool = path_candidate_entities_pool
        self.verbose = verbose

        ###########
        # Prompt template
        ###########

        path_prompt_templates_dir = os.path.join(
            os.path.dirname(__file__),
            "prompt_templates"
        )
        prompt_template_names = os.listdir(path_prompt_templates_dir)
        prompt_template_names = [
            os.path.splitext(name)[0] for name in prompt_template_names
        ]
        if self.prompt_template_name_or_path in prompt_template_names:
            with open(os.path.join(
                path_prompt_templates_dir,
                self.prompt_template_name_or_path + ".txt"
            )) as f:
                self.prompt_template = f.read()
        else:
            with open(self.prompt_template_name_or_path) as f:
                self.prompt_template = f.read()
        assert "{knowledge_base_name_prompt}" in self.prompt_template
        assert "{demonstrations_prompt}" in self.prompt_template
        assert "{test_prompt}" in self.prompt_template

        ###########
        # Entity Dict
        ###########

        # dict[str, EntityPage]
        self.entity_dict = {
            epage["entity_id"]: epage
            for epage in utils.read_json(path_entity_dict)
        }
        if self.verbose:
            logger.info(f"Loaded entity dictionary from {path_entity_dict}")

        ###########
        # Demonstrations
        ###########

        # dict[DocKey, Document]
        self.demonstration_pool = {
            demo_doc["doc_key"]: demo_doc
            for demo_doc in utils.read_json(path_demonstration_pool)
        }
        if self.verbose:
            logger.info(f"Loaded demonstration pool from {path_demonstration_pool}")

        # dict[DocKey, dict[str, str | list[list[CandEntKeyInfo]]]]
        self.candidate_entities_pool = {
            cands["doc_key"]: cands
            for cands in utils.read_json(path_candidate_entities_pool)
        }
        if self.verbose:
            logger.info(f"Loaded candidate entities for demonstration pool from {path_candidate_entities_pool}")

    def generate(
        self,
        document,
        candidate_entity_dicts_for_doc,
        demonstrations_for_doc,
        candidate_entity_dicts_for_demos,
        n_demos
    ):
        """
        Parameters
        ----------
        document : Document
        candidate_entity_dicts_for_doc: list[list[EntityPage]]
            shape of (n_mentions, n_candidates)
        demonstration_documents : list[Document]
            shape of (n_demos,)
        candidate_entity_dicts_for_demos: list[list[list[EntityPage]]]
            shape of (n_demos, n_mentions, n_candidates)

        Returns
        -------
        str
        """
        demonstrations_prompt = self.generate_demonstrations_prompt(
            demonstration_documents=demonstration_documents,
            candidate_entity_dicts_for_demos=candidate_entity_dicts_for_demos
        )
        test_prompt = self.generate_test_prompt(
            document=document,
            candidate_entity_dicts_for_doc=candidate_entity_dicts_for_doc
        )
        prompt = self.prompt_template.format(
            knowledge_base_name_prompt=self.knowledge_base_name_prompt,
            demonstrations_prompt=demonstrations_prompt,
            test_prompt=test_prompt
        )
        return prompt

    #####
    # Subfunctions for encoding
    #####

    def generate_demonstrations_prompt(
        self,
        demonstration_documents,
        candidate_entity_dicts_for_demos
    ):
        """
        Parameters
        ----------
        demonstration_documents: list[Document]
            shape of (n_demos,)
        candidate_entity_dicts_for_demos: list[list[list[EntityPage]]]
            shape of (n_demos, n_mentions, n_candidates)

        Returns
        -------
        str
        """
        text = ""
        n_demos = len(demonstration_documents)
        for demo_i, (demo_doc, cand_ent_dicts_for_demo) in enumerate(
            zip(
                demonstration_documents,
                candidate_entity_dicts_for_demos
            )
        ):
            text += f"# Example {demo_i+1}\n"
            text += (
                "Text: "
                + self.generate_input_prompt(document=demo_doc)
                + "\n"
            )
            mentions_text, selected_mention_indices = \
                self.generate_mentions_prompt(document=demo_doc, demo=True)
            text += (
                "Mentions:\n"
                + mentions_text
                + "\n"
            )
            text += (
                "Concept IDs (candidates):\n"
                + self.generate_candidate_entities_prompt(
                    candidate_entity_dicts_for_doc=cand_ent_dicts_for_demo,
                    selected_mention_indices=selected_mention_indices
                )
                + "\n"
            )
            text += (
                "Answer:\n"
                + self.generate_output_prompt(
                    document=demo_doc,
                    selected_mention_indices=selected_mention_indices
                )
                + "\n"
            )
            if demo_i < n_demos - 1:
                text += "\n"
        return text.rstrip()

    def generate_test_prompt(
        self,
        document,
        candidate_entity_dicts_for_doc
    ):
        """
        Parameters
        ----------
        document : Document
        candidate_entity_dicts_for_doc : list[list[EntityPage]]
            shape of (n_mentions, n_candidates)

        Returns
        -------
        str
        """
        text = ""
        text += "# Test Example\n"
        text += (
            "Text: "
            + self.generate_input_prompt(document=document)
            + "\n"
        )
        mentions_text, selected_mention_indices = \
            self.generate_mentions_prompt(document=document)
        text += (
            "Mentions:\n"
            + mentions_text
            + "\n"
        )
        text += (
            "Concept IDs (candidates):\n"
            + self.generate_candidate_entities_prompt(
                candidate_entity_dicts_for_doc=candidate_entity_dicts_for_doc,
                selected_mention_indices=selected_mention_indices
            )
        )
        return text.rstrip()

    def generate_input_prompt(self, document):
        """
        Parameters
        ----------
        document : Document

        Returns
        -------
        str
        """
        text = " ".join(document["sentences"]) + "\n"
        return text.rstrip()

    def generate_mentions_prompt(self, document, demo=False):
        """
        Parameters
        ----------
        document : Document
        demo : bool
            by default False

        Returns
        -------
        tuple[str, list[int]]
        """
        text = ""
        words = " ".join(document["sentences"]).split()
        names = []
        selected_mention_indices = []
        for m_i, mention in enumerate(document["mentions"]):
            begin_i, end_i = mention["span"]
            name = " ".join(words[begin_i: end_i + 1])
            if name in names:
                continue
            names.append(name)
            selected_mention_indices.append(m_i)
            # In the demonstrations, we skip some mentions
            if demo and len(names) >= 3:
                break
        for n_i, name in enumerate(names):
            text += f"{n_i + 1}. {name}\n"
        return text.rstrip(), selected_mention_indices

    def generate_candidate_entities_prompt(
        self,
        candidate_entity_dicts_for_doc,
        selected_mention_indices=None
    ):
        """
        Parameters
        ----------
        candidate_entity_dicts_for_doc : list[list[EntityPage]]
        selected_mention_indices : list[int] | None
            by default None

        Returns
        -------
        str
        """
        N_CAND = 3
        # Aggregate candidates as a single list
        candidates = []
        memorized_ids = set()
        for m_i, candidate_entity_dicts_for_one_mention in (
            enumerate(candidate_entity_dicts_for_doc)
        ):
            if (
                (selected_mention_indices is not None)
                and
                (not m_i in selected_mention_indices)
            ):
                continue
            for cand_dict in candidate_entity_dicts_for_one_mention[:N_CAND]:
                if not cand_dict["entity_id"] in memorized_ids:
                    candidates.append(cand_dict)
                    memorized_ids.add(cand_dict["entity_id"])
        # Transform the candidate list into text
        text = ""
        for cand_dict in candidates:
            entity_id = cand_dict["entity_id"]
            canonical_name = cand_dict["canonical_name"]
            # desc = cand_dict["description"]
            text += f"* {entity_id}: {canonical_name}\n"
        return text.rstrip()

    def generate_output_prompt(self, document, selected_mention_indices=None):
        """
        Parameters
        ----------
        document : Document
        selected_mention_indices : list[int] | None
            by default NOne

        Returns
        -------
        str
        """
        text = ""
        words = " ".join(document["sentences"]).split()
        for m_i, mention in enumerate(document["mentions"]):
            if (
                (selected_mention_indices is not None)
                and
                (not m_i in selected_mention_indices)
            ):
                continue
            begin_i, end_i = mention["span"]
            name = " ".join(words[begin_i : end_i + 1])
            entity_id = mention["entity_id"]
            text += f"{m_i+1}. {name} -> {entity_id}\n"
        return text.rstrip()

    #####
    # Decoding
    #####

