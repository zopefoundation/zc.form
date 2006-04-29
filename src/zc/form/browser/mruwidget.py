##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""source input widget with most recently used (MRU) value support

$Id: mruwidget.py 3677 2005-10-19 07:10:22Z fred $
"""
import cgi

import persistent.list
from BTrees import OOBTree

import zope.app.form.interfaces
import zope.app.form.browser.interfaces
from zope.app import zapi 
from zope.app.form.browser.source import SourceInputWidget
from zope.schema.interfaces import ISourceQueriables, ValidationError
import zope.annotation.interfaces

import zc.resourcelibrary

class MruSourceInputWidget(SourceInputWidget):
    ANNOTATION_KEY = 'zc.form.browser.mruwidget'

    def hasInput(self):
        return self.name+'.displayed' in self.request

    def getMostRecentlyUsedTokens(self):
        """Get a sequence of the most recently used tokens (most recent first).
        """
        key = self.name # TODO should the key be more specific?
        principal = self.request.principal
        annotations = zope.annotation.interfaces.IAnnotations(principal)

        annotation = annotations.get(self.ANNOTATION_KEY)
        if annotation is None:
            annotations[self.ANNOTATION_KEY] = annotation = OOBTree.OOBTree()

        tokens = annotation.get(key)
        if tokens is None:
            tokens = annotation[key] = persistent.list.PersistentList()

        return tokens
        
    def getMostRecentlyUsedTerms(self):
        """Get a sequence of the most recently used terms (most recent first).
        """
        tokens = self.getMostRecentlyUsedTokens()
        terms = zapi.getMultiAdapter((self.source, self.request),
                                     zope.app.form.browser.interfaces.ITerms)
        mru = []
        for token in tokens:
            try:
                value = terms.getValue(token)
                term = terms.getTerm(value)
            except LookupError:
                continue

            mru.append(term)

        return mru

    def addMostRecentlyUsedTerm(self, term):
        """Add a term to the list of MRU values.
        """
        tokens = self.getMostRecentlyUsedTokens()
        try:
            tokens.remove(term.token)
        except ValueError:
            pass

        tokens.insert(0, term.token)
        del tokens[10:] # TODO should this constant be configurable?

    def queryViewApplied(self):
        """Determine if a query view was used to set the value of the field.
        """
        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                return True
    
    def __call__(self):
        zc.resourcelibrary.need('zc.form.mruwidget')
        result = ['<div class="value">']
        value = self._value()
        field = self.context
        term = None
        if value != field.missing_value:
            try:
                term = self.terms.getTerm(value)
            except LookupError:
                pass # let the "missing" term value from above be used
            else:
                self.addMostRecentlyUsedTerm(term)

        mru_terms = self.getMostRecentlyUsedTerms()
        queries_id = self.name + '.queries'

        # should the query views be visible?
        if (self.request.form.get(queries_id+'.visible') == 'yes'
        and not self.queryViewApplied()) or not mru_terms:
            queries_style = ''
            queries_visible = 'yes'
        else:
            queries_style = 'display: none;'
            queries_visible = 'no'

        result.append('<input type="hidden" name="%s.visible" '
                      'id="%s.visible" value="%s">' 
                      % (queries_id, queries_id, queries_visible))

        if mru_terms:
            result.append('<select name="%s" id="%s">' %
                          (self.name, self.name))
            for mru_term in mru_terms:
                if term is not None and mru_term.token == term.token:
                    selected = ' selected="selected"'
                else:
                    selected = ''
                result.append('  <option value="%s"%s>%s</option>'
                              % (cgi.escape(mru_term.token), 
                                 selected, 
                                 cgi.escape(mru_term.title)))

            result.append('</select>')

            result.append('  <input type="button" '
              'name="%s.mru_expand_button" ' % self.name +
              'onclick="javascript:zc_mruwidget_toggleQueriesDisplay(\'%s\')"'
              % queries_id + ' value="...">')

        result.append('  <input type="hidden" name="%s.displayed" value="y">'
                      % self.name)
        
        result.append('  <div class="queries" id="%s" style="%s">'
                      % (queries_id, queries_style))
        for name, queryview in self.queryviews:
            result.append('    <div class="query">')
            result.append('      <div class="queryinput">')
            result.append(queryview.render(name))
            result.append('      </div> <!-- queryinput -->')

            qresults = queryview.results(name)
            if qresults:
                result.append('      <div class="queryresults">\n%s' %
                              self._renderResults(qresults, name))
                result.append('      </div> <!-- queryresults -->')
            result.append('    </div> <!-- query -->')
        result.append('  </div> <!-- queries -->')
        result.append('</div> <!-- value -->')
        return '\n'.join(result)
