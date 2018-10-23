#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mlist-manager.py
#
#  Copyright 2015 Luca Giovenzana <luca@giovenzana.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

__version__ = "0.2.2"

import os
import re
from argparse import ArgumentParser


def extract(filename, strict=True):
    """This method will extract mails using a regex then remove extra ",
       duplicated and sort"""
    mails = []
    regex = re.compile(r'([\w.-]+@+[\w.-]+\.+[\w.]+)')
    try:
        with open(filename, 'r') as f:
            match = re.findall(regex, f.read())
    except IOError as e:
        # strict is used to make sure the file exists
        if strict:
            raise e
        # we can return an empty list if the file don't exist and is not
        # important so that the execution can proceed without problems
        else:
            return set([])
    mails = [_add_quotes(x.lower()) for x in match]
    return sorted(set(mails))


def write_list(data, filename, overwrite=False, append=False):
    if not overwrite:
        if os.path.exists(filename):
            raise Exception("ERROR: file {} "
                            "already exists.".format(filename))
    if append:
        f = open(filename, 'a')
        f.write('\n')
    else:
        f = open(filename, 'w')
    for m in sorted(data):
        f.write('{}\n'.format(m))


def _add_quotes(mail):
    if mail[0] != '"':
        mail = '"{}'.format(mail)
    if mail[-1] != '"':
        mail = '{}"'.format(mail)
    return mail


class MlistManager():

    def __init__(self, full_path, current_path,
                 removed_path="", import_path=""):

        # TODO if not specified will use as suffix the folder name
        self.full_path = full_path
        self.current_path = current_path
        self.removed_path = removed_path

        self.full = extract(full_path)
        self.current = extract(current_path)
        # removed might not exist
        self.removed = extract(removed_path, strict=False)

        print "full has {} addresses".format(len(self.full))
        print "current has {} addresses".format(len(self.current))
        print "removed has {} addresses".format(len(self.removed))

    def update(self):
        # FIXME if by error data are not updated erroneus removed will be
        # created
        self.removed = set(self.full) - set(self.current)
        self.full = set(self.full) | set(self.current)

        # missing mails in current are added to full
        write_list(self.full, self.full_path, overwrite=True)
        # current is only sanitized and sorted
        write_list(self.current, self.current_path, overwrite=True)
        # this file is updated
        write_list(self.removed, self.removed_path, overwrite=True)

        print "updated full has {} addresses".format(len(self.full))
        print "updated current has {} addresses".format(len(self.current))
        print "updated removed has {} addresses".format(len(self.removed))

    def add(self, source_path, destination_path):
        # before adding make sure that all data are updated
        print "updating to makes sure data are reliable..."
        self.update()
        # get the mails from a txt file
        extracted = extract(source_path)
        print "extracted {} addresses".format(len(extracted))
        # prepare an import file with only the new ones
        output = set(extracted) - set(self.full) - set(self.removed)
        write_list(output, destination_path, overwrite=True, append=True)
        print "found {} new addresses to be added".format(len(output))
        self.full = set(self.full | output)
        write_list(self.full, self.full_path, overwrite=True)
        print "updated full has {} addresses".format(len(self.full))


def _default_file_name():
    pass


def main():

    parser = ArgumentParser()

    # ~parser.add_argument("-d", "--data-path",
                        # ~action='store', dest='DATA', default="./",
                        # ~help="path where all files are located, if names are "
                             # ~"defaults will be automatically detected")

    parser.add_argument("--extract-only",
                        action='store_true', dest='EXTRACT',
                        help="mode that parse the txt extracting and "
                             "sanitizing the mails")

    parser.add_argument("--update",
                        action='store_true', dest='UPDATE',
                        help="mode that updates the data structure without "
                             "adding the new addresses. WARNING running this "
                             "with outdated data might add wrong address to "
                             "the removed file.")

    parser.add_argument("--add",
                        action='store_true', dest='ADD',
                        help="mode that actually does the update and add new "
                             "addresses")

    parser.add_argument("-i", "--input",
                        action='store', dest='INPUT',
                        help="txt file with mails to be added "
                             "in mailing list system",
                        required=False)

    parser.add_argument("-o", "--output",
                        action='store', dest='OUTPUT',
                        default="output.csv",
                        help="list of new addresses ready to be imported "
                             "in mailing list system")

    parser.add_argument("-f", "--full",
                        action='store', dest='FULL', default="",
                        help="the complete db where all collected mails are "
                             "stored")

    parser.add_argument("-c", "--current",
                        action='store', dest='CURRENT', default="",
                        help="the exported csv that has the current e-mail "
                             "addresses in the mailing list (without people "
                             "that removed themself)")

    parser.add_argument("-r", "--removed",
                        action='store', dest='REMOVED', default="removed.csv",
                        help="the addresses that have been removed from the "
                             "mailing list")

    parser.add_argument('--version', action='version',
                        version="%(prog)s {}".format(__version__))

    args = parser.parse_args()

    if args.EXTRACT:
        extracted = extract(args.INPUT)
        print extracted
        print "input has {} addresses".format(len(extracted))
        if args.OUTPUT:
            write_list(extracted, args.OUTPUT)
        return 0
    elif args.UPDATE:
        mm = MlistManager(args.FULL, args.CURRENT, args.REMOVED)
        mm.update()
    elif args.ADD:
        mm = MlistManager(args.FULL, args.CURRENT, args.REMOVED)
        mm.add(args.INPUT, args.OUTPUT)
    else:
        parser.error("At least one option between --extract-only, --update\n"
                     "or --add needs to be selected.")

    return 0


if __name__ == '__main__':
    main()
