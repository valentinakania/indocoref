# Coreference Resolution

A Coreference Resolution system for Bahasa Indonesia, covering coreference relations between named-entity, noun phrase, and pronouns.
This system uses rule-based Multi-Pass Sieve approach to 201 Wikipedia articles which has been annotated using SACR#https://boberle.com/projects/coreference-annotation-with-sacr/.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
python3
pip3
Python virtual environment (venv)
```

### Installing

Python Modules needed are specified in requirements.txt.

Steps on how to install in local environment (using virtual environment) are described below.

```
python -m venv <env_name>
<env_name>\Scripts\activate
pip install -r requirements.txt
```

## Running the program

The main program is located in src/run_multi_pass_sieve.py.
```
python run_multi_pass_sieve.py --annotated_dir {annotated_dir} --passage_dir {passage_dir} --temp_dir {temp_dir} --output_dir {output_dir} {--do_eval}
```

which takes care of:
1. Downloading resources (polyglot, nltk)
2. Preprocessing annotated files and saving them to pickleable files
3. Running Coreference Solver with Multi Pass Sieve
5. Running evaluation with *scorch*

#### NOTE:
If *scorch* is giving out errors in Windows, please run from Linux/Mac machine.

Experimenting on Multi Pass Sieve can be done through commenting out lines of unused pass(es).

## Citation Information

If you find this work useful in your research, please cite as below:

Cite (ACL)

    Valentina Kania Prameswara Artari, Rahmad Mahendra, Meganingrum Arista Jiwanggi, Adityo Anggraito, and Indra Budi. 2021. A Multi-PassSieve Coreference Resolution for Indonesian. In Proceedings of the International Conference on Recent Advances in Natural Language Processing (RANLP 2021), pages 79–85, Held Online. 

Cite (Bibtex)

    @inproceedings{artari-etal-2021-multi,
      title        = {A Multi-Pass Sieve Coreference Resolution for {I}ndonesian},
      author       = {Artari, Valentina Kania Prameswara  and Mahendra, Rahmad  and Jiwanggi, Meganingrum Arista  and Anggraito, Adityo  and Budi, Indra},
      year         = 2021,
      month        = sep,
      booktitle    = {Proceedings of the International Conference on Recent Advances in Natural Language Processing (RANLP 2021)},
      publisher    = {INCOMA Ltd.},
      address      = {Held Online},
      pages        = {79--85},
      url          = {https://aclanthology.org/2021.ranlp-1.10},
      abstract     = {Coreference resolution is an NLP task to find out whether the set of referring expressions belong to the same concept in discourse. A multi-pass sieve is a deterministic coreference model that implements several layers of sieves, where each sieve takes a pair of correlated mentions from a collection of non-coherent mentions. The multi-pass sieve is based on the principle of high precision, followed by increased recall in each sieve. In this work, we examine the portability of the multi-pass sieve coreference resolution model to the Indonesian language. We conduct the experiment on 201 Wikipedia documents and the multi-pass sieve system yields 72.74{\%} of MUC F-measure and 52.18{\%} of BCUBED F-measure.}
    }
    

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Scorch#https://github.com/LoicGrobol/scorch
* etc
