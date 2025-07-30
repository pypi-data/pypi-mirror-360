#!/usr/bin/env python
from __future__ import with_statement

import traceback

from argparse import ArgumentParser
from a2p2 import __release_notes__
from distutils.version import LooseVersion



def createMdReleaseNotes():
    """
    Present in a reverse ordered way the dictionnary version items.
    """
    txt = "# A2P2 release notes"
    lvs = [LooseVersion(v) for v in __release_notes__]
    for lv in sorted(lvs, reverse=True):
        v=lv.vstring
        txt += "\n## V " + v + " :"
        keys = []
        for k in sorted(__release_notes__[v]):
            if not ("TODO" in k):
                keys.append(k)
        for k in sorted(__release_notes__[v]):
            if "TODO" in k:
                keys.append(k)

        for e in keys:
            infos = __release_notes__[v][e]
            if infos:
                txt += "\n### " + e + " : "
                for i in infos:
                    txt += "\n- " + i
        txt += "\n\n"
    f=open("release-notes.md", "w")
    f.write(txt)
    print(f"{f.name} generated")


def main():
    """Main method to start a2p2 program."""
    parser = ArgumentParser(
        description='Move your Aspro2 observation details to an observatory proposal database')
    # parser.add_argument('-c', '--config', action='store_true', help='show instruments and remote service configurations.')
    parser.add_argument('-f', '--fakeapi', action='store_true',
                        help='fake API to avoid remote connection (dev. only).')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')
    parser.add_argument('-c', '--createprefs', action='store_true', help='Create preferences file')
    parser.add_argument('-r', '--releasenotes', action='store_true', help='Create md release notes file')

    args = parser.parse_args()

    from . import A2p2Client

    if args.releasenotes:
        createMdReleaseNotes()
        exit()

    if args.createprefs:
        A2p2Client.createPreferencesFile()
        exit()


    try:
        with A2p2Client(args.fakeapi, args.verbose) as a2p2c:
            # if  args.config:
            #    print(a2p2c)
            # else:
            #    a2p2c.run()
            a2p2c.run()

    except Exception as e:
        if True or args.verbose:
            traceback.print_exc()
        else:
            print('ERROR: %s' % str(e))


if __name__ == '__main__':
    main()
