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

__version__ = "0.2.0"

import re
from argparse import ArgumentParser


class MlistManager():

    def __init__(self, full_path, export_path,
                 removed_path="", import_path=""):

        # TODO if not specified will use as suffix the folder name
        self.full_path = full_path
        self.export_path = export_path
        self.removed_path = removed_path

        self.full = self._load(full_path)
        self.export = self._load(export_path)
        # removed might not exist
        self.removed = self._load(removed_path, strict=False)

        print "full has {} addresses".format(len(self.full))
        print "export has {} addresses".format(len(self.export))
        print "removed has {} addresses".format(len(self.removed))

    def _add_quotes(self, mail):
        if mail[0] != '"':
            mail = '"{}'.format(mail)
        if mail[-1] != '"':
            mail = '{}"'.format(mail)
        return mail

    def _load(self, filename, strict=True):
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
        mails = [self._add_quotes(x.lower()) for x in match]
        return set(mails)

    def _write(self, data, filename):
        with open(filename, 'w') as f:
            for m in sorted(data):
                f.write('{}\n'.format(m))

    def update(self):
        new_removed = set(self.full - self.export)
        self.removed = set(self.removed | new_removed)
        self.full = set(self.full | self.export)

        # missing mails in export are added to full
        self._write(self.full, self.full_path)
        # export is only sanitized and sorted
        self._write(self.export, self.export_path)
        # this file is updated
        self._write(self.removed, self.removed_path)

        print "updated full has {} addresses".format(len(self.full))
        print "updated export has {} addresses".format(len(self.export))
        print "updated removed has {} addresses".format(len(self.removed))

    def extract(self, source_path, destination_path):
        extracted = self._load(source_path)
        self._write(extracted, destination_path)


def _default_file_name():
    pass


def main():

    parser = ArgumentParser()

    parser.add_argument("-d", "--data-path",
                        action='store', dest='DATA', default="./",
                        help="path where all files are located, if names are "
                             "defaults will be automatically detected")

    parser.add_argument("-f", "--full",
                        action='store', dest='FULL', default="",
                        help="the complete db where all collected mails are "
                             "stored")

    parser.add_argument("-e", "--export",
                        action='store', dest='EXPORT', default="",
                        help="the exported csv that has the real e-mail "
                             "addresses of the mailing list (without people "
                             "that removed themself)")

    parser.add_argument("-r", "--removed",
                        action='store', dest='REMOVED', default="removed.csv",
                        help="the addresses that have been removed from the "
                             "mailing list")

    parser.add_argument("-i", "--import",
                        action='store', dest='IMPORT',
                        help="list of new addresses ready to be imported")

    parser.add_argument("--update",
                        action='store_true', dest='UPDATE',
                        help="")

    parser.add_argument('--version', action='version',
                        version="%(prog)s {}".format(__version__))

    args = parser.parse_args()
    mm = MlistManager(args.FULL, args.EXPORT, args.REMOVED, args.IMPORT)

    if args.UPDATE:
        mm.update()

    return 0

if __name__ == '__main__':
    main()