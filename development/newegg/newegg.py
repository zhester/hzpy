#!/usr/bin/env python
##############################################################################
#
# newegg.py
#
# Requires requests module (separate installation).
# Download Windows installer from here:
#   http://www.lfd.uci.edu/~gohlke/pythonlibs/
# Or, use your package manager similar to this:
#   > pip install requests
#
# Article that helped me get started:
#   http://www.bemasher.net/archives/1002
#
# TODO:
# - Implement navigation queries.
# - Figure out parametric specifiers.
# - Implement a way to export the data to CSV.
# - Implement a way to export the data to sqlite.
#
##############################################################################

import argparse
import json
import os

import requests


#=============================================================================
class item:

    #=========================================================================
    def __init__( self, data ):

        # Fields retrieved for any item
        self.ItemNumber       = 0
        self.FinalPrice       = 0.0
        self.Model            = None
        self.FreeShippingFlag = False
        # ... and there's a lot more

        for key in data:
            setattr( self, key, data[ key ] )


#=============================================================================
class category:

    #=========================================================================
    def __init__( self, parent, data ):
        self.parent          = parent
        self.categories      = []

        # Fields retrieved for any category
        self.CategoryID      = 0
        self.CategoryType    = 0
        self.Description     = None
        self.NodeId          = 0
        self.ShowSeeAllDeals = False
        self.StoreID         = 0
        for key in data:
            setattr( self, key, data[ key ] )
        self.navigation_query = 'Stores.egg/Navigation/%d/%d/%d' \
            % ( self.StoreID, self.CategoryID, self.NodeId )

    #=========================================================================
    def get_subcategories( self ):
        category_list = self.parent.get_json( self.navigation_query )
        self.categories = []
        for c in category_list:
            self.categories.append( category( self, c ) )
        return self.categories

    #=========================================================================
    def get_json( self, query ):
        """ Temporary redirect -- will refactor """
        return self.parent.get_json( query )


#=============================================================================
class store:
    """ Models a store resource from Newegg's system """

    #=========================================================================
    def __init__( self, neobj, data ):
        """ Create a new store object. """

        # Basic object initialization
        self.neobj           = neobj
        self.categories      = []

        # Fields retrieved for any store
        self.ShowSeeAllDeals = False
        self.StoreDepa       = None
        self.StoreID         = 0
        self.StoreTitle      = None
        self.Title           = None

        # Override fields with initialization values
        for key, value in data.iteritems():
            setattr( self, key, value )

        # Build a query to list categories in this store
        self.category_query = 'Stores.egg/Categories/%d' % self.StoreID

    #=========================================================================
    def get_categories( self ):
        """ Get the list of categories for this store. """
        category_list = self.neobj.get_json( self.category_query )
        self.categories = []
        for c in category_list:
            self.categories.append( category( self, c ) )
        return self.categories

    #=========================================================================
    def get_json( self, query ):
        """ Temporary redirect -- will refactor """
        return self.neobj.get_json( query )


#=============================================================================
class newegg:

    # The base URL of all application requests
    base_url = 'http://www.ows.newegg.com/'

    #=========================================================================
    def __init__( self ):
        self.stores = []

    #=========================================================================
    def get_categories( self, store_id ):
        cat_store = store( self, { 'StoreID' : store_id } )
        return cat_store.get_categories()

    #=========================================================================
    def get_from_subcategory( self, subcategory ):
        query = {
            "SubCategoryId": subcategory.CategoryID,
            "NValue":        '',
            "StoreDepaId":   subcategory.StoreID,
            "NodeId":        subcategory.NodeId,
            "BrandId":       -1,
            "PageNumber":    1,
            "CategoryId":    subcategory.parent.CategoryID
        }
        return self.post( 'Search.egg/Advanced', query )

    #=========================================================================
    def get_item( self, item_number ):
        return self.get_json( 'Products.egg/%d/Specification' % item_number )

    #=========================================================================
    def get_json( self, query ):
        req = requests.get( '%s%s' % ( newegg.base_url, query ) )
        if req.status_code != 200:
            return None
        return req.json()

    #=========================================================================
    def get_stores( self ):
        store_list = self.get_json( 'Stores.egg/Menus' )
        self.stores = []
        for s in store_list:
            self.stores.append( store( self, s ) )
        return self.stores

    #=========================================================================
    def get_subcategories( self, category_id ):
################# ZIH save old queries?
        #cat = category( self, {  } )
        return None

    #=========================================================================
    def post( self, target, query ):
        url = '%s%s' % ( newegg.base_url, target )
        req = requests.post( url, data = json.dumps( query ) )
        if req.status_code != 200:
            return None
        return req.json()


#=============================================================================
def dump_json( filename, data ):
    with open( filename, 'wb' ) as out:
        out.write(
            json.dumps( data, indent = 4, separators = ( ',', ' : ' ) )
        )

#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # Create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Development and testing script for Newegg module.'
    )
    parser.add_argument(
        '-r', '--proxy', default = None,
        help = 'Specify HTTP proxy as http://user:pass@proxy:port/'
    )
    parser.add_argument(
        '-s', '--store', default = None, type = int,
        help = 'List categories for a given store ID'
    )
    parser.add_argument(
        '-c', '--category', default = None, type = int,
        help = 'List subcategories for a given category ID'
    )
    parser.add_argument(
        '-g', '--get', default = None,
        help = 'Make a GET request'
    )
#    parser.add_argument(
#        '-p', '--post', default = None,
#        help = 'Make a POST request'
#    )
    parser.add_argument(
        '-d', '--dump', default = None,
        help = 'Dump JSON output to a file'
    )

    # The parser only wants the arguments (not the program "argument")
    args = parser.parse_args( argv[ 1 : ] )

    # Check for HTTP proxy given on command-line
    if args.proxy != None:
        os.environ[ 'HTTP_PROXY' ] = args.proxy

    # Create a Newegg object
    ne = newegg()

    # Check for a GET request
    if args.get != None:
        data = ne.get_json( args.get )
        if args.dump != None:
            dump_json( args.dump, data )
            print 'JSON written to %s.' % args.dump
        else:
            print json.dumps( data, indent = 4, separators = ( ',', ' : ' ) )

    # Check for a category request
    elif args.category != None:
        categories = ne.get_subcategories( args.category )
        if args.dump != None:
            dump_json( args.dump, categories )
            print 'JSON written to %s.' % args.dump
        else:
            for category in categories:
                print '%4d: %s' % ( category.CategoryID, category.Description )

    # Check for a store request
    elif args.store != None:
        categories = ne.get_categories( args.store )
        if args.dump != None:
            dump_json( args.dump, categories )
            print 'JSON written to %s.' % args.dump
        else:
            for category in categories:
                print '%4d: %s' % ( category.CategoryID, category.Description )

    # Assume base request
    else:
        stores = ne.get_stores()
        if args.dump != None:
            dump_json( args.dump, stores )
            print 'JSON written to %s.' % args.dump
        else:
            for store in stores:
                print '%4d: %s' % ( store.StoreID, store.Title )

    # Return success.
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
