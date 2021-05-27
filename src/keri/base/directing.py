# -*- encoding: utf-8 -*-
"""
KERI
keri.base.directing module

simple direct mode demo support classes
"""
import os

from hio.base import doing
from hio.core import wiring
from hio.core.tcp import clienting, serving

from .. import kering
from ..db import dbing
from ..core import coring, eventing
from ..vdr.eventing import Tevery
from . import keeping
from . import basing
from . import keeping
from .. import help
from ..core import eventing
from ..db import dbing

logger = help.ogler.getLogger()


def setupController(name="who", sith=None, count=1, temp=False,
                    remotePort=5621, localPort=5620):
    """
    Setup and return doers list to run controller
    """
    # setup habitat
    hab = basing.Habitat(name=name, isith=sith, icount=count, temp=temp)
    logger.info("\nDirect Mode controller %s:\nNamed %s on TCP port %s to port %s.\n\n",
                hab.pre, hab.name, localPort, remotePort)

    # setup doers
    ksDoer = keeping.KeeperDoer(keeper=hab.ks)  # doer do reopens if not opened and closes
    dbDoer = dbing.BaserDoer(baser=hab.db)  # doer do reopens if not opened and closes

    # setup wirelog to create test vectors
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'logs')

    wl = wiring.WireLog(samed=True, filed=True, name=name, prefix='keri',
                        reopen=True, headDirPath=path)
    wireDoer = wiring.WireLogDoer(wl=wl)

    client = clienting.Client(host='127.0.0.1', port=remotePort, wl=wl)
    clientDoer = doing.ClientDoer(client=client)
    director = Director(hab=hab, client=client, tock=0.125)
    reactor = Reactor(hab=hab, client=client)

    server = serving.Server(host="", port=localPort, wl=wl)
    serverDoer = doing.ServerDoer(server=server)
    directant = Directant(hab=hab, server=server)
    # Reactants created on demand by directant

    return [ksDoer, dbDoer, wireDoer, clientDoer, director, reactor, serverDoer, directant]


class Director(doing.Doer):
    """
    Base class for Direct Mode KERI Controller Doer with habitat and TCP Client

    Attributes:
        hab (Habitat: local controller's context
        client (serving.Client): hio TCP client instance.
            Assumes operated by another doer.

    Inherited Properties:
        tyme (float): relative cycle time of associated Tymist, obtained
            via injected .tymth function wrapper closure.
        tymth (function): function wrapper closure returned by Tymist .tymeth()
            method.  When .tymth is called it returns associated Tymist .tyme.
            .tymth provides injected dependency on Tymist tyme base.
        tock (float): desired time in seconds between runs or until next run,
            non negative, zero means run asap

    Properties:

    Inherited Methods:
        .__call__ makes instance callable return generator
        .do is generator function returns generator

    Methods:

    Hidden:
       ._tymth is injected function wrapper closure returned by .tymen() of
            associated Tymist instance that returns Tymist .tyme. when called.
       ._tock is hidden attribute for .tock property
    """

    def __init__(self, hab, client, **kwa):
        """
        Initialize instance.

        Inherited Parameters:
            tymist is  Tymist instance
            tock is float seconds initial value of .tock

        Parameters:
            hab is Habitat instance
            client is TCP Client instance. Assumes opened/closed elsewhere

        """
        super(Director, self).__init__(**kwa)
        self.hab = hab
        self.client = client  # use client to initiate comms
        if self.tymth:
            self.client.wind(self.tymth)

    def wind(self, tymth):
        """
        Inject new tymist.tymth as new ._tymth. Changes tymist.tyme base.
        Updates winds .tymer .tymth
        """
        super(Director, self).wind(tymth)
        self.client.wind(tymth)

    def sendOwnEvent(self, sn):
        """
        Utility to send own event at sequence number sn
        """
        msg = self.hab.makeOwnEvent(sn=sn)
        # send to connected remote
        self.client.tx(msg)
        logger.info("%s: %s sent event:\n%s\n\n", self.hab.name, self.hab.pre, bytes(msg))

    def sendOwnInception(self):
        """
        Utility to send own inception on client
        """
        self.sendOwnEvent(sn=0)


class Reactor(doing.DoDoer):
    """
    Reactor Subclass of DoDoer with doers list from do generator methods:
        .msgDo, .cueDo, and  .escrowDo.
    Enables continuous scheduling of doers (do generator instances or functions)

    Implements Doist like functionality to allow nested scheduling of doers.
    Each DoDoer runs a list of doers like a Doist but using the tyme from its
       injected tymist as injected by its parent DoDoer or Doist.

    Scheduling hierarchy: Doist->DoDoer...->DoDoer->Doers

    Inherited Attributes:
        .done is Boolean completion state:
            True means completed
            Otherwise incomplete. Incompletion maybe due to close or abort.
        .opts is dict of injected options for its generator .do
        .doers is list of Doers or Doer like generator functions

    Attributes:
        .hab is Habitat instance of local controller's context
        .client is TCP Client instance.
        .kevery is Kevery instance


    Inherited Properties:
        .tyme is float relative cycle time of associated Tymist .tyme obtained
            via injected .tymth function wrapper closure.
        .tymth is function wrapper closure returned by Tymist .tymeth() method.
            When .tymth is called it returns associated Tymist .tyme.
            .tymth provides injected dependency on Tymist tyme base.
        .tock is float, desired time in seconds between runs or until next run,
                 non negative, zero means run asap

    Properties:

    Inherited Methods:
        .wind  injects ._tymth dependency from associated Tymist to get its .tyme
        .__call__ makes instance callable
            Appears as generator function that returns generator
        .do is generator method that returns generator
        .enter is enter context action method
        .recur is recur context action method or generator method
        .clean is clean context action method
        .exit is exit context method
        .close is close context method
        .abort is abort context method

    Overidden Methods:

    Hidden:
       ._tymth is injected function wrapper closure returned by .tymen() of
            associated Tymist instance that returns Tymist .tyme. when called.
       ._tock is hidden attribute for .tock property

    """

    def __init__(self, hab, client, verifier=None, indirect=False, doers=None, **kwa):
        """
        Initialize instance.

        Inherited Parameters:
            tymist is  Tymist instance
            tock is float seconds initial value of .tock
            doers is list of doers (do generator instances, functions or methods)

        Parameters:
            hab is Habitat instance of local controller's context
            client is TCP Client instance
            verifier is Verifier instance of local controller's TEL context
            indirect is Boolean, True means don't process cue'ed receipts

        """
        self.hab = hab
        self.client = client  # use client for both rx and tx
        self.verifier = verifier
        self.indirect = True if indirect else False
        self.kevery = eventing.Kevery(kevers=self.hab.kevers,
                                      db=self.hab.db,
                                      opre=self.hab.pre,
                                      indirect=self.indirect,
                                      local=False)

        if self.verifier is not None:
            self.tvy = Tevery(tevers=self.verifier.tevers,
                              reger=self.verifier.reger,
                              db=self.hab.db,
                              regk=None, local=False)
        else:
            self.tvy = None

        self.parser = eventing.Parser(ims=self.client.rxbs,
                                      framed=True,
                                      kvy=self.kevery,
                                      cloned=self.indirect,
                                      tvy=self.tvy)

        doers = doers if doers is not None else []
        doers.extend([self.msgDo, self.escrowDo])
        if not self.indirect:
            doers.extend([self.cueDo])

        super(Reactor, self).__init__(doers=doers, **kwa)
        if self.tymth:
            self.client.wind(self.tymth)

    def wind(self, tymth):
        """
        Inject new tymist.tymth as new ._tymth. Changes tymist.tyme base.
        Updates winds .tymer .tymth
        """
        super(Reactor, self).wind(tymth)
        self.client.wind(tymth)

    @doing.doize()
    def msgDo(self, tymth=None, tock=0.0, **opts):
        """
        Returns Doist compatibile generator method (doer dog) to process
            incoming message stream of .kevery

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters


        Usage:
            add to doers list
        """
        if self.parser.ims:
            logger.info("Client %s received:\n%s\n...\n", self.hab.pre, self.parser.ims[:1024])
        done = yield from self.parser.processor()  # process messages continuously
        return done  # should nover get here except forced close

    @doing.doize()
    def cueDo(self, tymth=None, tock=0.0, **opts):
        """
         Returns Doist compatibile generator method (doer dog) to process
            .kevery.cues deque

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters

        Usage:
            add to doers list
        """
        while True:
            for msg in self.hab.processCuesIter(self.kevery.cues):
                self.sendMessage(msg, label="chit or receipt")
                yield  # throttle just do one cue at a time
            yield
        return False  # should never get here except forced close

    @doing.doize()
    def escrowDo(self, tymth=None, tock=0.0, **opts):
        """
         Returns Doist compatibile generator method (doer dog) to process
            .kevery escrows.

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters

        Usage:
            add to doers list
        """
        while True:
            self.kevery.processEscrows()
            yield
        return False  # should never get here except forced close

    def sendMessage(self, msg, label=""):
        """
        Sends message msg and loggers label if any
        """
        self.client.tx(msg)  # send to remote
        logger.info("%s sent %s:\n%s\n\n", self.hab.pre, label, bytes(msg))


class Directant(doing.DoDoer):
    """
    Directant class with TCP Server.
    Responds to initiated connections from a remote Director by creating and
    running a Reactant per connection. Each Reactant has TCP remoter.

    Directant Subclass of DoDoer with doers list from do generator methods:
        .serviceDo

    Enables continuous scheduling of doers (do generator instances or functions)

    Implements Doist like functionality to allow nested scheduling of doers.
    Each DoDoer runs a list of doers like a Doist but using the tyme from its
       injected tymist as injected by its parent DoDoer or Doist.

    Scheduling hierarchy: Doist->DoDoer...->DoDoer->Doers

    Inherited Attributes:
        .done is Boolean completion state:
            True means completed
            Otherwise incomplete. Incompletion maybe due to close or abort.
        .opts is dict of injected options for its generator .do
        .doers is list of Doers or Doer like generator functions

    Attributes:
        .hab is Habitat instance of local controller's context
        .server is TCP client instance. Assumes operated by another doer.
        .rants is dict of Reactants indexed by connection address

    Inherited Properties:
        .tyme is float relative cycle time of associated Tymist .tyme obtained
            via injected .tymth function wrapper closure.
        .tymth is function wrapper closure returned by Tymist .tymeth() method.
            When .tymth is called it returns associated Tymist .tyme.
            .tymth provides injected dependency on Tymist tyme base.
        .tock is desired time in seconds between runs or until next run,
                 non negative, zero means run asap

    Properties:

    Inherited Methods:
        .wind  injects ._tymth dependency from associated Tymist to get its .tyme
        .__call__ makes instance callable
            Appears as generator function that returns generator
        .do is generator method that returns generator
        .enter is enter context action method
        .recur is recur context action method or generator method
        .clean is clean context action method
        .exit is exit context method
        .close is close context method
        .abort is abort context method

    Methods:

    Hidden:
       ._tymth is injected function wrapper closure returned by .tymen() of
            associated Tymist instance that returns Tymist .tyme. when called.
       ._tock is hidden attribute for .tock property
    """

    def __init__(self, hab, server, verifier=None, doers=None, **kwa):
        """
        Initialize instance.

        Inherited Parameters:
            tymist is  Tymist instance
            tock is float seconds initial value of .tock

        Parameters:
            hab is Habitat instance of local controller's context
            verifier (optional) is Verifier instance of local controller's TEL context
            server is TCP Server instance
        """
        self.hab = hab
        self.verifier = verifier
        self.server = server  # use server for cx
        self.rants = dict()
        doers = doers if doers is not None else []
        doers.extend([self.serviceDo])
        super(Directant, self).__init__(doers=doers, **kwa)
        if self.tymth:
            self.server.wind(self.tymth)

    def wind(self, tymth):
        """
        Inject new tymist.tymth as new ._tymth. Changes tymist.tyme base.
        Updates winds .tymer .tymth
        """
        super(Directant, self).wind(tymth)
        self.server.wind(tymth)

    @doing.doize()
    def serviceDo(self, tymth=None, tock=0.0, **opts):
        """
        Returns Doist compatibile generator method (doer dog) to service
            connections on .server. Creates remoter and rant (Reactant) for each
            open connection and adds rant to running doers.

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters


        Usage:
            add to doers list
        """
        while True:
            for ca, ix in list(self.server.ixes.items()):
                if ix.cutoff:
                    self.closeConnection(ca)
                    continue

                if ca not in self.rants:  # create Reactant and extend doers with it
                    rant = Reactant(tymth=self.tymth, hab=self.hab, verifier=self.verifier, remoter=ix)
                    self.rants[ca] = rant
                    # add Reactant (rant) doer to running doers
                    self.extend(doers=[rant])  # open and run rant as doer

                if ix.timeout > 0.0 and ix.tymer.expired:
                    self.closeConnection(ca)  # also removes rant

            yield
        return False  # should never get here

    def closeConnection(self, ca):
        """
        Close and remove connection given by ca and remove associated rant at ca.
        """
        if ca in self.server.ixes:  # remoter still there
            self.server.ixes[ca].serviceSends()  # send final bytes to socket
        self.server.removeIx(ca)
        if ca in self.rants:  # remove rant (Reactant) if any
            self.remove([self.rants[ca]])  # close and remove rant from doers list
            del self.rants[ca]


class Reactant(doing.DoDoer):
    """
    Reactant Subclass of DoDoer with doers list from do generator methods:
        .msgDo, .cueDo, and .escrowDo.
    Enables continuous scheduling of doers (do generator instances or functions)

    Implements Doist like functionality to allow nested scheduling of doers.
    Each DoDoer runs a list of doers like a Doist but using the tyme from its
       injected tymist as injected by its parent DoDoer or Doist.

    Scheduling hierarchy: Doist->DoDoer...->DoDoer->Doers

    Attributes:
        .hab is Habitat instance of local controller's context
        .kevery is Kevery instance
        .remoter is TCP Remoter instance for connection from remote TCP client.

    Inherited Attributes:
        .done is Boolean completion state:
            True means completed
            Otherwise incomplete. Incompletion maybe due to close or abort.
        .opts is dict of injected options for its generator .do
        .doers is list of Doers or Doer like generator functions


    Inherited Properties:
        .tyme is float relative cycle time of associated Tymist .tyme obtained
            via injected .tymth function wrapper closure.
        .tymth is function wrapper closure returned by Tymist .tymeth() method.
            When .tymth is called it returns associated Tymist .tyme.
            .tymth provides injected dependency on Tymist tyme base.
        .tock is float, desired time in seconds between runs or until next run,
                 non negative, zero means run asap

    Properties:

    Inherited Methods:
        .wind  injects ._tymth dependency from associated Tymist to get its .tyme
        .__call__ makes instance callable
            Appears as generator function that returns generator
        .do is generator method that returns generator
        .enter is enter context action method
        .recur is recur context action method or generator method
        .clean is clean context action method
        .exit is exit context method
        .close is close context method
        .abort is abort context method

    Overidden Methods:

    Hidden:
       ._tymth is injected function wrapper closure returned by .tymen() of
            associated Tymist instance that returns Tymist .tyme. when called.
       ._tock is hidden attribute for .tock property

    """

    def __init__(self, hab, remoter, verifier=None, doers=None, **kwa):
        """
        Initialize instance.

        Inherited Parameters:
            tymist is  Tymist instance
            tock is float seconds initial value of .tock
            doers is list of doers (do generator instancs or functions)

        Parameters:
            hab is Habitat instance of local controller's context
            verifier is Verifier instance of local controller's TEL context
            remoter is TCP Remoter instance
            doers is list of doers (do generator instances, functions or methods)

        """
        self.hab = hab
        self.verifier = verifier
        self.remoter = remoter  # use remoter for both rx and tx

        doers = doers if doers is not None else []
        doers.extend([self.msgDo, self.cueDo, self.escrowDo])

        #  neeeds unique kevery with ims per remoter connnection
        self.kevery = eventing.Kevery(kevers=self.hab.kevers,
                                      db=self.hab.db,
                                      opre=self.hab.pre,
                                      local=False)

        if self.verifier is not None:
            self.tevery = Tevery(tevers=self.verifier.tevers,
                                 reger=self.verifier.reger,
                                 db=self.hab.db,
                                 regk=None, local=False)
            doers.extend([self.verifierDo])
        else:
            self.tevery = None

        self.parser = eventing.Parser(ims=self.remoter.rxbs,
                                      framed=True,
                                      kvy=self.kevery,
                                      tvy=self.tevery)

        super(Reactant, self).__init__(doers=doers, **kwa)
        if self.tymth:
            self.remoter.wind(self.tymth)

    def wind(self, tymth):
        """
        Inject new tymist.tymth as new ._tymth. Changes tymist.tyme base.
        Updates winds .tymer .tymth
        """
        super(Reactant, self).wind(tymth)
        self.remoter.wind(tymth)

    @doing.doize()
    def msgDo(self, tymth=None, tock=0.0, **opts):
        """
        Returns Doist compatibile generator method (doer dog) to process
            incoming message stream of .kevery

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters


        Usage:
            add to doers list
        """
        if self.parser.ims:
            logger.info("Server %s: %s received:\n%s\n...\n", self.hab.name,
                        self.hab.pre, self.parser.ims[:1024])
        done = yield from self.parser.processor()  # process messages continuously
        return done  # should nover get here except forced close

    @doing.doize()
    def cueDo(self, tymth=None, tock=0.0, **opts):
        """
         Returns Doist compatibile generator method (doer dog) to process
            .kevery.cues deque

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters

        Usage:
            add to doers list
        """
        while True:
            for msg in self.hab.processCuesIter(self.kevery.cues):
                self.sendMessage(msg, label="chit or receipt or replay")
                yield  # throttle just do one cue at a time
            yield
        return False  # should never get here except forced close

    @doing.doize()
    def verifierDo(self, tymth=None, tock=0.0, **opts):
        """
         Returns Doist compatibile generator method (doer dog) to process
            .tevery.cues deque

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters

        Usage:
            add to doers list
        """
        while True:
            for msg in self.verifier.processCuesIter(self.tevery.cues):
                self.sendMessage(msg, label="replay")
                yield  # throttle just do one cue at a time
            yield
        return False  # should never get here except forced close

    @doing.doize()
    def escrowDo(self, tymth=None, tock=0.0, **opts):
        """
         Returns Doist compatibile generator method (doer dog) to process
            .kevery escrows.

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value
            opts is dict of injected optional additional parameters

        Usage:
            add to doers list
        """
        while True:
            self.kevery.processEscrows()
            yield
        return False  # should never get here except forced close

    def sendMessage(self, msg, label=""):
        """
        Sends message msg and loggers label if any
        """
        self.remoter.tx(msg)  # send to remote
        logger.info("Server %s: %s sent %s:\n%s\n\n", self.hab.name,
                    self.hab.pre, label, bytes(msg))


def runController(doers, expire=0.0):
    """
    Utiitity Function to create doist to run doers
    """
    tock = 0.03125
    doist = doing.Doist(limit=expire, tock=tock, real=True)
    doist.do(doers=doers)
