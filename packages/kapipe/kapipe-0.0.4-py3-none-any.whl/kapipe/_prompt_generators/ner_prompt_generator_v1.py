import logging
import os

from .. import utils

logger = logging.getLogger(__name__)


class NERPromptGeneratorV1:

    def __init__(
        self,
        prompt_template_name_or_path,
        possible_entity_types,
        demonstration_documents,
        verbose=True
    ):
        """
        Parameters
        ----------
        prompt_template_name : str
        possible_entity_types : list[str]
        demonstration_documents,
        verbose : bool
            by default True
        """
        self.prompt_template_name_or_path = prompt_template_name_or_path
        self.possible_entity_types = possible_entity_types
        self.demonstration_documents = demonstration_documents
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
        assert "{entity_types_prompt}" in self.prompt_template
        assert "{demonstrations_prompt}" in self.prompt_template
        assert "{test_prompt}" in self.prompt_template

        self.entity_types_prompt = ", ".join(self.possible_entity_types)

    def generate(self, document, demonstrations_for_doc, n_demos):
        """
        Parameters
        ----------
        document : Document
        demonstrations_for_doc : dict[str, str|list[DemoKeyInfo]]
        n_demos : int

        Returns
        -------
        str
        """
       
        # Get demonstrations  
        demonstration_documents = [] # list[Document]
        for demo_dict in (
            demonstrations_for_doc["demonstrations"][:n_demos]
        ):
            demo_doc = self.demonstration_pool[demo_dict["doc_key"]]
            demonstration_documents.append(demo_doc)

        # Get prompt part for demonstrations
        demonstrations_prompt = self.generate_demonstrations_prompt(
            demonstration_documents=demonstration_documents
        )

        # Get prompt part for test input
        test_prompt = self.generate_test_prompt(
            document=document
        )

        # Combine the prompt parts
        prompt = self.prompt_template.format(
            entity_types_prompt=self.entity_types_prompt,
            demonstrations_prompt=demonstrations_prompt,
            test_prompt=test_prompt
        )

        return prompt

    def generate_demonstrations_prompt(self, demonstration_documents):
        """
        Parameters
        ----------
        demonstration_documents: list[Document]

        Returns
        -------
        str
        """
        text = ""
        n_demos = len(demonstration_documents)
        for demo_i, demo_doc in enumerate(demonstration_documents):
            text += f"# Example {demo_i+1}\n"
            text += (
                "Text: "
                + self.generate_input_prompt(document=demo_doc)
                + "\n"
            )
            text += (
                "Answer:\n"
                + self.generate_output_prompt(document=demo_doc)
                + "\n"
            )
            if demo_i < n_demos - 1:
                text += "\n"
        return text.rstrip()

    def generate_test_prompt(self, document):
        """
        Parameters
        ----------
        document : Document

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

    def generate_output_prompt(self, document):
        """
        Parameters
        ----------
        document : Document

        Returns
        -------
        str
        """
        text = ""
        words = " ".join(document["sentences"]).split()
        names = []
        entity_types = []
        for m_i, mention in enumerate(document["mentions"]):
            begin_i, end_i = mention["span"]
            name = " ".join(words[begin_i: end_i + 1])
            if name in names:
                continue
            entity_type = mention["entity_type"]
            names.append(name)
            entity_types.append(entity_type)
        for n_i, (name, entity_type) in enumerate(zip(names, entity_types)):
            text += f"{n_i+1}. {name} -> {entity_type}\n"
        return text.rstrip()

