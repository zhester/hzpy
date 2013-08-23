#!/usr/bin/python
##############################################################################
#
#   MTar.py
#
#   Zac Hester
#   2011-12-22
#
#   This behaves similarly to Python's built-in tar support.  However, this is
#   a simplified library that writes extremely primitive tar files.  The
#   reason this library exists is to make it easier (on the programmer and
#   system resources) to write data directly from memory into a tar archive.
#   There is no need to write intermediate files to the file system, then
#   run the tar tools on those files.
#
#   Once an archive is created with this library, any tar program or Python's
#   tarfile module can be used to read and extract the archived files.
#
#   See the main procedure for an example on using this library.
#
##############################################################################

import math, operator, time

#=============================================================================
# Manage information about an archived file.
#=============================================================================
class MTarInfo:

    def __init__(self, filename, **kw):
        """
        Create a new MTarInfo object.
        @param filename The name of the "file" to store in an archive.
        @param **kw
            mode    Octal file mode (default: 0600)
            uid     Numeric user ID (default: 0)
            gid     Numeric group ID (default: 0)
            size    Size of file in bytes (default: 0)
            mtime   Last modified time (default: current time)
        """
        self.filename = filename;
        self.fields = {};
        for k,v in kw.items():
            self[k] = v;

    def __setitem__(self, k, v):
        """
        Set/update an info field for this object.  See the list of keyword
        arguments used in the constructor for a valid list of object keys.
        """
        self.fields[k] = v;

    def __getitem__(self, k):
        """
        Get an info field from this object.  See the list of keyword
        arguments used in the constructor for a valid list of object keys.
        If the field has not been set by the object's user, this will NOT
        report the default value of that field.  Instead, it will report
        None to indicate that it has not been explicitly set.
        """
        if k in self.fields:
            return self.fields[k];
        return None;

    def __str__(self):
        """
        The string representation of the object is a tar format file header.
        """

        # Check "file" size.
        size = self['size'] if self['size'] else 0;

        # Check mode.
        mode = self['mode'] if self['mode'] else 0600;

        # Check user/group IDs.
        uid = self['uid'] if self['uid'] else 0;
        gid = self['gid'] if self['gid'] else 0;

        # Check mod time.
        mtime = self['mtime'] if self['mtime'] else time.time();

        # The file name is 100 characters, null padded.
        header = self.filename + ('\0' * (100 - len(self.filename)));

        # File mode is zero-filled octal mode.
        header += ('%07o\0' % mode);

        # User and group IDs.
        header += ('%07o\0' % uid) + ('%07o\0' % gid);

        # File size and modified time.
        header += ('%011o\0' % size) + ('%011o\0' % mtime);

        # The checksum field is temporarily filled with spaces.
        header += (' ' * 8);

        # Set the link indicator to be a normal file.
        header += '0';

        # Null pad header to 512 bytes.
        header += '\0' * (512 - len(header));

        # Calculate the checksum, and update the checksum field.
        header = header[:148]                                                \
            + ('%06o\0 ' % MTarInfo.checksum(header))                        \
            + header[156:];

        # Return the header.
        return header;

    def __repr__(self):
        """
        Represent the object as a string.
        """
        return self.__str__();

    @staticmethod
    def checksum(data):
        """
        Calculate a simple additive checksum of all bytes in a string.
        """
        return reduce(operator.add, map(ord, data));


#=============================================================================
# Create a tar file from in-memory data.
#=============================================================================
class MTar:

    def __init__(self, filename):
        """
        Create a new MTar object, and open a new archive file.
        @param filename The name of the new archive file
        """
        self.filename = filename;
        self.fh = open(filename, 'wb');
        self.nblocks = 0;
        self.files = [];
        self.nindexes = 0;

    def __del__(self):
        """
        Perform any cleanup for the object before it is deleted.
        """
        self.close();

    @staticmethod
    def open(filename):
        """
        Convenience function for creating/opening a new MTar object.  This is
        provided to make it obvious that a file is being created during
        instantiation.
        @param filename The name of the new archive file
        """
        return MTar(filename);

    def close(self):
        """
        Close the archive file.
        """
        if self.fh:
            self.fh.close();

    def add(self, filename, data):
        """
        Add a new file to the archive.
        @param filename The name of the file to write
        @param data The data (as a string) to write to the archive
        """

        # The string length is used as the "file" size.
        filesize = len(data);

        # Calculate the number of blocks needed for this file.
        nblocks = int(math.ceil(filesize / 512.0));

        # Add to the list of files in this archive.
        self.files.append([filename, filesize, (self.nblocks + 1), nblocks]);

        # Update the total number of blocks.
        self.nblocks += nblocks + 1;

        # Create an MTarInfo object to build the header.
        theader = MTarInfo(filename, size=filesize);

        # Calculate the amount of block padding needed for the last block.
        nullpad = 512 - (filesize % 512);

        # Write the header, data, and null pad.
        self.fh.write(str(theader) + data + ('\0' * nullpad));

    def addIndex(self):
        """
        Write an index file to the current point in the tar file.  This is
        intended for more advanced tools to more quickly find individual
        files without searching the entire archive.  For small archives, this
        may not provide a significant improvement in performance.
        """

        # Create the index.
        data = "\n".join(map(lambda f: ','.join(map(str, f)), self.files));

        # Add the index as a new file.
        self.add(('.tarindex_%d.csv' % self.nindexes), data);
        self.nindexes += 1;


#-----------------------------------------------------------------------------
# The main procedure used when the class isn't being used as a library.
#-----------------------------------------------------------------------------
def main(argc, argv):

    # This test code creates three random strings, and stores them as files in
    #   a tar archive.
    import random
    tf = MTar.open('test.tar');
    for i in range(3):
        data = '';
        for j in range(500):
            if (j > 0) and ((j % 64) == 0):
                data += "\n";
            data += chr(random.randint(32,126));
        tf.add(('data_%d.txt' % i), data);
    tf.addIndex();
    tf.close();

    # Return to the shell with success.
    return 0;


# If the script is executed directly, run the main procedure.
if __name__ == "__main__":
    import sys
    sys.exit(main(len(sys.argv), sys.argv));
