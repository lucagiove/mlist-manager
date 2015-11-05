Mlist Manager
=============

This is a simple tool to help extracting mail addresses from any txt files
uniform them and keep track of removed mails from an external mailing system.

Files
-----

**full_mlist.csv**

This is the complete db where all collected mails are stored.

**export_mlist.csv**

This is the exported csv  that has the current e-mail addresses in the mailing
list (without people that removed themself).

**removed_mlist.csv**

This includes the addresses that have been removed from the mailing list.
These addresses should not be re-added for any reason!!!

**output.csv**

This is a list of new addresses ready to be imported in mlist system.

Actions
-------

**extract**

This action extracts the mails from any text file with a powerful regex.

**update**

This action performs the diff between the complete list and the current
status removed = full - export

It also make sure the format is the correct and mails are sorted and
duplicated removed.

Addresses included only in export and not full  means they've been added
manually on the mlist system and for this reason they've to be updated in
full. full = full + (export - full)

**add**

Takes a new mail list and add the addresses to source, substract the
removed and add the remaining to a ready to import in aruba file.

**merge**

Takes two files and add the mails in one file to the second removing
duplicated and sorting them.
