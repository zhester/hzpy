Change Default Python on Windows
================================

Lately, I've found I need to work with Python code spread across
multiple interpretors.  My computer at work has four interpretors installed:

 - 2.6 (for one or two legacy scripts)
 - 2.7: 32 bit (to be able to use a lot of addons that don't support
   64-bit Python)
 - 2.7: 64 bit (everyday use)
 - 3.2: 64 bit (updating code, working with newer APIs)

In a Windows environment there are three ways to invoke a Python script,
and they can all be distinct from each other:

 - Invoke the interpretor explicitly:
   `C:\Python27\python.exe script.py`
 - Invoke the interpretor implicitly (depends on PATH):
   `python.exe script.py`
 - Invoke the script directly (depends on file associations):
   `script.py`

In normal environments, the script can control which interpretor is used
when invoked directly via "shebang" shell conventions.  The stock command
interpretor (shell) in Windows, however, uses the file association
database to determine the path to the application that should be used
to execuate a script.  Unfortunately, modifying this database is not
always easy.  The GUI is tedious, and not designed for repeatedly changing
an existing entry (it's good at adding new entries).  The built-in
commands in cmd.exe (assoc and ftype) work decently, but I rather not have
to remember (and type) a lot of paths and command syntaxes.

That's where I decided to write this script.  It got a bit more complicated
than I expected, but it works well to make changing things around (and
putting things back when you're done), and it's fast and easy to remember.

If you decide to give this a try, type `chpy.py help` before
you do anything else:

Usage Examples
--------------

  chpy.py help                      - Display this information.
  chpy.py current                   - Display the current association.
  chpy.py restore                   - Restore the original assocation.
  chpy.py 27                        - Associate a 2.7 installation.
  chpy.py Python27                  - Associate a 2.7 installation.
  chpy.py C:\Python27\python.exe    - Specify a complete path to use.
  C:\Python27\python.exe chpy.py    - Use the invoking interpretor.

*Note:* This script is not compatible with Python 3.x.
You can still change the file association to and from 3.x, but you will
need to explicitly invoke a 2.6+ interpretor rather than attempting to
execute the script directly when 3.x is the current association.

The following example changes the file association to use a 3.2
installation (assuming the currently associated interpretor is 2.6+).
It then changes to a 2.7 installation (passing no arguments to the
script means it will use whatever interpretor is running the script).

  C:\scripts>chpy.py 32
  C:\scripts>C:\Python27\python.exe chpy.py
