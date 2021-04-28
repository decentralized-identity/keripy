# -*- encoding: utf-8 -*-
"""
keri.db.viring module

VIR  Verifiable Issuance(Revocation) Registry

Provides public simple Verifiable Credential Issuance/Revocation Registry
A special purpose Verifiable Data Registry (VDR)
"""

from keri.db import dbing


class Issuer(dbing.LMDBer):
    """
    Issuer sets up named sub databases for VIR

    Attributes:
        see superclass LMDBer for inherited attributes


        .tvts is named sub DB whose values are serialized TEL events
            dgKey
            DB is keyed by identifer prefix plus digest of serialized event
            Only one value per DB key is allowed
        .tels is named sub DB of key event log tables that map sequence numbers
            to serialized event digests.
            snKey
            Values are digests used to lookup event in .tvts sub DB
            DB is keyed by identifer prefix plus sequence number of tel event
            Only one value per DB key is allowed
        .tibs is named sub DB of indexed backer signatures of event
            Backers always have nontransferable indetifier prefixes.
            The index is the offset of the backer into the backer list
            of the most recent establishment event wrt the receipted event.
            dgKey
            DB is keyed by identifer prefix plus digest of serialized event
            More than one value per DB key is allowed
        .twes is named sub DB of partially backer escrowed event tables
            that map sequence numbers to serialized event digests.
            snKey
            Values are digests used to lookup event in .evts sub DB
            DB is keyed by identifer prefix plus sequence number of tel event
            Only one value per DB key is allowed
        .ancs is a named sub DB of anchors to KEL events.  Quadlet
            Each quadruple is concatenation of  four fully qualified items
            of validator. These are: transferable prefix, plus latest establishment
            event sequence number plus latest establishment event digest,
            plus indexed event signature.
            When latest establishment event is multisig then there will
            be multiple quadruples one per signing key, each a dup at same db key.
            dgKey
            DB is keyed by identifer prefix plus digest of serialized event
            More than one value per DB key is allowed

    Properties:


    """
    def __init__(self, headDirPath=None, reopen=True, **kwa):
        """
        Setup named sub databases.

        Inherited Parameters:
            name is str directory path name differentiator for main database
                When system employs more than one keri database, name allows
                differentiating each instance by name
            temp is boolean, assign to .temp
                True then open in temporary directory, clear on close
                Othewise then open persistent directory, do not clear on close
            headDirPath is optional str head directory pathname for main database
                If not provided use default .HeadDirpath
            mode is int numeric os dir permissions for database directory
            reopen is boolean, IF True then database will be reopened by this init

        Notes:

        dupsort=True for sub DB means allow unique (key,pair) duplicates at a key.
        Duplicate means that is more than one value at a key but not a redundant
        copies a (key,value) pair per key. In other words the pair (key,value)
        must be unique both key and value in combination.
        Attempting to put the same (key,value) pair a second time does
        not add another copy.

        Duplicates are inserted in lexocographic order by value, insertion order.

        """
        super(Issuer, self).__init__(headDirPath=headDirPath, reopen=reopen, **kwa)

    def reopen(self, **kwa):
        """
        Open sub databases
        """
        super(Issuer, self).reopen(**kwa)

        # Create by opening first time named sub DBs within main DB instance
        # Names end with "." as sub DB name must include a non Base64 character
        # to avoid namespace collisions with Base64 identifier prefixes.

        self.tvts = self.env.open_db(key=b'tvts.')
        self.tels = self.env.open_db(key=b'tels.')
        self.tibs = self.env.open_db(key=b'tibs.', dupsort=True)
        self.twes = self.env.open_db(key=b'twes.', dupsort=True)
        self.ancs = self.env.open_db(key=b'ancs.', dupsort=True)

    def putTvt(self, key, val):
        """
        Use dgKey()
        Write serialized VC bytes val to key
        Does not overwrite existing val if any
        Returns True If val successfully written Else False
        Return False if key already exists
        """
        return self.putVal(self.tvts, key, val)

    def setTvt(self, key, val):
        """
        Use dgKey()
        Write serialized VC bytes val to key
        Overwrites existing val if any
        Returns True If val successfully written Else False
        """
        return self.setVal(self.tvts, key, val)

    def getTvt(self, key):
        """
        Use dgKey()
        Return event at key
        Returns None if no entry at key
        """
        return self.getVal(self.tvts, key)

    def delTvt(self, key):
        """
        Use dgKey()
        Deletes value at key.
        Returns True If key exists in database Else False
        """
        return self.delVal(self.tvts, key)

    def putTel(self, key, val):
        """
        Use dgKey()
        Write serialized VC bytes val to key
        Does not overwrite existing val if any
        Returns True If val successfully written Else False
        Return False if key already exists
        """
        return self.putVal(self.tels, key, val)

    def setTel(self, key, val):
        """
        Use dgKey()
        Write serialized VC bytes val to key
        Overwrites existing val if any
        Returns True If val successfully written Else False
        """
        return self.setVal(self.tels, key, val)

    def getTel(self, key):
        """
        Use dgKey()
        Return event at key
        Returns None if no entry at key
        """
        return self.getVal(self.tels, key)

    def delTel(self, key):
        """
        Use dgKey()
        Deletes value at key.
        Returns True If key exists in database Else False
        """
        return self.delVal(self.tels, key)

    def getTibs(self, key):
        """
        Use dgKey()
        Return list of indexed witness signatures at key
        Returns empty list if no entry at key
        Duplicates are retrieved in lexocographic order not insertion order.
        """
        return self.getVals(self.tibs, key)

    def getTibsIter(self, key):
        """
        Use dgKey()
        Return iterator of indexed witness signatures at key
        Raises StopIteration Error when empty
        Duplicates are retrieved in lexocographic order not insertion order.
        """
        return self.getValsIter(self.tibs, key)

    def putTibs(self, key, vals):
        """
        Use dgKey()
        Write each entry from list of bytes indexed witness signatures vals to key
        Adds to existing signatures at key if any
        Returns True If no error
        Apparently always returns True (is this how .put works with dupsort=True)
        Duplicates are inserted in lexocographic order not insertion order.
        """
        return self.putVals(self.tibs, key, vals)

    def addTib(self, key, val):
        """
        Use dgKey()
        Add indexed witness signature val bytes as dup to key in db
        Adds to existing values at key if any
        Returns True if written else False if dup val already exists
        Duplicates are inserted in lexocographic order not insertion order.
        """
        return self.addVal(self.tibs, key, val)

    def cntTibs(self, key):
        """
        Use dgKey()
        Return count of indexed witness signatures at key
        Returns zero if no entry at key
        """
        return self.cntVals(self.tibs, key)

    def delTibs(self, key, val=b''):
        """
        Use dgKey()
        Deletes all values at key if val = b'' else deletes dup val = val.
        Returns True If key exists in database (or key, val if val not b'') Else False
        """
        return self.delVals(self.tibs, key, val)

    def putTwe(self, key, val):
        """
        Use dgKey()
        Write serialized VC bytes val to key
        Does not overwrite existing val if any
        Returns True If val successfully written Else False
        Return False if key already exists
        """
        return self.putVal(self.twes, key, val)

    def setTwe(self, key, val):
        """
        Use dgKey()
        Write serialized VC bytes val to key
        Overwrites existing val if any
        Returns True If val successfully written Else False
        """
        return self.setVal(self.twes, key, val)

    def getTwe(self, key):
        """
        Use dgKey()
        Return event at key
        Returns None if no entry at key
        """
        return self.getVal(self.twes, key)

    def delTwe(self, key):
        """
        Use dgKey()
        Deletes value at key.
        Returns True If key exists in database Else False
        """
        return self.delVal(self.twes, key)

    def putAncs(self, key, vals):
        """
        Use dgKey()
        Write each entry from list of bytes receipt quadruples vals to key
        quadruple is spre+ssnu+sdig+sig
        Adds to existing receipts at key if any
        Returns True If no error
        Apparently always returns True (is this how .put works with dupsort=True)
        Duplicates are inserted in lexocographic order not insertion order.
        """
        return self.putVals(self.ancs, key, vals)


    def addAnc(self, key, val):
        """
        Use dgKey()
        Add receipt quadruple val bytes as dup to key in db
        quadruple is spre+ssnu+sdig+sig
        Adds to existing values at key if any
        Returns True if written else False if dup val already exists
        Duplicates are inserted in lexocographic order not insertion order.
        """
        return self.addVal(self.ancs, key, val)


    def getAncs(self, key):
        """
        Use dgKey()
        Return list of receipt quadruples at key
        quadruple is spre+ssnu+sdig+sig
        Returns empty list if no entry at key
        Duplicates are retrieved in lexocographic order not insertion order.
        """
        return self.getVals(self.ancs, key)


    def getAncsIter(self, key):
        """
        Use dgKey()
        Return iterator of receipt quadruples at key
        quadruple is spre+ssnu+sdig+sig
        Raises StopIteration Error when empty
        Duplicates are retrieved in lexocographic order not insertion order.
        """
        return self.getValsIter(self.ancs, key)


    def cntAncs(self, key):
        """
        Use dgKey()
        Return count of receipt quadruples at key
        Returns zero if no entry at key
        """
        return self.cntVals(self.ancs, key)


    def delAncs(self, key, val=b''):
        """
        Use dgKey()
        Deletes all values at key if val = b'' else deletes dup val = val.
        Returns True If key exists in database (or key, val if val not b'') Else False
        """
        return self.delVals(self.ancs, key, val)



def regKey(pre, rdig):
    """
    Returns bytes Registry key from concatenation of ':' with qualified Base64 issuer
    prefix bytes pre and qualified Base64 bytes digest of serialized vcp event
    If pre or dig are str then converts to bytes
    """
    if hasattr(pre, "encode"):
        pre = pre.encode("utf-8")  # convert str to bytes
    if hasattr(rdig, "encode"):
        rdig = rdig.encode("utf-8")  # convert str to bytes
    return (b'%s:%s' %  (pre, rdig))

def vcKey(pre, rdig, vcdig):
    """
    Returns bytes Registry key from concatenation of ':' with qualified Base64 issuer
    prefix bytes pre and qualified Base64 bytes digest of serialized vcp event
    If pre or dig are str then converts to bytes
    """
    if hasattr(pre, "encode"):
        pre = pre.encode("utf-8")  # convert str to bytes
    if hasattr(rdig, "encode"):
        rdig = rdig.encode("utf-8")  # convert str to bytes
    if hasattr(vcdig, "encode"):
        vcdig = vcdig.encode("utf-8")  # convert str to bytes
    return (b'%s:%s:%s' %  (pre, rdig, vcdig))

