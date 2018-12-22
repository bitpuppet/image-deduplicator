#BlogPost: http://enamulhaq.com/blog/avoid-picture-duplication---reclaim-your-space

import os

class FileFinder(object):
 
    @classmethod
    def ifind(self, src_path, filter_exts=None, 
             ext_delimiter='.'):
        '''
            Function given the directory path and extension, it'll
            reutrn the generator to iterator the list of files found
        '''
        if filter_exts and not isinstance(filter_exts, list):
            raise TypeError('filter_exts should be a list of extensions')
 
        for dirpath, subdirs, filenames in os.walk(src_path):
            for fn in filenames:
                if filter_exts:
                    if fn[ fn.rfind(ext_delimiter) + 1:] in filter_exts:
                        yield os.path.join(dirpath, fn)
                else:
                    yield os.path.join(dirpath, fn)

class ImageFinder(object):
    
    filters_ext = ['jpg', 'jpeg', 'JPG']

    @classmethod
    def ifind(cls, src_path):
        return FileFinder.ifind(src_path, cls.filters_ext)
