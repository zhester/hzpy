In-Memory Tar Archive Creation
==============================

A lot of my work in Python involves processing large volumes of data from
various sources (reports, data acquisition systems, binary files, etc).
I have a few scripts that take in relatively few files and output
thousands of small files representing logical segments of the input files.
The end-users don't care how the output information is stored, but they
do notice when their computer slows down due to having thousands of files
under a single directory.

Instead of creating all the small files (which are usually just
intermediates used as input to something else), I wanted to combine all
those files into one, and add capabilities to other tools to be able to
extract single "files" from the combined file.  Thus, a relatively simple
(if not, entirely, optimal) solution is to merely _tarball_ all the
intermediate files, and extract the subset of needed files later.  Plus,
since no one needs the intermediate files, and I'm generating their
contents in memory anyway, it seems logical to simply build a tar archive
on-the-fly.

This library merely creates tar archive files based on data from memory
rather than file in the file system.

To get around searching the entire archive for a single file, I've added
a feature to create an index "file" in the archive.  This is stored as any
other file, but it is a CSV-style list of files in the archive (up to that
point).  The row in the list corresponds directly to the order of the
files in the archive.  Each row shows the file's name, real size in bytes,
the starting tar block (512 bytes/block), and the number of tar blocks
occupied by the file.  Thus, a tool may read the index from the end of the
archive (searching backwards 512 bytes at a time until it finds the string
".tarindex_*.csv") and extract the required file(s) using block offsets.

The index feature can be used multiple times on the same archive, and
future indexes will contain the full list of files (which includes any
intermediate indexes created before the current one).
