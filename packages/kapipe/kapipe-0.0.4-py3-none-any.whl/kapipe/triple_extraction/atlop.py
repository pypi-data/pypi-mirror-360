import copy
import logging
import os

import numpy as np
import torch
# import torch.nn as nn
from tqdm import tqdm
import jsonlines

from .  import shared_functions
from ..models import ATLOPModel
from .. import evaluation
from .. import utils
from ..utils import BestScoreHolder


logger = logging.getLogger(__name__)


class ATLOP:
    """ATLOP (Zhou et al., 2021).
    """

    def __init__(
        self,
        # General
        device,
        config,
        # Task specific
        vocab_relation,
        # Misc.
        path_model=None,
        verbose=True
    ):
        """
        Parameters
        ----------
        device: str
        config: ConfigTree | str
        vocab_relation: dict[str, int] | str
        path_model: str | None
            by default None
        verbose: bool | None
            by default True
        """
        self.verbose = verbose
        if self.verbose:
            logger.info(">>>>>>>>>> ATLOP Initialization >>>>>>>>>>")
        self.device = device

        ######
        # Config
        ######

        if isinstance(config, str):
            tmp = config
            config = utils.get_hocon_config(
                config_path=config,
                config_name=None
            )
            if self.verbose:
                logger.info(f"Loaded configuration from {tmp}")
        self.config = config
        if self.verbose:
            logger.info(utils.pretty_format_dict(self.config))

        ######
        # Vocabulary (relations)
        ######

        if isinstance(vocab_relation, str):
            tmp = vocab_relation
            vocab_relation = utils.read_vocab(vocab_relation)
            if self.verbose:
                logger.info(f"Loaded relation type vocabulary from {tmp}")
        self.vocab_relation = vocab_relation
        self.ivocab_relation = {i:l for l, i in self.vocab_relation.items()}

        ######
        # Model
        ######

        self.model_name = config["model_name"]
        self.top_k_labels = config["top_k_labels"]
        if self.model_name == "atlopmodel":
            self.model = ATLOPModel(
                device=device,
                bert_pretrained_name_or_path=config[
                    "bert_pretrained_name_or_path"
                ],
                max_seg_len=config["max_seg_len"],
                token_embedding_method=config["token_embedding_method"],
                entity_pooling_method=config["entity_pooling_method"],
                use_localized_context_pooling=config[
                    "use_localized_context_pooling"
                ],
                bilinear_block_size=config["bilinear_block_size"],
                vocab_relation=self.vocab_relation,
                loss_function_name=config["loss_function"],
                possible_head_entity_types=config["possible_head_entity_types"],
                possible_tail_entity_types=config["possible_tail_entity_types"]
            )
        else:
            raise Exception(f"Invalid model_name: {self.model_name}")

        # Show parameter shapes
        # logger.info("Model parameters:")
        # for name, param in self.model.named_parameters():
        #     logger.info(f"{name}: {tuple(param.shape)}")

        # Load trained model parameters
        if path_model is not None:
            self.load_model(path=path_model)
            if self.verbose:
                logger.info(f"Loaded model parameters from {path_model}")

        self.model.to(self.model.device)

        if self.verbose:
            logger.info("<<<<<<<<<< ATLOP Initialization <<<<<<<<<<")

    def load_model(self, path):
        """
        Parameters
        ----------
        path : str
        """
        self.model.load_state_dict(
            torch.load(path, map_location=torch.device("cpu")),
            strict=False
        )

    def save_model(self, path):
        """
        Parameters
        ----------
        path : str
        """
        torch.save(self.model.state_dict(), path)

    # ---

    def compute_loss(self, document):
        """
        Parameters
        ----------
        document : Document

        Returns
        -------
        tuple[torch.Tensor, torch.Tensor, int, int]
        """
        # Switch to training mode
        self.model.train()

        # Preprocess
        preprocessed_data = self.model.preprocess(document=document)

        # Tensorize
        model_input = self.model.tensorize(
            preprocessed_data=preprocessed_data,
            compute_loss=True
        )

        # Forward
        model_output = self.model.forward(**model_input)

        return (
            model_output.loss,
            model_output.acc,
            model_output.n_valid_pairs,
            model_output.n_valid_triples
        )

    def extract(self, document):
        """
        Parameters
        ----------
        document : Document

        Returns
        -------
        Document
        """
        with torch.no_grad():
            # Switch to inference mode
            self.model.eval()

            # Preprocess
            preprocessed_data = self.model.preprocess(document=document)
            if (
                len(preprocessed_data["pair_head_entity_indices"]) == 0
                or
                len(preprocessed_data["pair_tail_entity_indices"]) == 0
            ):
                result_document = copy.deepcopy(document)
                result_document["relations"] = []
                return result_document

            # Tensorize
            model_input = self.model.tensorize(
                preprocessed_data=preprocessed_data,
                compute_loss=False
            )

            # Forward
            model_output = self.model.forward(**model_input)
            # (n_entity_pairs, n_relations)
            logits = model_output.logits

            # Structurize
            triples = self.structurize(
                pair_head_entity_indices=preprocessed_data["pair_head_entity_indices"],
                pair_tail_entity_indices=preprocessed_data["pair_tail_entity_indices"],
                logits=logits
            )

            # Integrate
            result_document = copy.deepcopy(document)
            result_document["relations"] = triples
            return result_document

    def structurize(
        self,
        pair_head_entity_indices,
        pair_tail_entity_indices,
        logits
    ):
        triples = [] # list[Triple]

        # (n_entity_pairs, n_relations)
        pair_pred_relation_labels = self.model.loss_function.get_labels(
            logits=logits,
            top_k=self.top_k_labels
        ).cpu().numpy()

        for head_entity_i, tail_entity_i, rel_indicators in zip(
            pair_head_entity_indices,
            pair_tail_entity_indices,
            pair_pred_relation_labels
        ):
            assert head_entity_i != tail_entity_i
            # Find non-zero relation IDs (indices)
            rel_indices = np.nonzero(rel_indicators)[0].tolist()
            for rel_i in rel_indices:
                if rel_i != 0:
                    rel = self.ivocab_relation[rel_i]
                    triples.append({
                        "arg1": int(head_entity_i),
                        "relation": rel,
                        "arg2": int(tail_entity_i),
                        })

        return triples

    def batch_extract(self, documents):
        """
        Parameters
        ----------
        documents : list[Document]

        Returns
        -------
        list[Document]
        """
        result_documents = []
        for document in tqdm(documents, desc="extraction steps"):
            result_document = self.extract(
                document=document
            )
            result_documents.append(result_document)
        return result_documents


class ATLOPTrainer:

    def __init__(self, base_output_path):
        """
        Parameters
        ----------
        base_output_path : str
        """
        self.base_output_path = base_output_path
        self.paths = self.get_paths()

    def get_paths(self):
        """
        Returns
        -------
        dict[str, str]
        """
        paths = {}

        # Path to config file
        paths["path_config"] = self.base_output_path + "/config"
        # Path to vocabulary
        paths["path_vocab_relation"] = self.base_output_path + "/relations.vocab.txt"
        # Path to model snapshot
        paths["path_snapshot"] = self.base_output_path + "/model"

        # Path to gold training triples for Ign evaluation
        paths["path_gold_train_triples"] = self.base_output_path + "/gold_train_triples.json"

        # Paths to training-losses and validation-scores files
        paths["path_train_losses"] = self.base_output_path + "/train.losses.jsonl"
        paths["path_dev_evals"] = self.base_output_path + "/dev.eval.jsonl"

        # Paths to validation outputs and scores
        paths["path_dev_gold"] = self.base_output_path + "/dev.gold.json"
        paths["path_dev_pred"] = self.base_output_path + "/dev.pred.json"
        paths["path_dev_eval"] = self.base_output_path + "/dev.eval.json"

        # Paths to evaluation outputs and scores
        paths["path_test_gold"] = self.base_output_path + "/test.gold.json"
        paths["path_test_pred"] = self.base_output_path + "/test.pred.json"
        paths["path_test_eval"] = self.base_output_path + "/test.eval.json"

        return paths

    def setup_dataset(
        self,
        extractor,
        documents,
        split,
        with_gold_annotations=True
    ):
        """
        Parameters
        ----------
        extractor : ATLOP
        documents : list[Document]
        split : str
        with_gold_annotations : bool
            by default True
        """
        if split == "train":
            # Cache the gold training triples for Ign evaluation
            if not os.path.exists(self.paths["path_gold_train_triples"]):
                gold_train_triples = []
                for document in tqdm(documents, desc="dataset setup"):
                    mentions = document["mentions"]
                    entity_index_to_mention_names = {
                        e_i: [
                            mentions[m_i]["name"]
                            for m_i in e["mention_indices"]
                        ]
                        for e_i, e in enumerate(document["entities"])
                    }
                    for triple in document["relations"]:
                        arg1_entity_i = triple["arg1"]
                        rel = triple["relation"]
                        arg2_entity_i = triple["arg2"]
                        arg1_mention_names \
                            = entity_index_to_mention_names[arg1_entity_i]
                        arg2_mention_names \
                            = entity_index_to_mention_names[arg2_entity_i]
                        for arg1_mention_name in arg1_mention_names:
                            for arg2_mention_name in arg2_mention_names:
                                gold_train_triples.append((
                                    arg1_mention_name,
                                    rel,
                                    arg2_mention_name
                                ))
                gold_train_triples = list(set(gold_train_triples))
                gold_train_triples = {"root": gold_train_triples}
                utils.write_json(
                    self.paths["path_gold_train_triples"],
                    gold_train_triples
                )
                logger.info(f"Saved the gold training triples for Ign evaluation in {self.paths['path_gold_train_triples']}")

        # Cache the gold annotations for evaluation
        if split != "train" and with_gold_annotations:
            path_gold = self.paths[f"path_{split}_gold"]
            if not os.path.exists(path_gold):
                gold_documents = []
                for document in tqdm(documents, desc="dataset setup"):
                    gold_doc = copy.deepcopy(document)
                    gold_doc["intra_inter_map"] \
                        = shared_functions.create_intra_inter_map(
                            document=document
                        )
                    gold_documents.append(gold_doc)
                utils.write_json(path_gold, gold_documents)
                logger.info(f"Saved the gold annotations for evaluation in {path_gold}")

    def train(
        self,
        extractor,
        train_documents,
        dev_documents,
        supplemental_info
    ):
        """
        Parameters
        ----------
        extractor : ATLOP
        train_documents : list[Document]
        dev_documents : list[Document]
        supplemental_info : dict[str, Any]
        """
        train_doc_indices = np.arange(len(train_documents))

        ##################
        # Get optimizer and scheduler
        ##################

        n_train = len(train_doc_indices)
        max_epoch = extractor.config["max_epoch"]
        batch_size = extractor.config["batch_size"]
        gradient_accumulation_steps \
            = extractor.config["gradient_accumulation_steps"]
        total_update_steps \
            = n_train * max_epoch // (batch_size * gradient_accumulation_steps)
        warmup_steps = int(total_update_steps * extractor.config["warmup_ratio"])

        logger.info("Number of training documents: %d" % n_train)
        logger.info("Number of epochs: %d" % max_epoch)
        logger.info("Batch size: %d" % batch_size)
        logger.info("Gradient accumulation steps: %d" % gradient_accumulation_steps)
        logger.info("Total update steps: %d" % total_update_steps)
        logger.info("Warmup steps: %d" % warmup_steps)

        optimizer = shared_functions.get_optimizer2(
            model=extractor.model,
            config=extractor.config
        )
        # extractor.model, optimizer = amp.initialize(
        #     extractor.model,
        #     optimizer,
        #     opt_level="O1",
        #     verbosity=0
        # )
        scheduler = shared_functions.get_scheduler2(
            optimizer=optimizer,
            total_update_steps=total_update_steps,
            warmup_steps=warmup_steps
        )

        ##################
        # Get reporter and best score holder
        ##################

        writer_train = jsonlines.Writer(
            open(self.paths["path_train_losses"], "w"),
            flush=True
        )
        writer_dev = jsonlines.Writer(
            open(self.paths["path_dev_evals"], "w"),
            flush=True
        )
        bestscore_holder = BestScoreHolder(scale=1.0)
        bestscore_holder.init()

        ##################
        # Evaluate
        ##################

        if extractor.config["use_official_evaluation"]:
            scores = self.official_evaluate(
                extractor=extractor,
                documents=dev_documents,
                split="dev",
                supplemental_info=supplemental_info,
                #
                get_scores_only=True
            )
        else:
            scores = self.evaluate(
                extractor=extractor,
                documents=dev_documents,
                split="dev",
                supplemental_info=supplemental_info,
                #
                skip_intra_inter=True,
                skip_ign=True,
                get_scores_only=True
            )
        scores["epoch"] = 0
        scores["step"] = 0
        writer_dev.write(scores)
        logger.info(utils.pretty_format_dict(scores))

        bestscore_holder.compare_scores(scores["standard"]["f1"], 0)

        ##################
        # Save
        ##################

        # Save the model
        extractor.save_model(path=self.paths["path_snapshot"])
        logger.info("Saved model to %s" % self.paths["path_snapshot"])

        # Save the config (only once)
        # utils.dump_hocon_config(self.paths["path_config"], extractor.config)
        utils.write_json(self.paths["path_config"], extractor.config)
        logger.info("Saved config file to %s" % self.paths["path_config"])

        # Save the vocabulary (only once)
        utils.write_vocab(
            self.paths["path_vocab_relation"],
            extractor.vocab_relation,
            write_frequency=False
        )
        logger.info("Saved relation type vocabulary to %s" % self.paths["path_vocab_relation"])

        ##################
        # Training-and-validation loops
        ##################

        bert_param, task_param = extractor.model.get_params()
        extractor.model.zero_grad()
        step = 0
        batch_i = 0

        # Variables for reporting
        loss_accum = 0.0
        acc_accum = 0.0
        accum_count = 0

        progress_bar = tqdm(total=total_update_steps, desc="training steps")
        for epoch in range(1, max_epoch + 1):

            perm = np.random.permutation(n_train)

            for instance_i in range(0, n_train, batch_size):

                ##################
                # Forward pass
                ##################

                batch_i += 1

                # Initialize loss
                batch_loss = 0.0
                batch_acc = 0.0
                actual_batchsize = 0
                actual_total_pairs = 0
                actual_total_triples = 0

                for doc_i in train_doc_indices[
                    perm[instance_i : instance_i + batch_size]
                ]:

                    # Forward and compute loss
                    (
                        one_loss,
                        one_acc,
                        n_valid_pairs,
                        n_valid_triples
                    ) = extractor.compute_loss(document=train_documents[doc_i])

                    # Accumulate the loss
                    batch_loss = batch_loss + one_loss
                    batch_acc += one_acc
                    actual_batchsize += 1
                    actual_total_pairs += n_valid_pairs
                    actual_total_triples += n_valid_triples

                # Average the loss
                actual_batchsize = float(actual_batchsize)
                actual_total_pairs = float(actual_total_pairs)
                actual_total_triples = float(actual_total_triples)
                batch_loss = batch_loss / actual_total_pairs # loss per pair
                batch_acc = batch_acc / actual_total_triples

                ##################
                # Backward
                ##################

                batch_loss = batch_loss / gradient_accumulation_steps
                batch_loss.backward()
                # with amp.scale_loss(batch_loss, optimizer) as scaled_loss:
                #     scaled_loss.backward()

                # Accumulate for reporting
                loss_accum += float(batch_loss.cpu())
                acc_accum += batch_acc
                accum_count += 1

                if batch_i % gradient_accumulation_steps == 0:

                    ##################
                    # Update
                    ##################

                    if extractor.config["max_grad_norm"] > 0:
                        torch.nn.utils.clip_grad_norm_(
                            bert_param,
                            extractor.config["max_grad_norm"]
                        )
                        torch.nn.utils.clip_grad_norm_(
                            task_param,
                            extractor.config["max_grad_norm"]
                        )
                        # torch.nn.utils.clip_grad_norm_(
                        #     amp.master_params(optimizer),
                        #     extractor.config["max_grad_norm"]
                        # )
                    optimizer.step()
                    scheduler.step()

                    extractor.model.zero_grad()
                    step += 1
                    progress_bar.update()
                    progress_bar.refresh()

                # Report
                if (
                    (instance_i + batch_size >= n_train)
                    or
                    (
                        (batch_i % gradient_accumulation_steps == 0)
                        and
                        (step % extractor.config["n_steps_for_monitoring"] == 0)
                    )
                ):

                    ##################
                    # Rerpot
                    ##################

                    out = {
                        "step": step,
                        "epoch": epoch,
                        "step_progress": "%d/%d" % (step, total_update_steps),
                        "step_progress(ratio)": \
                            float(step) / total_update_steps * 100.0,
                        "one_epoch_progress": \
                            "%d/%d" % (instance_i + actual_batchsize, n_train),
                        "one_epoch_progress(ratio)": (
                            float(instance_i + actual_batchsize)
                            / n_train
                            * 100.0
                        ),
                        "loss": loss_accum / accum_count,
                        "accuracy": 100.0 * acc_accum / accum_count,
                        "max_valid_f1": bestscore_holder.best_score,
                        "patience": bestscore_holder.patience
                    }
                    writer_train.write(out)
                    logger.info(utils.pretty_format_dict(out))
                    loss_accum = 0.0
                    acc_accum = 0.0
                    accum_count = 0

                if (
                    (instance_i + batch_size >= n_train)
                    or
                    (
                        (batch_i % gradient_accumulation_steps == 0)
                        and
                        (extractor.config["n_steps_for_validation"] > 0)
                        and
                        (step % extractor.config["n_steps_for_validation"] == 0)
                    )
                ):

                    ##################
                    # Evaluate
                    ##################

                    if extractor.config["use_official_evaluation"]:
                        scores = self.official_evaluate(
                            extractor=extractor,
                            documents=dev_documents,
                            split="dev",
                            supplemental_info=supplemental_info,
                            #
                            get_scores_only=True
                        )
                    else:
                        scores = self.evaluate(
                            extractor=extractor,
                            documents=dev_documents,
                            split="dev",
                            supplemental_info=supplemental_info,
                            #
                            skip_intra_inter=True,
                            skip_ign=True,
                            get_scores_only=True
                        )
                    scores["epoch"] = epoch
                    scores["step"] = step
                    writer_dev.write(scores)
                    logger.info(utils.pretty_format_dict(scores))

                    did_update = bestscore_holder.compare_scores(
                        scores["standard"]["f1"],
                        epoch
                    )
                    logger.info("[Step %d] Max validation F1: %f" % (step, bestscore_holder.best_score))

                    ##################
                    # Save
                    ##################

                    # Save the model?
                    if did_update:
                        extractor.save_model(path=self.paths["path_snapshot"])
                        logger.info("Saved model to %s" % self.paths["path_snapshot"])

                    if (
                        bestscore_holder.patience
                        >= extractor.config["max_patience"]
                    ):
                        writer_train.close()
                        writer_dev.close()
                        progress_bar.close()
                        return

        writer_train.close()
        writer_dev.close()
        progress_bar.close()

    def evaluate(
        self,
        extractor,
        documents,
        split,
        supplemental_info,
        #
        skip_intra_inter=False,
        skip_ign=False,
        prediction_only=False,
        get_scores_only=False
    ):
        """
        Parameters
        ----------
        extractor : ATLOP
        documents : list[Document]
        split : str
        supplemental_info : dict[str, Any]
        skip_intra_inter : bool, by default False
        skip_ign : bool, by default False
        prediction_only : bool, by default False
        get_scores_only : bool, by default False

        Returns
        -------
        dict[str, Any] | None
        """
        # documents -> path_pred
        result_documents = extractor.batch_extract(documents=documents)
        utils.write_json(self.paths[f"path_{split}_pred"], result_documents)
        if prediction_only:
            return
        # (path_pred, path_gold) -> scores
        scores = evaluation.docre.fscore(
            pred_path=self.paths[f"path_{split}_pred"],
            gold_path=self.paths[f"path_{split}_gold"],
            skip_intra_inter=skip_intra_inter,
            skip_ign=skip_ign,
            gold_train_triples_path=self.paths["path_gold_train_triples"]
        )
        if get_scores_only:
            return scores
        # scores -> path_eval
        utils.write_json(self.paths[f"path_{split}_eval"], scores)
        logger.info(utils.pretty_format_dict(scores))
        return scores

    def official_evaluate(
        self,
        extractor,
        documents,
        split,
        supplemental_info,
        #
        prediction_only=False,
        get_scores_only=False
    ):
        """
        Parameters
        ----------
        extractor : ATLOP
        documents : list[Document]
        split : str
        supplemental_info : dict[str, Any]
        prediction_only : bool
            by default False
        get_scores_only : bool
            by default False

        Returns
        -------
        dict[str, Any] | None
        """
        # NOTE: prediction_only is assumed to be used for the DocRED test set
        # documents -> path_pred
        result_documents = extractor.batch_extract(documents=documents)
        utils.write_json(self.paths[f"path_{split}_pred"], result_documents)
        # path_pred -> triples (path_pred variant)
        triples = evaluation.docre.to_official(
            path_input=self.paths[f"path_{split}_pred"],
            path_output=self.paths[
                f"path_{split}_pred"
            ].replace(".json", ".official.json")
        )
        if prediction_only:
            return
        # gold info
        original_data_dir = supplemental_info["original_data_dir"]
        train_file_name = supplemental_info["train_file_name"]
        dev_file_name = supplemental_info[f"{split}_file_name"]
        # (triples, gold info) -> scores
        scores = evaluation.docre.official_evaluate(
            triples=triples,
            original_data_dir=original_data_dir,
            train_file_name=train_file_name,
            dev_file_name=dev_file_name
        )
        if get_scores_only:
            return scores
        # scores -> path_eval
        utils.write_json(self.paths[f"path_{split}_eval"], scores)
        logger.info(utils.pretty_format_dict(scores))
        return scores
