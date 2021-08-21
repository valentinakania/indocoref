import os
import logging

from utils.feature_utils import FeatureUtils, PairFeatureUtils
from utils.file_utils import FileUtils


logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)


def copy_clusters(clusters):
    from copy import deepcopy
    clusters = deepcopy(clusters)
    return clusters


class MultiPassSieve:
    def __init__(self, passage_dir, temp_dir, output_dir):
        filenames = os.listdir(temp_dir)
        self.clusters = {}
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.passage_dir = passage_dir
        self.filenames = filenames
    
    def run(self, log_step=10):
        total_files = len(self.filenames)
        for idx, name in enumerate(self.filenames):
            if (idx + 1) % log_step == 0:
                logger.info("Running MPS %d/%d" % (idx + 1, total_files))
            mentions = FileUtils.read_pickle(self.temp_dir, name)
            sents = FileUtils.read_passage_file(self.passage_dir, name)
            self.clusters = copy_clusters(mentions)
            self.pass_1()
            self.pass_2(sents)
            self.pass_3()
            self.pass_4()
            self.pass_5()
            self.pass_6()
            equivalent_class = self.build_mps_equivalent_class()
            gold_equivalent_class = self.build_gold_equivalent_class(mentions)
            FileUtils.write_mps_result_to_json(self.output_dir, name, equivalent_class)
            FileUtils.write_gold_cluster_to_json(self.output_dir, name, gold_equivalent_class)

    def is_same_cluster(self, mention_a, mention_b):
        return mention_a["cluster"] == mention_b["cluster"]

    def merge_cluster(self, mention_a, mention_b):
        old_cluster = mention_b["cluster"]
        new_cluster = mention_a["cluster"]
        mention_b["cluster"] = new_cluster
        for obj in self.clusters:
            if obj["cluster"] == old_cluster:
                obj["cluster"] = new_cluster

    # Pass 1: Exact string match
    def pass_1(self):
        for antecedent_idx in range(len(self.clusters)):
            c1 = self.clusters[antecedent_idx]
            if FeatureUtils.is_pronoun(c1):
                continue
            for mention_idx in range(antecedent_idx, len(self.clusters)):
                c2 = self.clusters[mention_idx]
                if self.is_same_cluster(c1, c2) or FeatureUtils.is_pronoun(c2):
                    continue
                if PairFeatureUtils.is_exact_match(c1, c2):
                    self.merge_cluster(c1, c2)
    
    # Pass 2: Precise Constructs
    def pass_2(self, sents):
        for antecedent_idx in range(len(self.clusters)):
            c1 = self.clusters[antecedent_idx]
            if FeatureUtils.is_pronoun(c1):
                continue
            for mention_idx in range(antecedent_idx, len(self.clusters)):
                c2 = self.clusters[mention_idx]
                if self.is_same_cluster(c1, c2) or FeatureUtils.is_pronoun(c2):
                    continue
                if PairFeatureUtils.is_appositive(c1, c2, sents) or PairFeatureUtils.is_copulative(c1, c2, sents) or PairFeatureUtils.is_abbreviation(c1, c2):
                    self.merge_cluster(c1, c2)
    
    # Pass 3: Strict Head Match
    def pass_3(self):
        for antecedent_idx in range(len(self.clusters)):
            c1 = self.clusters[antecedent_idx]
            if FeatureUtils.is_pronoun(c1):
                continue
            for mention_idx in range(antecedent_idx, len(self.clusters)):
                c2 = self.clusters[mention_idx]
                if self.is_same_cluster(c1, c2) or FeatureUtils.is_pronoun(c2):
                    continue
                elif PairFeatureUtils.is_demonstrative(c1, c2) or PairFeatureUtils.is_name_shortened(c1, c2):
                    self.merge_cluster(c1, c2)
                    break
                if PairFeatureUtils.is_head_match(c1, c2):
                    self.merge_cluster(c1, c2)
                    break
    
    # Pass 4: Proper Head Match
    def pass_4(self):
        for antecedent_idx in range(len(self.clusters)):
            c1 = self.clusters[antecedent_idx]
            if FeatureUtils.is_pronoun(c1):
                continue
            for mention_idx in range(antecedent_idx, len(self.clusters)):
                c2 = self.clusters[mention_idx]
                if self.is_same_cluster(c1, c2) or FeatureUtils.is_pronoun(c2):
                    continue
                if PairFeatureUtils.is_full_proper_head_match(c1, c2):
                    self.merge_cluster(c1, c2)

    # Pass 5: Relaxed Head Match
    def pass_5(self):
        for antecedent_idx in range(len(self.clusters)):
            c1 = self.clusters[antecedent_idx]
            if FeatureUtils.is_pronoun(c1):
                continue
            for mention_idx in range(antecedent_idx, len(self.clusters)):
                c2 = self.clusters[mention_idx]
                if self.is_same_cluster(c1, c2) or FeatureUtils.is_pronoun(c2):
                    continue
                if PairFeatureUtils.is_relaxed_match(c1, c2):
                    self.merge_cluster(c1, c2)

    # Pass 6: Pronoun
    def pass_6(self):
        candidate_idx = len(self.clusters) - 1
        antecedent_idx = len(self.clusters) - 2
        while candidate_idx > 0 and antecedent_idx >= 0:
            if candidate_idx <= antecedent_idx:
                antecedent_idx = candidate_idx - 1
            elif self.clusters[candidate_idx] == "":
                candidate_idx -= 1
            elif self.clusters[antecedent_idx] == "":
                antecedent_idx -= 1
            elif FeatureUtils.is_pronoun(self.clusters[candidate_idx]):
                if FeatureUtils.is_clitic(self.clusters[candidate_idx]) and abs(antecedent_idx - candidate_idx) <= 1 \
                    or FeatureUtils.is_location(self.clusters[antecedent_idx]) \
                    or FeatureUtils.is_pronoun(self.clusters[antecedent_idx]) \
                    or PairFeatureUtils.is_word_class_mismatch(self.clusters[candidate_idx], self.clusters[antecedent_idx]):
                    antecedent_idx -= 1
                    continue
                self.clusters[candidate_idx]["cluster"] = self.clusters[antecedent_idx]["cluster"]
                candidate_idx -= 1
                antecedent_idx -= 1
            else:
                candidate_idx -= 1
                antecedent_idx = candidate_idx - 1

    def build_mps_equivalent_class(self):
        cluster_found = {}
        for cluster in self.clusters:
            arr = cluster_found.get(cluster["cluster"])
            if cluster_found.get(cluster["cluster"]) is None:
                arr = []
                cluster_found[cluster["cluster"]] = arr
            
            arr.append(cluster["id"])

        return cluster_found

    def build_gold_equivalent_class(self, mentions):
        gold = {}
        for mention in mentions:
            labels = mention["label"]
            if not isinstance(mention["label"], list):
                labels = [labels]

            for label in labels:
                if gold.get(label) is None:
                    gold[label] = []
                if mention["id"] not in gold.get(label):
                    gold[label].append(mention["id"])

        return gold
