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

## Authors

* **Valentina Artari** - *Faculty of Computer Science, Universitas Indonesia* - [Github](https://github.com/valentinakania)
* **Rahmad Mahendra, S.Kom., M.Sc.** - *Faculty of Computer Science, Universitas Indonesia*
* **Meganingrum Arista Jiwanggi, S.Kom., M.Kom., M.C.S.** - *Faculty of Computer Science, Universitas Indonesia*
* **Adityo Anggraito** - *Faculty of Computer Science, Universitas Indonesia*
* **Dr. Indra Budi, S.Kom., M.Kom.** - *Faculty of Computer Science, Universitas Indonesia*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Scorch#https://github.com/LoicGrobol/scorch
* etc
