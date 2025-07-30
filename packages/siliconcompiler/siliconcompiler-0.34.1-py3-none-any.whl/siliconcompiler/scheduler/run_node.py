#!/usr/bin/env python3

import argparse
import os
import sys
import tarfile
import os.path

from siliconcompiler import Chip, Schema
from siliconcompiler.scheduler.schedulernode import SchedulerNode
from siliconcompiler import __version__


##########################
def main():
    schema = Schema()

    # Can't use chip.cmdline because we don't want a bunch of extra logger information
    parser = argparse.ArgumentParser(prog='run_node',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='Script to run a single node in an SC flowgraph')

    parser.add_argument('-version',
                        action='version',
                        version=__version__)
    parser.add_argument('-cfg',
                        required=True,
                        metavar='<file>',
                        help=schema.get('option', 'cfg',
                                        field='shorthelp'))
    parser.add_argument('-cwd',
                        required=True,
                        metavar='<directory>',
                        help='Run current working directory')
    parser.add_argument('-builddir',
                        metavar='<directory>',
                        required=True,
                        help=schema.get('option', 'builddir',
                                        field='shorthelp'))
    parser.add_argument('-cachedir',
                        metavar='<directory>',
                        help=schema.get('option', 'cachedir',
                                        field='shorthelp'))
    parser.add_argument('-cachemap',
                        metavar='<package>:<directory>',
                        nargs='+',
                        help='Map of caches to prepopulate runner with')
    parser.add_argument('-step',
                        required=True,
                        metavar='<step>',
                        help=schema.get('arg', 'step',
                                        field='shorthelp'))
    parser.add_argument('-index',
                        required=True,
                        metavar='<index>',
                        help=schema.get('arg', 'index',
                                        field='shorthelp'))
    parser.add_argument('-remoteid',
                        metavar='<id>',
                        help=schema.get('record', 'remoteid',
                                        field='shorthelp'))
    parser.add_argument('-archive',
                        metavar='<file>',
                        help='Generate archive')
    parser.add_argument('-include',
                        metavar='<path>',
                        nargs='+',
                        help='Files to include in archive')
    parser.add_argument('-unset_scheduler',
                        action='store_true',
                        help='Unset scheduler to ensure local run')
    parser.add_argument('-replay',
                        action='store_true',
                        help='Running as replay')
    args = parser.parse_args()

    # Change to working directory to allow rel path to be build dir
    # this avoids needing to deal with the job hash on the client
    # side
    os.chdir(os.path.abspath(args.cwd))

    # Create the Chip object.
    chip = Chip('<design>')
    chip.read_manifest(args.cfg)

    # setup work directory
    chip.set('arg', 'step', args.step)
    chip.set('arg', 'index', args.index)
    chip.set('option', 'builddir', os.path.abspath(args.builddir))

    if args.cachedir:
        chip.set('option', 'cachedir', os.path.abspath(args.cachedir))

    if args.remoteid:
        chip.set('record', 'remoteid', args.remoteid)

    if args.unset_scheduler:
        for _, step, index in chip.get('option', 'scheduler', 'name',
                                       field=None).getvalues():
            chip.unset('option', 'scheduler', 'name', step=step, index=index)

    if args.cachemap:
        for cachepair in args.cachemap:
            package, path = cachepair.split(':')
            chip.get("package", field="schema")._set_cache(package, path)

    # Populate cache
    for resolver in chip.get('package', field='schema').get_resolvers().values():
        resolver()

    # Run the task.
    error = True
    try:
        SchedulerNode(chip,
                      args.step,
                      args.index,
                      replay=args.replay).run()
        error = False

    finally:
        if args.archive:
            # Archive the results.
            with tarfile.open(args.archive,
                              mode='w:gz') as tf:
                chip._archive_node(tf,
                                   step=args.step,
                                   index=args.index,
                                   include=args.include)

    # Return success/fail flag, in case the caller is interested.
    if error:
        return 1
    return 0


##########################
if __name__ == "__main__":
    sys.exit(main())
