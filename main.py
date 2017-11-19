import argparse, os, logging, re, string, sys
import sqlite3
from nltk.corpus import stopwords

stop = set(stopwords.words('english'))

DB_NAME = 'concepts.db'

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)


def add_concepts(fname, cur, verbose=True):
    """
    adds a list of concepts to the database
    :param fname: path to the document containing the concepts
    :param cur: cursor pointing to the DB
    :param verbose: True to log number of new concepts at the end
    :return number of new concepts added
    """

    # check if file exists
    if not os.path.exists(fname):
        log.info('File {} not found'.format(fname))
        return 0

    # Read doc
    with open(fname, 'r', encoding='utf-8') as f:
        doc = f.readlines()
    log.info('Found {} concepts in {}'.format(len(doc), fname))
    new_concepts = 0
    for c in doc:  # for each concept
        #
        c = c.strip().lower().split(' ')
        if len(c) > 2:
            log.error("Three word concept found. System was designed assuming a max of two words per concept")
            quit()
        two_words = len(c) == 2
        if two_words:
            adj, root = c  # save concepts in lowercase
        else:
            adj, root = '_', c[0]  # if no adj, adj = '_'

        # check if the root concept is already in the database
        root_apps = cur.execute('select * from concepts where root == "{}"'.format(root)).fetchone()
        if root_apps is None:
            log.debug("{} not found, adding {}".format(root, (adj, root)))
            # add new root and adj
            new_concepts += 1
            cur.execute('insert into concepts (root, adjs) values ("{}", "{}")'.format(root, adj))
        else:
            # add new adj to this root
            root_apps = set(root_apps[1].split(','))
            if adj not in root_apps:
                log.debug("{} found, adding {}".format(root, (adj, root)))
                new_concepts += 1
                root_apps |= set([adj])
                cur.execute("update concepts set adjs = '{}' where root = "
                            "'{}'".format(str(','.join(root_apps)), root))
            else:
                log.debug('Concept "{}" already in the DB. Omitted'.format(c))

    if verbose:
        log.info("Added {} new concepts".format(new_concepts))
    return new_concepts


def add_concepts_dir(dirname, cur):
    n = 0
    if not dirname.endswith('/'):
        dirname += '/'
    for f in os.listdir(dirname):
        if 'concepts' in f:
            n += add_concepts(dirname + f, cur, verbose=False)
    log.info("Added {} new concepts".format(n))
    return n


def query_input(sent, cur):
    """
    Given an input sentence, searches in the database for all concepts in the input
    :param sent: sentence input
    :param cur: pointer to DB
    :return: found concepts
    """
    sent = re.sub(r"\.|\?|\!|,", '', sent.strip()).lower().split()
    concepts = set()
    log.debug(sent)
    for r in range(1, len(sent)):
        root = sent[r]
        root_apps = cur.execute("select * from concepts where root == '{}'".format(root)).fetchone() \
            if root not in stop else None
        if root_apps is None:
            continue
        root_apps = set(root_apps[1].split(','))
        log.debug("{} found".format(root))
        # if root is itself a concept, will be in DB with '_' in adjs
        if '_' in root_apps:
            log.debug("{} is a itself a concept".format(root))
            concepts.update([string.capwords(root)])
        adj = sent[r - 1]
        if adj in root_apps:
            log.debug("{} found".format(' '.join([adj, root])))
            concepts.update([string.capwords(' '.join([adj, root]))])
    return concepts if len(concepts) > 0 else {"none"}


def query_input_file(fname, cur):
    if not os.path.exists(fname):
        log.info("File not found")
        quit()
    log.debug("Reading file {}".format(fname))
    with open(fname, 'r', encoding='utf-8') as f:
        sents = f.readlines()
    concepts = set()
    for sent in sents:
        concepts |= query_input(sent, cur)
    if len(concepts) > 1:
        concepts -= {'none'}
    log.debug("Concepts found: {}".format(concepts))
    return concepts if len(concepts) > 0 else ["none"]


def clean(cur, tables):
    """
    Remove concepts from database
    :param cur: pointer to DB
    :return: True if done, False if no tables found
    """
    cleaned = False
    if 'concepts' in tables:
        n = cur.execute('select count(*) from concepts;').fetchall()[0][0]
        if n > 0:
            log.info("Found {} elems. Deleting".format(n))
            cur.execute('delete from concepts;')
            cleaned = True
    if cleaned:
        log.info("Database cleaned")
        return True
    else:
        log.info("Nothing to clean")
        return False


def init(cur, tables):
    """
    :param cur: pointer to DB
    :param tables: names of tables in DB
    :return: True if success, False if table already there
    """
    new_table = False
    if 'concepts' not in tables:
        new_table = True
        cur.execute("create table `concepts` (`root` STRING PRIMARY KEY, `adjs` TEXT);")

    if new_table:
        log.info("Database successfully initialized")
        return True
    else:
        return False

if __name__ == '__main__':

    if sys.version_info[0] < 3:
        log.error("Must be using Python 3")
        quit()

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='PROG')
    subparsers = parser.add_subparsers(help='help for subcommand', dest='command')

    # create the parser for the "add_doc" command
    parser_a = subparsers.add_parser('add_concepts')
    parser_a.add_argument('fname', type=str, help='file name')

    parser_b = subparsers.add_parser('add_concepts_dir')
    parser_b.add_argument('dirname', type=str, help='dir name')

    parser_c = subparsers.add_parser('query_input')
    parser_c.add_argument('sent', type=str)

    parser_d = subparsers.add_parser('query_input_file')
    parser_d.add_argument('fname', type=str)

    parser_e = subparsers.add_parser('clean')



    args = parser.parse_args()
    command = args.command
    if command is None:
        parser.print_help()
        quit()

    db = sqlite3.connect(DB_NAME)
    cur = db.cursor()
    tables = cur.execute("select name from sqlite_master where type=='table'").fetchall()
    # A list of tuples is returned, turn to list
    if len(tables) > 0:
        tables = [i[0] for i in tables]
    else:  # if there are no tables
        if 'add_concepts' in command:
            init(cur, tables)
        else:
            os.remove(DB_NAME)
            if command == 'clean':
                log.info("Nothing to clean")
            else:  # query input
                log.info("No data in the system. Please add data before querying")
            quit()

    if command == 'add_concepts':
        add_concepts(args.fname, cur)
    elif command == 'add_concepts_dir':
        add_concepts_dir(args.dirname, cur)
    elif command == 'query_input':
        # Only query if any docs have been added
        if cur.execute('SELECT * from concepts').fetchone() is None:
            log.info("No concepts added, cannot query")
            quit()
        log.info('Matches {}'.format(', '.join(query_input(args.sent, cur))))
    elif command == 'query_input_file':
        if cur.execute('SELECT * from concepts').fetchone() is None:
            log.info("No concepts added, cannot query")
            quit()
        log.info('Matches {}'.format(', '.join(query_input_file(args.fname, cur))))
    else:  # command == 'clean':
        clean(cur, tables)

    db.commit()
