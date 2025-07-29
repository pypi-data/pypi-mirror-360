import os
import os.path
import re

def do_it(wd      :str,
          fn_regex:str):

    print(f'Looking in {wd}, where file names match {repr(fn_regex)}')
    found:list[str] = []
    for dp,dns,fns in os.walk(wd):

        for fn in fns:

            fn_full  = os.path.join(dp, fn)
            if not re.search(pattern=fn_regex, string=fn_full): continue
            found.append(fn_full)
    
    if found:

        for fn in found:
                
            print('>>> ' + fn)
    
    else:

        print('No occurrences.')

def main():

    import argparse

    class A:

        WORKING_DIRECTORY = 'wd'
        FILE_NAME_REGEX   = 'fnre'

    p = argparse.ArgumentParser(description='Find all files whose name matches a given expression')
    p.add_argument(f'--{A.WORKING_DIRECTORY}',
                   help   ='working directory - defaults to current',
                   default='.')
    p.add_argument(f'{A.FILE_NAME_REGEX}',
                   help   ='file name regex to consider')
    get = p.parse_args().__getattribute__
    # do it
    do_it(wd      =get(A.WORKING_DIRECTORY),
          fn_regex=get(A.FILE_NAME_REGEX))

if __name__ == '__main__': main()
