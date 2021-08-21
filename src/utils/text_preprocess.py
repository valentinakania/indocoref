import os
import re
import logging

from utils.feature_utils import FeatureUtils
from utils.feature_utils import CLITICS
from utils.file_utils import FileUtils

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)

class TextPreprocess:
    def __init__(self, annotated_dir, pkl_dir):
        files = os.listdir(annotated_dir)
        self.filenames = files
        self.annotated_dir = annotated_dir
        self.pkl_dir = pkl_dir

    def run(self, log_step=10):
        total_mentions = 0
        total_files = len(self.filenames)
        for idx, name in enumerate(self.filenames):
            if (idx + 1) % log_step == 0:
                logging.info("Preprocessing %d/%d" % (idx + 1, total_files))
            annotation, sents = FileUtils.read_annotated_file(self.annotated_dir, name)
            
            mentions = self.tokenize_by_regex(annotation)
            mentions = self.merge_nested_labels(mentions)
            self.gen_mention_attributes(mentions, sents)
            label_map = self.map_label_by_id(mentions)
            label_map = self.merge_labelmap(label_map)
            mentions = self.put_labels(mentions, label_map)
            total_mentions += len(mentions)

            FileUtils.write_to_pickle(self.pkl_dir, name, mentions)
        
        logging.info('Total mentions found: %s' % total_mentions)

    ### Tokenize annotated document by regex according to SACR format
    ### SACR format:
    ### [...<other text>..., '{', <ID>, ':', <property_name>, '=', "<property_value>" <annotated_mention>, '}', ...<other text>...]  
    ### Ex:
    ### ['{', 'M1', ':', 'jenis', '=', '"noun phrase other" judul novel', '}', 'dari tahun 1990.']
    def tokenize_by_regex(self, annotation):
        tokens = re.split(r'({|:|=|})', annotation)
        i = 0
        j = 0
        brackets = 0
        mentions = []

        while i < len(tokens):
            if tokens[i] == '}':
                brackets -= 1
            if tokens[i] == '{':
                brackets += 1
                mention = dict()
                mention['id'] = j
                j += 1
                i += 1
                if brackets > 1:
                    mention['num_labels'] = brackets - 1
                if mention.get('labels') is None:
                    mention['labels'] = []
                mention['labels'].append(tokens[i][1:])

                # Skipping ':', <property_name>, '='
                i += 4

                found = re.search(r'^"([^"]*)" (.*)$', tokens[i])
                class_type = found.group(1)
                text = found.group(2)
                mention['class'] = class_type
                mention['text'] = text.strip()
                mentions.append(mention)
            i += 1
        return mentions

    def merge_nested_labels(self, mentions):
        j = len(mentions) - 1
        i = len(mentions) - 2
        while j > 0 and i >= 0:
            if i >= j:
                i = j - 1
            if mentions[j].get('num_labels', 0) > 0:
                before = mentions[i]
                after = mentions[j]
                after['num_labels'] -= 1
                if before['text'].strip() == '':
                    after['labels'] = before['labels'] + after['labels']
                    if after['class'] == '':
                        after['class'] = before['class']
                    mentions.remove(before)
                    i -= 1
                    j -= 1
                elif after['text'] not in before['text']:
                    if after['text'] in CLITICS:
                        before['text'] += after['text']
                    else:
                        before['text'] += ' ' + after['text']
                if after['class'] == '':
                    after['class'] = before['class']
                if mentions[j].get('num_labels', 0) == 0:
                    i -= 1
                    j -= 1
            else:
                j -= 1
                i -= 1
        return mentions

    def gen_mention_attributes(self, mentions, sentences):
        for idx, mention in enumerate(mentions):
            mention['pronoun'] = FeatureUtils.is_pronoun(mention)
            mention['proper'] = FeatureUtils.is_proper_noun(mention)
            mention['sent'] = FeatureUtils.find_in_sentence(mention, sentences)
            mention['pos'], mention['tag'] = FeatureUtils.get_pos_and_chunks(mention['text'])
            mention['cluster'] = idx
            mention['per'] = 1 if mention['class'] == 'named-entity person' else 0
            mention['org'] = 1 if mention['class'] == 'named-entity organisation' else 0
            mention['loc'] = 1 if mention['class'] == 'named-entity place' else 0
            mention['ner'] = 1 if 'named-entity' in mention['class'] else 0

    def map_label_by_id(self, objs):
        label_map = dict()
        for obj in objs:
            labels = sorted(obj['labels'], key=int)
            if len(labels) > 1:
                label_map[labels[len(labels) - 1]] = labels[:-1]
            else:
                label_map[labels[0]] = labels[0]
        for label in label_map.keys():
            if len(label_map.get(label)) == 1:
                label_map[label] = label_map.get(label)[0]

        return label_map

    def merge_labelmap(self, label_map):
        for label in label_map.keys():
            if isinstance(label_map.get(label), str):
                curr_label = label
                antecedent = label_map.get(curr_label)
                while antecedent != curr_label:
                    label_map[label] = label_map.get(antecedent)
                    curr_label = label_map[label]
                    if not isinstance(curr_label, str):
                        break
                    antecedent = label_map.get(curr_label)
                    if not isinstance(antecedent, str):
                        break
        return label_map

    def put_labels(self, objs, label_map):
        for obj in objs:
            obj['labels'].sort(key=int)
            obj['label'] = label_map.get(obj['labels'][-1])
        return objs