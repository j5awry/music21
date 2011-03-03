#-------------------------------------------------------------------------------
# Name:         text.py
# Purpose:      music21 classes for text processing
#
# Authors:      Michael Scott Cuthbert
# Authors:      Christopher Ariza
#
# Copyright:    (c) 2009-2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------
'''Utility routines for processing text in scores and other musical objects. 
'''

import doctest, unittest
import music21 # needed to properly do isinstance checking


# using ISO 639-1 Code from here:
# http://www.loc.gov/standards/iso639-2/php/code_list.php
# nice article reference here:
# http://en.wikipedia.org/wiki/Article_(grammar)
articleReference = {
    # arabic
    'ar' : ['al-'],
    # english
    'en' : ['the', 'a', 'an'],
    # german
    'de' : ['der', 'die', 'das', 'des', 'dem', 'den', 'ein', 'eine', 'einer', 'einem', 'einen'],
    # dutch
    'nl' : ['de', 'het', 'een'],
    # spanish
    'es' : ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
    # portuguese
    'pt' : ['o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas'],
    # french
    'fr' : ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'de la', 'des'],
    # italian
    'it' : ['il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una', 'del', 'dello', 'della', 'dei', 'degli', 'delle'],
    }

#-------------------------------------------------------------------------------
def assembleLyrics(streamIn):
    '''Concatenate text from a stream.
    '''
    word = []; words = []
    noteStream = streamIn.flat.notes
    for n in noteStream:
        for lyricObj in n.lyrics: # a list of lyric objs
            #print lyricObj, lyricObj.syllabic, lyricObj.text
            # need to match case of non-defined syllabic attribute
            if lyricObj.syllabic in ['begin', 'middle']:
                word.append(lyricObj.text)
            elif lyricObj.syllabic in ['end', 'single', None]:
                word.append(lyricObj.text)
                words.append(''.join(word))
                word = []
    return ' '.join(words)
        

def prependArticle(src, language=None):
    '''Given a text string, if an article is found in a trailing position with a comma, place the article in front and remove the comma. 

    >>> from music21 import *
    >>> text.prependArticle('Ale is Dear, The')
    'The Ale is Dear'
    >>> text.prependArticle('Ale is Dear, The', 'en')
    'The Ale is Dear'
    >>> text.prependArticle('Ale is Dear, The', 'it')
    'Ale is Dear, The'
    >>> text.prependArticle('Combattimento di Tancredi e Clorinda, Il', 'it') 
    'Il Combattimento di Tancredi e Clorinda'
    '''
    if ',' not in src: # must have a comma
        return src

    if language == None: # get all languages?
        ref = []
        for key in articleReference.keys():
            ref += articleReference[key]
    else:
        ref = articleReference[language]

    trailing = src.split(',')[-1].strip()
    match = None
    for candidate in ref:
        if trailing.lower() == candidate:
            match = trailing
            break
    if match != None:
        # recombine everything except the last comma split
        return match + ' ' + ','.join(src.split(',')[:-1])
    else: # not match
        return src


def postpendArticle(src, language=None):
    '''Given a text string, if an article is found in a leading position, place it at the end with a comma. 

    >>> from music21 import *
    >>> text.postpendArticle('The Ale is Dear')
    'Ale is Dear, The'
    >>> text.postpendArticle('The Ale is Dear', 'en')
    'Ale is Dear, The'
    >>> text.postpendArticle('The Ale is Dear', 'it') 
    'The Ale is Dear'
    >>> text.postpendArticle('Il Combattimento di Tancredi e Clorinda', 'it') 
    'Combattimento di Tancredi e Clorinda, Il'
    '''
    if ' ' not in src: # must have at least one space
        return src

    if language == None: # get all languages?
        ref = []
        for key in articleReference.keys():
            ref += articleReference[key]
    else:
        ref = articleReference[language]
    
    leading = src.split(' ')[0].strip()
    match = None
    for candidate in ref:
        if leading.lower() == candidate:
            match = leading
            break
    if match != None:
        # recombine everything except the last comma split
        return ' '.join(src.split(' ')[1:]) + ', %s' % match
    else: # not match
        return src




#-------------------------------------------------------------------------------
class TextFormatException(music21.Music21Exception):
    pass

class TextFormat(object):
    '''An object for defining text formatting. This object can be multiple-inherited by object that storage and i/o of text settings. 
    '''
    def __init__(self):
        # these could all be in a text s
        self._justify = None
        self._style = None
        self._size = None
        self._letterSpacing = None

        # TODO: a comma separated list; can also be generic font styles
        self._fontFamily = None 

    def _getJustify(self):
        return self._justify    
    
    def _setJustify(self, value):
        if value.lower() not in ['left', 'center', 'right']:
            raise TextFormatException('Not a supported justification: %s' % value)
        self._justify = value.lower()

    justify = property(_getJustify, _setJustify, 
        doc = '''Get or set the the justification.

        >>> from music21 import *
        >>> tf = TextFormat()
        >>> tf.justify = 'center'
        >>> tf.justify
        'center'
        ''')

    def _getStyle(self):
        return self._style    
    
    def _setStyle(self, value):
        if value.lower() not in ['italic', 'normal', 'bold', 'bolditalic']:
            raise TextFormatException('Not a supported justification: %s' % value)
        self._style = value.lower()

    style = property(_getStyle, _setStyle, 
        doc = '''Get or set the style, as normal, italic, bold, and bolditalic.

        >>> from music21 import *
        >>> tf = TextFormat()
        >>> tf.style = 'bold'
        >>> tf.style
        'bold'
        ''')


    def _getSize(self):
        return self._size    
    
    def _setSize(self, value):
        try:
            value = float(value)
        except (ValueError):
            raise TextFormatException('Not a supported size: %s' % value)
        self._size = value

    size = property(_getSize, _setSize, 
        doc = '''Get or set the style, as normal, italic, bold, and bolditalic.

        >>> from music21 import *
        >>> tf = TextFormat()
        >>> tf.size = 20
        >>> tf.size
        20.0
        ''')


    def _getLetterSpacing(self):
        return self._letterSpacing    
    
    def _setLetterSpacing(self, value):
        if value != 'normal':            
            # convert to number
            try:
                value = float(value)
            except (ValueError):
                raise TextFormatException('Not a supported size: %s' % value)

        self._letterSpacing = value

    letterSpacing = property(_getLetterSpacing, _setLetterSpacing, 
        doc = '''Get or set the letter spacing.

        >>> from music21 import *
        >>> tf = TextFormat()
        >>> tf.letterSpacing = 20
        >>> tf.letterSpacing
        20.0
        >>> tf.letterSpacing = 'normal'
        ''')


    def getMXLParameters(self):
        '''Return a dictionary with the attribute of this object notated as needed for MusicXML output

        >>> from music21 import *
        >>> tf = TextFormat()
        >>> tf.style = 'bolditalic'
        >>> tf.getMXLParameters()['font-weight']
        'bold'
        >>> tf.getMXLParameters()['font-style']
        'italic'
        '''
        post = {}
        post['justify'] = self._justify

        post['font-style'] = 'normal'
        post['font-weight'] = 'normal'
        if self._style == 'normal':
            pass            
        elif self._style == 'italic':
            post['font-style'] = 'italic'
        elif self._style == 'bold':
            post['font-weight'] = 'bold'
        elif self._style == 'bolditalic':
            post['font-weight'] = 'bold'
            post['font-style'] = 'italic'

        post['font-size'] = self._getSize()
        post['letter-spacing'] = self._getLetterSpacing()

        # font family not yet being specified
        return post


#-------------------------------------------------------------------------------
class Test(unittest.TestCase):

    def runTest(self):
        pass

    def testBasic(self):
        from music21 import converter, corpus

        a = converter.parse(corpus.getWork('haydn/opus74no2/movement4.xml'))
        post = assembleLyrics(a)
        self.assertEqual(post, '') # no lyrics!

        a = converter.parse(corpus.getWork('luca/gloria'))
        post = assembleLyrics(a)
        self.assertEqual(post.startswith('Et in terra pax hominibus bone voluntatis'), True) 



if __name__ == "__main__":
    music21.mainTest(Test)


#------------------------------------------------------------------------------
# eof





