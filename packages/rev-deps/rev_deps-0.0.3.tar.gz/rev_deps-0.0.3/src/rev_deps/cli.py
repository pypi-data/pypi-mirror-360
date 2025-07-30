import sys

from . import api

def main(args=sys.argv[1:]):
    
    project=args[0]
    
    for dependency in api.get_rev_deps(project):
        print(dependency)
        
    return 0