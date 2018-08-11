import pdb
def foo(**kwargs):
    pdb.set_trace()
    print('end')

foo(**{'key1':1, 'key2':2})