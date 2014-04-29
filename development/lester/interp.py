
"""
Lester Interpretor
"""



class parser( object ):

    def __init__( self ):
        self.comment = '#'
        self.escape  = '\\'
        self.group   = '()[]{}'
        self.string  = '"\''
        self.token   = ' '

        self._stack  = []
        self._text   = ''

    def is_open( self ):
        return len( self._text ) > 0

    def load( self, text ):
        self._text += text

    def get_token( self ):
        #raise NotImplemented()
        ## ZIH - temp
        return None



class product( object ):
    STATUS_OK   = 0
    STATUS_EXIT = 1
    def __init__( self, output, status = STATUS_OK ):
        self.status = product.STATUS_OK
        self.output = None
    def __str__( self ):
        return str( self.output )


class statement( object ):
    MODE_POSTFIX = 0
    MODE_PREFIX  = 1
    def __init__( self, tokens, mode = MODE_POSTFIX ):
        self.mode   = mode
        self.tokens = tokens


class context( object ):

    def __init__( self ):
        self._stack = []

    def execute( statement ):
        ## ZIH - temp
        pass


class interp( object ):


    def __init__( self ):
        self.context = context()
        self.parser  = parser()
        self.stack   = []


    def run( self, ifh, ofh, interactive = False ):
        if interactive == True:
            ofh.write( '> ' )
        line = ifh.readline()
        while line != '':
            result = self.enter_line( line )
            if result.status == product.STATUS_EXIT:
                break
            if interactive == True:
                ofh.write( '< ' + str( result ) + '\n> ' )
            line = ifh.readline()


    def enter_line( self, line ):
        self.parser.load( line )
        #stmt = statement( tokens )
        #result = self.context.execute( stmt )
        ## ZIH - temp
        p = product( 'not implemented' )
        if line.strip()[ 0 : 4 ] == 'exit':
            p.status = product.STATUS_EXIT
            return p
        return p
