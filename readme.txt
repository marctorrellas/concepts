Author: Marc Torrellas
Nov. 2017

********
Overview
********

The system implemented returns a list of concepts found in queries. It is able to handle requests to add new
concepts from files, and returning a list of concepts from input queries. See section Syntax for more details

*******************
Python requirements
*******************

- Python3
- nltk
- pytest
- sqlite3

***********
Assumptions
***********

- Concepts are described by at most two words. The first word is called the adj (from adjective) in code, the
  second one the root. This nomenclature is based on test examples, but does not need necessarily to apply to all
  possible concepts.
- Based on the last assumption, the database is organized by roots as keys, an all applicable adjectives as its
  value. The list of adjectives are separated by commas. If a concept can be defined by just one word, the assigned
  adjective is "_".
- First word in a question will never be a concept. This can easily be changed, it's just a speed improvement
  based on the observation of how humans use to build query inputs.
- Stop words will never be root. This saves us to check many queries to the DBs. Again, can be easily changed
  if not accepted as a valid assumption.

******
Syntax
******

python3 main.py [command] [possible args]

Available commands:
    - add_concepts: add concepts file, containing one concept per line
    - add_concepts_dir: add all concepts files in directory, whose filenames must contain the word "concepts",
      e.g. concepts1.txt
    - query_input: queries a sentence to get list of concepts in it
    - query_input_file: queries for all questions in files, one per line
    - clean

********
Examples
********

python3 main.py clean
python3 main.py add_concepts test_docs/concepts1.txt
python3 main.py add_concepts_dir test_docs
python3 main.py query_input "what west"
python3 main.py query_input "what west indian is chinese"
python3 main.py query_input_file test_docs/questions1.txt

*******
Testing
*******

Some tests have been prepared. They can be executed by:

pytest -s tests.py

or

pytest -vs tests.py

for additional details

**********
Extensions
**********

Some ideas to improve speed:

- Using Redis rather than sqlite. Redis is faster but the requests involve network overhead. Depending on
  the size of the DB could improve performance
- Search in parallel in multiple databases using a map-reduce framework
- Use a compiled language, e.g. C++


