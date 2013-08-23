#!/usr/bin/env python
##############################################################################
#
# dbschema.py
#
# Abstracts representation of a database's structure.  Allows modules to
# define entire schemas in a compact representation, and then build the
# appropriate queries to create, synchronize, backup, and restore the
# structure of a database.
#
# Schemas are free-form node graphs represented by nested dictionaries in
# Python, and stored as JSON files.
#
# The target database API for the generated queries is sqlite3.
#
##############################################################################


# Minimal example of the schema document structure
_example_schema = """
{
    "serial" : 20130612,
    "tables" : [
        {
            "name" : "example",
            "columns" : [
                {
                    "name" : "id",
                    "type" : "integer",
                    "null" : false
                },
                {
                    "name" : "name",
                    "type" : "text",
                    "default" : "",
                    "null" : false
                },
                {
                    "name" : "age",
                    "type" : "integer"
                },
                {
                    "name" : "compkey",
                    "type" : "integer"
                }
            ],
            "indexes" : [
                [ "name" ],
                [ "age", "compkey" ]
            ],
            "initdata" : [
                [ 1, "adam",    11, 8 ],
                [ 2, "baker",   12, 5 ],
                [ 3, "charlie", 13, 4 ]
            ]
        }
    ]
}
"""


#=============================================================================
class dbdict( dict ):
    """
    Extends the basic dictionary type to enable auto-loading existing
    dictionaries, and dot-style element access.
    """

    # Statically assign attribute access methods to dictionary access methods.
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    #=========================================================================
    def __init__( self, data = {} ):
        """
        Initialize the dbdict instance.
        """
        super( dbdict, self ).__init__( data )


#=============================================================================
class dbcolumn( dbdict ):

    #=========================================================================
    def __init__( self, table, schema, prikey = False ):
        super( dbcolumn, self ).__init__( schema )
        self.table = table
        self.prikey = prikey

    #=========================================================================
    def __str__( self ):
        s = '%s %s' % ( self.name, self.type )
        if ( 'null' in self ) and ( self.null == False ):
            s += ' not null'
        if 'default' in self:
            s += " default '%s'" % self.default
        if self.prikey == True:
            s += ' primary key'
        return s


#=============================================================================
class dbindex( list ):

    #=========================================================================
    def __init__( self, table, schema ):
        super( dbindex, self ).__init__( schema )
        self.table = table

    #=========================================================================
    def __str__( self ):
        return 'create index %s_i on %s (%s)' % (
            '_'.join( self ),
            self.table.name,
            ','.join( self )
        )


#=============================================================================
class dbtable( dbdict ):

    #=========================================================================
    def __init__( self, schema ):
        super( dbtable, self ).__init__( schema )
        self.dbcolumns = []
        self.dbindexes = []
        first = True
        for c in self.columns:
            self.dbcolumns.append( dbcolumn( self, c, first ) )
            first = False
        for i in self.indexes:
            self.dbindexes.append( dbindex( self, i ) )

    #=========================================================================
    def __str__( self ):
        return 'create table %s (\n  %s\n)' % (
            self.name,
            ',\n  '.join( [ str( c ) for c in self.dbcolumns ] )
        )

    #=========================================================================
    def get_column_names( self ):
        return [ c.name for c in self.dbcolumns ]

    #=========================================================================
    def get_columns( self ):
        return self.dbcolumns

    #=========================================================================
    def get_indexes( self ):
        return self.dbindexes

    #=========================================================================
    def get_init_data( self ):
        markers = ','.join( [ '?' ] * len( self.columns ) )
        q = 'insert into %s values (%s)' % ( self.name, markers )
        return { 'query' : q, 'values' : self.initdata }


#=============================================================================
class dbschema( dbdict ):

    #=========================================================================
    def __init__( self, schema ):
        super( dbdict, self ).__init__( schema )

    #=========================================================================
    def get_table_by_name( self, name ):
        for t in self.tables:
            if t[ 'name' ] == name:
                return dbtable( t )
        return None


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    import argparse
    import json

    # Create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Development and testing script for dbschema module.'
    )
    parser.add_argument(
        '-j', '--json', default = None,
        help = 'Load schema from JSON file for testing'
    )
    parser.add_argument(
        '-t', '--table', default = None,
        help = 'Specify table to display'
    )

    # The parser only wants the arguments (not the program "argument")
    args = parser.parse_args( argv[ 1 : ] )

    # See if the user wants to check out their own JSON schema
    if args.json != None:
        schema = json.load( arts.json )
    else:
        schema = json.loads( _example_schema )

    # Initialize the schema object
    dbs = dbschema( schema )

    # Check for a table to display
    if args.table != None:
        table_name = args.table
    else:
        table_name = 'example'

    # Demonstrate query generation
    table = dbs.get_table_by_name( table_name )
    print str( table )
    indexes = table.get_indexes()
    for i in indexes:
        print str( i )
    data = table.get_init_data()
    print data[ 'query' ]
    for d in data[ 'values' ]:
        print '  %s' % ','.join( [ str( v ) for v in d ] )

    # Return success.
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
