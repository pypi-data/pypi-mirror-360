
import sys
import os

from nwebclient import NWebClient
from nwebclient import util

class DocMap:
    def __init__(self, executor, meta_value_key, base, dict_map):
        self.count = 0
        self.executor = executor
        self.meta_value_key = meta_value_key
        self.base = base
        if isinstance(dict_map, str):
            self.dict_map = dict_map.split(':')
        else: 
            self.dict_map = ['title', 'mapped_title']
    def __call__(self, doc, nclient):
        data = self.base | doc.to_dict()
        if doc.is_image():
            doc.downloadThumbnail('docmap.jpg', 'm')
            data['image_filename'] = 'docmap.jpg'
        data[self.dict_map[1]] = data[self.dict_map[0]]
        result = self.executor(data)
        self.count += 1
        return result[self.meta_value_key]
                
def mapDocs(n, args):
    meta_ns = args.getValue('meta_ns')
    meta_name = args.getValue('meta_name')
    filterArgs = args.getValue('filter', 'kind=image')
    limit = int(args.getValue('limit', 1000))
    update = bool(args.getValue('update', True))
    meta_value_key = args.getValue('meta_value_key')
    executor = args.getValue('executor')
    dict_map = args.getValue('dict_map', None)
    base = args.getValue('base', None)
    print("Params:")
    print("  pwd             " + os.getcwd())
    print("  meta_ns:        " + meta_ns)
    print("  meta_name:      " + meta_name)
    print("  filter:         " + filterArgs)
    print("  limit:          " + str(limit))
    print("  update:         " + str(update))
    print("  meta_value_key: " + meta_value_key)
    print("  executor:       " + str(executor))
    print("  base:           " + str(base))
    print("  dict_map:       " + str(dict_map))
    print("")
    exe = util.load_class(executor, create=True)
    if base is None:
        base = {}
    else:
        base = util.load_json_file(base)
    fn = DocMap(exe, meta_value_key, base, dict_map)
    n.mapDocMeta(meta_ns=meta_ns, meta_name=meta_name, filterArgs=filterArgs, limit=limit, update=update, mapFunction=fn)
    

def main():
    print("python -m nwebclient.nc")
    print("Params: ")
    print("  - dict_map Abbildung des JobResults auf nweb:meta")
    c = NWebClient(None)
    args = util.Args()
    if args.hasFlag('map'):
        mapDocs(c, args)
    else:
        print(sys.argv)
        print(str(c.docs()))

if __name__ == '__main__': 
    main()