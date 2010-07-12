#!/usr/bin/env python

import ternip
import nltk.tokenize
import nltk.tag
import xml.dom.minidom
from collections import defaultdict

class xml_doc:
    """
    An abstract base class which all XML types can inherit from. This implements
    almost everything, apart from the conversion of timex objects to and from
    timex tags in the XML. This is done by child classes 
    """
    
    @staticmethod
    def _add_words_to_node_from_sents(doc, node, sents, tok_offsets=None):
        """
        Uses the given node and adds an XML form of sents to it. The node
        passed in should have no children (be an empty element)
        """
        
        # Just add text here, then leave it up to reconcile to add all other
        # tags
        
        for i in len(sents):
            
            for j in len(sent):
                (tok, pos, ts) = sents[i][j]
                
                # Do we know what token offsets are in order to reinstate them?
                if tok_offsets is not None:
                    # Add whitespace between tokens if needed
                    while s_offset < tok_offsets[i][j]:
                        s_tag.appendChild(doc.createTextNode(' '))
                        s_offset += 1
                
                # Add the text
                s_tag.appendChild(doc.createTextNode(tok))
                
                # If we're not using token offsets, assume a single space is
                # what's used
                if tok_offsets is None:
                    s_tag.appendChild(doc.createTextNode(' '))
                else:
                    # Increase our current sentence offset
                    s_offset += len(tok)
        
        node.normalize()
    
    @staticmethod
    def create(sents, tok_offsets=None, add_S=False, add_LEX=False, pos_attr=False):
        """
        Override this to build a document from internal representation only.
        The output this produces is pretty generic, as can be expected at this
        high level. The root node is called 'root' and no DTD is used.
        
        sents is the [[(word, pos, timexes), ...], ...] format.
        
        tok_offsets is used to correctly reinsert whitespace lost in
        tokenisation. It's in the format of a list of lists of integers, where
        each integer is the offset from the start of the sentence of that token.
        If set to None (the default), then a single space is assumed between
        all tokens.
        
        If add_S is set to something other than false, then the tags to indicate
        sentence boundaries are added, with the name of the tag being the value
        of add_S
        
        add_LEX is similar, but for token boundaries
        
        pos_attr is similar but refers to the name of the attribute on the LEX
        (or whatever) tag that holds the POS tag.
        """
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, 'root', None)
        
        # Create a document with just text nodes
        x = xml_doc(xml_doc._add_words_to_node_from_sents(doc, doc.documentElement, sents, tok_offsets), doc.documentElement)
        
        # Now reconcile the S, LEX and TIMEX tags
        x.reconcile(sents, add_S, add_LEX, pos_attr)
        
        return x
    
    def __init__(self, file, nodename=None, has_S=False, has_LEX=False, pos_attr=False):
        """
        Passes in an XML document (as one consecutive string) which is used
        as the basis for this object.
        
        Alternatively, you can pass in an xml.dom.Document class which means
        that it's not parsed. This is used by the static create function.
        
        Node name is the name of the "body" of this document to be considered.
        If set to None (it's default), then the root node is considered to be
        the document body.
        
        has_S means that the document uses XML tags to mark sentence boundaries.
        This defaults to False, but if your XML document does, you should set it
        to the name of your sentence boundary tag (normally 'S').
        
        has_LEX is similar to has_S, but for token boundaries. Again, set this
        to your tag for token boundaries (not as common, but sometimes it's
        'lex')
        
        pos_attr is the name of the attribute on your LEX (or whatever) tags
        that indicates the POS tag for that token.
        
        The tagger needs tokenised sentences and tokenised and POS tagged tokens
        in order to be able to tag. If the input does not supply this data, the
        NLTK is used to fill the blanks. If this input is supplied, it is
        blindly accepted as reasonably sensible. If there are tokens which are
        not annotated (for whatever reason), then alignment between XML nodes
        and the results of the tagging may fail and give undesirable results.
        Similarly, if tokens are embedded inside other tokens, this will also
        error in likely undesirable way, and such a tagging is likely erroneous.
        """
        
        if isinstance(file, xml.dom.minidom.Document):
            self._xml_doc = file
        else:
            self._xml_doc = xml.dom.minidom.parseString(file)
        
        if nodename is None:
            self._xml_body = self._xml_doc.documentElement
        else:
            tags = self._xml_doc.getElementsByTagName(nodename)
            if len(tags) != 1:
                raise bad_node_name_error()
            self._xml_body = tags[0]
        
        self._has_S = has_S
        self._has_LEX = has_LEX
        self._pos_attr = pos_attr
    
    def _strip_tags(self, doc, tagname, node):
        """
        Recursively remove a tag from this node
        """
        
        # Recursive step - depth-first search
        for child in node.childNodes:
            
            # Get the list of nodes which replace this one (if any)
            rep = self._strip_tags(doc, tagname, child)
            
            if len(rep) == 1:
                # If it's a single node that's taking the place of this one (e.g.,
                # if there was no change, or a timex tag that only had some text
                # inside it), but only if the node's changed
                if rep[0] is not child:
                    node.replaceChild(rep[0], child)
            else:
                # There were multiple child nodes, need to insert all of them
                # where in the same location, in order, where their parent
                # node was. Unfortunately replaceChild can't do replacement
                # of a node with multiple nodes.
                before = child.nextSibling
                node.removeChild(child)
                for new_node in rep:
                    node.insertBefore(new_node, before)
                node.normalize()
        
        # Base step
        if node.nodeType == node.ELEMENT_NODE and node.tagName == tagname:
            return [child for child in node.childNodes]
        else:
            return [node]
    
    def strip_timexes(self):
        """
        Strips all timexes from this document. Useful if we're evaluating the
        software - we can just feed in the gold standard directly and compare
        the output then.
        """
        self._strip_tags(self._xml_doc, self._timex_tag_name, self._xml_body)
    
    def _get_text_recurse(self, element, until = None):
        """
        Given an element, returns only the text only nodes in it concatenated
        together, up until the node specified by until is reached.
        """
        
        cont = True
        text = ""
        
        if element == until:
            # Check if we need to stop
            cont = False
        elif element.nodeType == element.TEXT_NODE:
            # If it's a text node, add the data, and no more recursion
            text += element.data
        else:
            # depth-first search, recursive step
            for child in element.childNodes:
                (cont, t) = self._get_text_recurse(child, until)
                text += t
                if not cont:
                    break
            
        return (cont, text)
    
    def _get_text(self, element, until = None):
        """
        Given an element, returns only the text only nodes in it concatenated
        together, up until the node specified by until is reached.
        """
        return self._get_text_recurse(element, until)[1]
    
    def _can_align_node_sent(self, node, sent):
        """
        Can this sentence be aligned with this node?
        """
        
        text = self._get_text(node)
        texti = 0
        
        # Go through each token and check it can be aligned with somewhere in
        # the text
        for i in range(len(sent)):
            offset = text.find(sent[i][0][0], texti)
            if offset == -1:
                # This token can't be aligned, so we say we can't align, but do
                # say how many tokens were successfully aligned
                return (False, i, texti)
            else:
                texti = offset + len(sent[i][0])
        
        return (True, i, texti)
    
    def _split_text_for_S(self, node, sents, s_name, align_point):
        """
        Given a text node, splits it up into sentences and insert these
        sentences in to an appropriate point in the parent node
        """
        
        # Don't include leading whitespace in the tag
        s_start = node.data.find(sents[0][0][0])
        if s_start > 0:
            node.parentNode.insertBefore(self._xml_doc.createTextNode(node.data[:s_start]), node)
        
        # Create an S tag containing the matched part
        s_tag = self._xml_doc.createElement(s_name)
        s_tag.appendChild(self._xml_doc.createTextNode(node.data[s_start:align_point]))
        
        # Insert this where this match tag is
        node.parentNode.insertBefore(s_tag, node)
        
        # If there's still some text left, then create a new text node with
        # what was left, and then insert that where this text node was, and
        # recurse on it to tag any more sentences, if there are any
        if align_point < len(node.data):
            new_child = self._xml_doc.createTextNode(node.data[align_point:])
            node.parentNode.replaceChild(new_child, node)
            (can_align, tok_aligned, text_aligned) = self._can_align_node_sent(node, sents[1])
            if can_align and len(sents) > 1:
                return self._split_text_for_S(new_child, sents[1:], s_name, text_aligned)
            else:
                return sents[1:]
        else:
            node.parentNode.removeChild(node)
            return sents[1:]
    
    def _add_S_tags(self, node, sents, s_name):
        """
        Given a node, and some sentences, add tags called s_name such that these
        tags denote sentence boundaries.
        """
        
        # Base case
        if len(sents) > 0:
            sent = list(sents[0])
        else:
            return []
        
        for child in list(node.childNodes):
            # If this node contains the entirety of this sentence, and isn't a
            # text node, then recurse on it to break it down
            (can_align, tok_aligned, text_aligned) = self._can_align_node_sent(child, sent)
            if can_align and child.nodeType != child.TEXT_NODE:
                if len(sent) == len(sents[0]):
                    # Current sent isn't a partial match, continue as per usual
                    sents = self._add_S_tags(child, sents, s_name)
                    if len(sents) > 0:
                        sent = list(sents[0])
                    else:
                        return []
            
            elif can_align and child.nodeType == child.TEXT_NODE:
                # If this text node does contain the full sentence so far, then
                # break up that text node and add the text between <s> tags as
                # appropriate
                if len(sent) == len(sents[0]):
                    sents = self._split_text_for_S(child, sents, s_name, text_aligned)
                    if len(sents) > 0:
                        sent = list(sents[0])
                    else:
                        return []
                else:
                    # If we've matched part of a sentence so far, and this
                    # text node finishes it off, then break up the text node and
                    # add the first bit of it to this node. Then recurse on the
                    # rest of it with the remaining sentences
                    s_tag.appendChild(self._xml_doc.createTextNode(child.data[:text_aligned]))
                    new_child = self._xml_doc.createTextNode(child.data[text_aligned:])
                    node.replaceChild(new_child, child)
                    (can_align, tok_aligned, text_aligned) = self._can_align_node_sent(new_child, sents[1])
                    sents = self._split_text_for_S(new_child, sents[1:], s_name, text_aligned)
                    if len(sents) > 0:
                        sent = list(sents[0])
                    else:
                        return []
                
            else:
                # What we have didn't match the whole sentence, so just add the
                # entire node and then update how little we have left.
                # If this is the first incomplete match we've found (that is,
                # our partial sentence is the same as the full one), then this
                # is a new sentence
                if len(sent) == len(sents[0]):
                    s_tag = self._xml_doc.createElement(s_name)
                    node.insertBefore(s_tag, child)
                s_tag.appendChild(child)
                
                # update our sentence to a partial match
                sent = sent[tok_aligned:]
        
        return sents
    
    def reconcile(self, sents, add_S = False, add_LEX = False, pos_attr=False):
        """
        Reconciles this document against the new internal representation. If
        add_S is set to anything other than False, this means tags are indicated
        to indicate the sentence boundaries, with the tag names being the value
        of add_S. add_LEX is the same, but for marking token boundaries, and
        pos_attr is the name of the attribute which holds the POS tag for that
        token. This is mainly useful for transforming the TERN documents into
        something that GUTime can parse.
        
        If your document already contains S and LEX tags, they will be stripped,
        and the new ones added.
        """
        
        # Strip old TIMEXes, as they are always added
        self.strip_timexes()
        
        # For XML documents, TIMEXes need unique IDs
        all_ts = set()
        for sent in sents:
            for (tok, pos, ts) in sent:
                for t in ts:
                    all_ts.add(t)
        ternip.add_timex_ids(all_ts)
        
        # If LEX tags are being added, strip the old ones, if there are any.
        if self._has_LEX and add_LEX:
            self._strip_tags(self._xml_doc, self._has_LEX, self._xml_body)
        
        # First, add S tags if need be.
        if add_S:
            
            # First, strip any old ones
            if self._has_S:
                self._strip_tags(self._xml_doc, self._has_S, self._xml_body)
            
            self._add_S_tags(self._xml_body, sents, add_S)
            
            # Update what we consider to be our S tags
            self._has_S = add_S
        
        # If add_S is none and also has_S is none, then concatenate all the
        # lists in sents to one massive thing, and treat the root as the S tag.
        
        # If add_LEX = False but has_LEX, change the value of self._pos_attr to
        # the POS tag in the tuple. If pos_attr != self._pos_attr, then remove
        # the old one and add the new one. EDGE CASE!
        
        # Update what we consider to be LEX tags
        if add_LEX:
            self._has_LEX = add_LEX
        if pos_attr:
            self._pos_attr = pos_attr
    
    def _nodes_to_sents(self, node, done_sents, nondone_sents, senti):
        """
        Given a node (which spans multiple sentences), a list of sentences which
        have nodes assigned, and those which don't currently have nodes assigned
        """
        
        # Get next not done sent
        (sent, snodes) = nondone_sents[0]
        
        # Align start of node with where we care about
        text = self._get_text(node)
        text = text[text.find(sent[senti]):]
        
        if len(text) > len(sent) - senti and node.nodeType != node.TEXT_NODE:
            # This node is longer than what's remaining in our sentence, so
            # try and find a small enough piece.
            for child in node.childNodes:
                (done_sents, nondone_sents, senti) = self._nodes_to_sents(child, done_sents, nondone_sents, senti)
        
        elif len(text) > len(sent) - senti and node.nodeType == node.TEXT_NODE:
            # It's a text node! Append the relevant part of this text node to
            # this sent
            snodes.append(self._xml_doc.createTextNode(text[:len(sent) - senti]))
            
            # Mark this sentence as done, yay!
            done_sents.append(nondone_sents[0])
            nondone_sents = nondone_sents[1:]
            
            # Now recurse on the next text node
            (done_sents, nondone_sents, senti) = self._nodes_to_sents(self._xml_doc.createTextNode(text[len(sent) - senti:]), done_sents, nondone_sents, 0)
        
        else:
            # This node is shorter or the same length as what's left in this
            # sentence! So we can just add this node
            snodes.append(node)
            nondone_sents[0] = (sent, snodes)
            senti += len(text)
            
            # Now, if that sentence is complete, then move it from nondone into
            # done
            if senti == len(sent):
                done_sents.append(nondone_sents[0])
                nondone_sents = nondone_sents[1:]
                senti = 0
        
        return (done_sents, nondone_sents, senti)
    
    def _timex_node_token_align(self, text, sent, tokeni):
        """
        Given a tokenised sentence and some text, with some starting token
        offset, figure out which is the token after the last token in this
        block of text
        """
        texti = 0
        for (token, pos, timexes) in sent[tokeni:]:
            text_offset = text[texti:].find(sent[tokeni][0][0])
            if text_offset == -1:
                # can't align with what's left, so next token must be a boundary
                break
            else:
                # Move our text point along to the end of the current token,
                # and continue
                texti += text_offset + len(token)
                tokeni += 1
        
        return tokeni
    
    def get_sents(self):
        """
        Returns a representation of this document in the
        [[(word, pos, timexes), ...], ...] format.
        
        If there are any TIMEXes in the input document that cross sentence
        boundaries (and the input is not already broken up into sentences with
        the S tag), then those TIMEXes are disregarded.
        """
        
        # Is this pre-tokenised into sentences?
        if self._has_S:
            # easy
            sents = [(self._get_text(sent), [sent]) for sent in self._xml_body.getElementsByTagName(self._has_S)]
        else:
            # Get the text, sentence tokenise it and then assign the content
            # nodes of a sentence to that sentence. This is used for identifying
            # LEX tags, if any, and TIMEX tags, if any, later.
            (sents, ndsents, i) = self._nodes_to_sents(self._xml_body, [], [(sent, []) for sent in nltk.tokenize.sent_tokenize(self._get_text(self._xml_body))], 0)
            if len(ndsents) > 0:
                print sents, ndsents, i
                raise tokenise_error('INTERNAL ERROR: there appears to be sentences not assigned to nodes')
        
        # Is this pre-tokenised into tokens?
        if self._has_LEX:
            # Go through each node, and find the LEX tags in there
            tsents = []
            for (sent, nodes) in sents:
                toks = []
                for node in nodes:
                    if node.nodeType == node.ELEMENT_NODE and node.tagName == self._has_LEX:
                        # If this is a LEX tag
                        toks.append((self._get_text(node), node))
                    elif node.nodeType == node.ELEMENT_NODE or node.nodeType == node.DOCUMENT_NODE:
                        # get any lex tags which are children of this node
                        # and add them
                        for lex in node.getElementsByTagName(self._has_LEX):
                            toks.append((self._get_text(lex), lex))
                tsents.append((toks, nodes))
        else:
            # Don't need to keep nodes this time, so this is easier than
            # sentence tokenisation
            tsents = [([(tok, None) for tok in nltk.tokenize.word_tokenize(sent)], nodes) for (sent, nodes) in sents]
        
        # Right, now POS tag. If POS is an attribute on the LEX tag, then just
        # use that
        if self._has_LEX and self._pos_attr:
            psents = [([(tok, tag.getAttribute(self._pos_attr)) for (tok, tag) in sent], nodes) for (sent, nodes) in tsents]
        else:
            # use the NLTK
            psents = [([t for t in nltk.tag.pos_tag([s for (s, a) in sent])], nodes) for (sent, nodes) in tsents]
        
        # Now do timexes - first get all timex tags in a sent
        txsents = []
        for (sent, nodes) in psents:
            txsent = [(t, pos, set()) for (t, pos) in sent]
            for node in nodes:
                if node.nodeType == node.ELEMENT_NODE or node.nodeType == node.DOCUMENT_NODE:
                    if node.tagName == self._timex_tag_name:
                        timex_nodes = [node]
                    else:
                        timex_nodes = node.getElementsByTagName(self._timex_tag_name)
                    
                    # Now, for each timex tag, create a timex object to
                    # represent it
                    for timex_node in timex_nodes:
                        timex = self._timex_from_node(timex_node)
                        
                        # Now figure out the extent of it
                        timex_body = self._get_text(timex_node)
                        timex_before = self._get_text(node, timex_node)
                        
                        # Go through each part of the before text and find the
                        # first token in the body of the timex
                        tokeni = self._timex_node_token_align(timex_before, txsent, 0)
                        
                        # Now we have the start token, find the end token from
                        # the body of the timex
                        tokenj = self._timex_node_token_align(timex_body, txsent, tokeni)
                        
                        # Okay, now add this timex to the relevant tokens
                        for (tok, pos, timexes) in txsent[tokeni:tokenj]:
                            timexes.add(timex)
            
            txsents.append(txsent)
        
        return txsents
    
    def __str__(self):
        """
        String representation of this document
        """
        return self._xml_doc.toxml()

class tokenise_error(Exception):
    
    def __init__(self, s):
        self._s = s
    
    def __str__(self):
        return str(self._s)

class nesting_error(Exception):
    
    def __init__(self, s):
        self._s = s
    
    def __str__(self):
        return str(self._s)

class bad_node_name_error(Exception):
        
    def __str__(self):
        return "The specified tag name does not exist exactly once in the document"