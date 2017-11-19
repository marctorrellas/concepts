from main import add_concepts, clean, init, query_input, add_concepts_dir, query_input_file, DB_NAME
import os, pytest, sqlite3


@pytest.fixture(scope='module')
def backup_existing_db():
    if os.path.exists(DB_NAME):
        os.rename(DB_NAME,DB_NAME+'.bak')


@pytest.fixture()
def get_db():
    # run before each test
    db = sqlite3.connect(DB_NAME)
    cur = db.cursor()
    tables = cur.execute("select name from sqlite_master where type=='table'").fetchall()
    # A list of tuples is returned, turn to list
    if len(tables) > 0:
        tables = [i[0] for i in tables]
    yield db, cur, tables
    db.commit()


def test_empty_clean(backup_existing_db, get_db):
    db,cur,tables = get_db[0], get_db[1], get_db[2]
    assert not clean(cur, tables)


def test_init(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert init(cur, tables)


def test_init_already_done(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert not init(cur, tables)


def test_add_concepts(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert add_concepts('test_docs/concepts1.txt', cur) == 15


def test_add_concepts_again(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert add_concepts('test_docs/concepts1.txt', cur) == 0


def test_add_concepts_dir(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert add_concepts_dir('test_docs', cur) == 6


def test_clean2(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert clean(cur, tables)


def test_add_concepts_dir2(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert add_concepts_dir('test_docs', cur) == 21


def test_query_sent(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert len(query_input('How many East Asian people live in Catalonia?', cur)) == 3


def test_query(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert len(query_input_file('test_docs/questions1.txt', cur)) == 6


def test_query2(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert len(query_input_file('test_docs/questions2.txt', cur)) == 7


def test_query_notfound(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert query_input_file('test_docs/questions_notfound.txt', cur) == {'none'}


def test_query_emptyfile(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    assert query_input_file('test_docs/questions_empty.txt', cur) == ['none']


def test_clean_3(get_db):
    db, cur, tables = get_db[0], get_db[1], get_db[2]
    x = clean(cur, tables)
    os.remove(DB_NAME)
    if os.path.exists(DB_NAME+'.bak'):
            os.rename(DB_NAME+'.bak', DB_NAME)
    assert x
