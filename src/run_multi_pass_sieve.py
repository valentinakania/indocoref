import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

import nltk
from polyglot.downloader import downloader

from utils.text_preprocess import TextPreprocess
from mpsieve import MultiPassSieve

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)

def run():
    
    logger.info('----- Coreference Resolution with Multi-Pass Sieve -----')
    parser = argparse.ArgumentParser()

    parser.add_argument("--annotated_dir",
                        help="Directory containing annotated files in SACR format")
    parser.add_argument("--passage_dir",
                        help="Directory containing passage files in txt")
    parser.add_argument("--output_dir",
                        help="Output directory for equivalent classes files",
                        required=False,
                        default=None)
    parser.add_argument("--temp_dir",
                        help="Directory to keep temporary .pkl files",
                        required=False,
                        default="./temp")

    parser.add_argument("--log_step",
                        help="Logging steps",
                        required=False,
                        default=10)

    parser.add_argument("--do_eval",
                        help="Set this argument to do evaluation in scorch. Note that scorch might not work well in Windows.",
                        action="store_true")
    
    args = parser.parse_args()

    if args.output_dir is None:
        now = datetime.now()
        args.output_dir = Path("./output-{}".format(now.strftime("%Y-%m-%d-%H-%M-%S"))).as_posix()

    logger.info("Running CR with config: %s" % vars(args))

    logger.info('Downloading resources...')
    downloader.download('embeddings2.id')
    downloader.download('pos2.id')

    nltk.download('punkt')
    logger.info('Downloading resources Done')
    logging.info('Preprocessing Text...')
    TextPreprocess(args.annotated_dir, args.temp_dir).run(args.log_step)

    logging.info('----- CR: Multi Pass Sieve -----')
    MultiPassSieve(args.passage_dir, args.temp_dir, args.output_dir).run(args.log_step)
    if args.do_eval:
        logging.info('Evaluating results...')
        os.system('scorch {output_dir}/tesrun/gold {output_dir}/result-mps {output_dir}/eval.txt'
                    .format(output_dir=args.output_dir))

        logging.info('Evaluating results saved in {}/eval.txt'.format(args.output_dir))

    logging.info('----- Coreference Resolution Done-----')

run()