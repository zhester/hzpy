#!/usr/bin/env python
##############################################################################
#
# neweggdb.py
#
# Fetches data from Newegg's servers and stores it in a local database for
# analysis and cost estimation across a large number of products.
#
##############################################################################

import sqlite3

import dbschema
import newegg


# Database structure
_schema = """
{
    "serial" : 20130612,
    "tables" : [
        {
            "name" : "stores",
            "columns" : [
                { "name" : "StoreID",    "type" : "integer" },
                { "name" : "Title",      "type" : "text"    },
                { "name" : "StoreDepa",  "type" : "text"    }
            ]
        },
        {
            "name" : "categories",
            "columns" : [
                { "name" : "CategoryID",   "type" : "integer" },
                { "name" : "parent_id",    "type" : "integer" },
                { "name" : "StoreID",      "type" : "integer" },
                { "name" : "NodeId",       "type" : "integer" },
                { "name" : "CategoryType", "type" : "integer" },
                { "name" : "Description",  "type" : "text"    }
            ],
            "indexes" : [
                "parent_id",
                "StoreID"
            ]
        },
        {
            "name" : "items",
            "columns" : [
                { "name" : "id",            "type" : "integer" },
                { "name" : "ItemNumber",    "type" : "text"    },
                { "name" : "Title",         "type" : "text"    },
                { "name" : "Rating",        "type" : "integer" },
                { "name" : "TotalReviews",  "type" : "text"    },
                { "name" : "FinalPrice",    "type" : "text"    },
                { "name" : "OriginalPrice", "type" : "text"    },
                { "name" : "Model",         "type" : "text"    }
            ],
            "indexes" : [
                "ItemNumber"
            ]
        },
        {
            "name" : "key_data",
            "columns" : [
                { "name" : "id",          "type" : "integer" },
                { "name" : "item_id",     "type" : "integer" },
                { "name" : "key_type_id", "type" : "integer" },
                { "name" : "Key",         "type" : "text"    },
                { "name" : "Value",       "type" : "text"    }
            ],
            "indexes" : [
                "item_id",
                "key_type_id"
            ]
        },
        {
            "name" : "key_types",
            "columns" : [
                { "name" : "id",   "type" : "integer" },
                { "name" : "name", "type" : "text"    }
            ],
            "initdata" : [
                [ 1, "Model" ],
                [ 2, "Specifications" ],
                [ 3, "Warranty" ]
            ]
        }
    ]
}
"""


#=============================================================================
class neweggdb:

    def __init__( self, dbfile = None ):
        if type( dbfile ) is str:
            self.dbfile = dbfile
        else:
            self.dbfile = 'neweggdb.sqlite'
        self.db = sqlite3.connect( self.dbfile )
        self._check_db_init()

    def _check_db_init( self ):
        cursor = self.db.cursor()
        cursor.execute( "select name from sqlite_master where type='table'" )
        


#=============================================================================
def main( argv ):
    """ Script execution entry point """



    # return success
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
