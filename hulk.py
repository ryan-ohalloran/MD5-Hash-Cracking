#!/usr/bin/env python3

import concurrent.futures
import hashlib
import os
import string
import sys

# Constants

ALPHABET = string.ascii_lowercase + string.digits

# Functions

def usage(exit_code=0):
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} [-a ALPHABET -c CORES -l LENGTH -p PATH -s HASHES]
    -a ALPHABET Alphabet to use in permutations
    -c CORES    CPU Cores to use
    -l LENGTH   Length of permutations
    -p PREFIX   Prefix for all permutations
    -s HASHES   Path of hashes file''')
    sys.exit(exit_code)

def md5sum(s):
    ''' Compute md5 digest for given string. '''
    
    return hashlib.md5(str.encode(s)).hexdigest()

def permutations(length, alphabet=ALPHABET):
    ''' Recursively yield all permutations of alphabet up to given length. '''
    
    if length == 0:
        yield ''
    elif length == 1:
        for letter in alphabet:
            yield letter
    else:
        for letter in alphabet:
            for permutation in permutations(length-1, alphabet):
                yield letter + permutation


def flatten(sequence):
    ''' Flatten sequence of iterators. '''
    # TODO: Iterate through sequence and yield from each iterator in sequence.
    
    for seq in sequence:
        if type(seq) == 'str':
            yield seq
        else:
            for string in seq:
                yield string

def crack(hashes, length, alphabet=ALPHABET, prefix=''):
    ''' Return all password permutations of specified length that are in hashes
    by sequentially trying all permutations. '''
    
    return [prefix + i for i in permutations(length, alphabet) if md5sum(prefix + i) in hashes]

def whack(arguments):
    ''' Call the crack function with the specified list of arguments '''
    return crack(*arguments)

def smash(hashes, length, alphabet=ALPHABET, prefix='', cores=1):
    ''' Return all password permutations of specified length that are in hashes
    by concurrently subsets of permutations concurrently.
    '''
    
    if prefix != '':
        letters = prefix
    else:
        letters = alphabet
    arguments = ((hashes, length-1, alphabet, letter) if prefix == '' else (hashes, length, alphabet, letter) for letter in letters)
    
    with concurrent.futures.ProcessPoolExecutor(cores) as executor:
        return flatten(executor.map(whack, arguments))
# Main Execution

def main():
    arguments   = sys.argv[1:]
    alphabet    = ALPHABET
    cores       = 1
    hashes_path = 'hashes.txt'
    length      = 1
    prefix      = ''

    
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-h':
            usage(0)
        elif argument == '-a':
            alphabet = arguments.pop(0)
        elif argument == '-c':
            cores = int(arguments.pop(0))
        elif argument == '-l':
            length = int(arguments.pop(0))
        elif argument == '-p':
            prefix = arguments.pop(0)
        elif argument == '-s':
            hashes_path = arguments.pop(0)
        else:
            usage(1)
    
    hashes = set(line.strip() for line in open(hashes_path))
    
    passwordList = smash(hashes, length, alphabet, prefix, cores)
    
    print(*passwordList, sep='\n')
if __name__ == '__main__':
    main()

# vim: set sts=4 sw=4 ts=8 expandtab ft=python: