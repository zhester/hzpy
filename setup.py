"""
hzpy Setup Script
"""

#=============================================================================
conf = {
    'name'             : 'hzpy',
    'version'          : '0.0.0',
    'author'           : 'Zac Hester',
    'author_email'     : 'zac.hester@gmail.com',
    'license'          : 'BSD 2-Clause',
    'url'              : 'https://github.com/zhester/hzpy',
    'package_dir'      : { '' : 'modules' },
    'py_modules'       : [ 'hzpy' ],
    'scripts'          : [ 'utilities/dbrun.py' ],
    'description'      : 'Reusable modules, utilities, examples and references.',
    'long_description' : """
This is a personal project for keeping track of a large investment in reusable
Python modules and other code.  Feel free to use this code according to the
included LICENSE.

The repository is available from Github:
https://github.com/zhester/hzpy

Documentation is typically inline with each module, and varies from
comprehensive to somewhat lacking.  If you find something you find
interesting, and want to know more about it, feel free to email me.
"""
}


#=============================================================================
if __name__ == "__main__":

    from distutils.core import setup

    setup( **conf )

