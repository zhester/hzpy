#!/usr/bin/python
##############################################################################
#
#   MTarGet.py
#
#   Zac Hester
#   2011-12-22
#   Version: 0.0.0
#   Python: 2.6
#
#   Helper class to extract specific files from an indexed tar archive
#   created by the MTar library using the index feature.
#
##############################################################################

import os

#=============================================================================
# MTarGet
#=============================================================================
class MTarGet:

    def __init__(self, filename):
        """
        Create a new MTarGet object.
        @param filename The name of the archive from which to read
        """
        self.filename = filename;
        self.files = [];

        # Use the reported file size to bound our search.
        size = os.path.getsize(filename);

        # Open the specified archive.
        fh = open(filename, 'rb');

        # Make sure the archive was opened properly.
        if fh:

            # Set a position offset in the file.
            pos = 0;

            # File search loop.
            while True:

                # Move the position back 512 bytes.
                pos -= 512;

                # Make sure we're not reading past the beginning of the file.
                if (size + pos) >= 0:

                    # Move the file read head to the previous block.
                    fh.seek(pos, os.SEEK_END);

                    # Read 10 bytes to look for a generic file name.
                    chunk = fh.read(10);

                    # The MTar library uses an incrementing index file name.
                    if chunk == '.tarindex_':

                        # Construct the tar header for this file.
                        header = chunk + fh.read(502);

                        # Extract and convert the tar file's size field.
                        rsize = isize = int(header[124:135], 8);

                        # Index read loop.
                        while True:

                            # Pull a line from the index file.
                            line = fh.readline();

                            # Decrement against the file size.
                            rsize -= len(line);

                            # Parse and store an index record for a file.
                            self.files.append(
                                line.strip('\n\0').rsplit(',', 4));

                            # Stop reading at the end of the index.
                            if rsize <= 0:
                                break;

                        # Finish searching the archive at the index.
                        break;

                # No index found in archive, leave read loop.
                else:
                    break;

            # Close the archive.
            fh.close();

    def getIndex(self):
        """
        Provide the complete list of files in the archive with index details.
        @return A list of lists containing each file's name, size, archive
            block position, and number of blocks (512 bytes/block)
        """
        return self.files;

    def getPosition(self, index):
        """
        Calculate the byte position (offset and length) of a file in the
        archive for a given index.
        @param index The index of the file in the archive (0 = first file)
        @return A tuple containing the byte offset and length of the file
        """
        if index < len(self.files):
            return ((int(self.files[index][2]) * 512),
                int(self.files[index][1]));
        return None;

    def getString(self, index):
        """
        Extracts the file contents as a string based on the file's index in
        the tar archive.
        @param index The index of the file in the archive (0 = first file)
        @return A string containing all the data in the file
        """

        # Get the file's coordinates in the archive.
        fi = self.getPosition(index);

        # Verify it is a valid index.
        if fi != None:

            # Open the archive.
            fh = open(self.filename, 'rb');

            # Move the read head to the start of the file.
            fh.seek(fi[0]);

            # Read in the proper number of bytes.
            data = fh.read(fi[1]);

            # Close the archive.
            fh.close();

            # Return the file contents.
            return data;

        # The index doesn't appear valid.
        return None;



#-----------------------------------------------------------------------------
# The main procedure
#-----------------------------------------------------------------------------
def main(argc, argv):

    # Create a tar get object.
    tg = MTarGet('test.tar');

    # Pull the index for the archive.
    fi = tg.getIndex();

    # Use the index to display some details about each file in the archive.
    for i in range(len(fi)):
        p = tg.getPosition(i);
        if p != None:
            print '%s: 0x%04X, 0x%04X' % (fi[i][0], p[0], p[1]);

    # Pull the contents of the first file, and display them.
    data = tg.getString(0);
    print '%s is %d bytes long, and contains...' % (fi[0][0], len(data));
    print data;

    # Return to the shell with success.
    return 0;


# If the script is executed directly, run the main procedure.
if __name__ == "__main__":
    import sys
    sys.exit(main(len(sys.argv), sys.argv));
