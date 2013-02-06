import time
import sqlite3
import importlib
import cPickle as pickle
import os.path
import memcache

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

def get_categories_from_db():
    con = sqlite3.connect('test.db')
    cur = con.cursor()    
    cur.execute('SELECT * FROM categories;')
    categories = cur.fetchall()
    #nice tree should be build here but that is not the point
    return categories
    
def get_categories_from_pickledfile():
    path = 'catcache.p'
    if not os.path.exists(path):
        start = time.time()
        pickle.dump( get_categories_from_db(), open( path, 'wb' ) )
        print '(SET CACHE IN %f)' % (time.time() - start)
    return pickle.load(open( path, 'rb' ));
    
def get_categories_from_memcached():
    key = 'catcache'
    categories = mc.get(key)
    if not categories:
        start = time.time()
        categories = get_categories_from_db()
        mc.set(key, categories)
        print '(SET CACHE IN %f)' % (time.time() - start)
    return categories

def get_categories_from_pythonsrc():
    if not os.path.exists('catcache.py'):
        start = time.time()
        f = open( 'catcache.py', 'wb' )
        categories = get_categories_from_db()
        f.write('x = ' + repr(categories))
        f.close()
        print '(SET CACHE IN %f)' % (time.time() - start)
    import catcache
    return catcache.x

for run in ['FIRST RUN', 'SECOND RUN']:
    print run
    for m in ['get_categories_from_db', 'get_categories_from_memcached', 'get_categories_from_pickledfile', 'get_categories_from_pythonsrc']:
        print m
        start = time.time()
        for i in range(2**15):
            categories = locals()[m]()
        print time.time() - start

