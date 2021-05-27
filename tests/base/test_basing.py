# -*- encoding: utf-8 -*-
"""
tests.base.basing module

"""

import json
import os
from dataclasses import dataclass, asdict

import pytest

from keri.base import basing, keeping
from keri.base.basing import Habitat
from keri.core.coring import Serials, Serder
from keri.db import dbing
from keri.db.dbing import fnKey, dgKey
from keri.help import helping


def test_habitat():
    """
    Test Habitat class
    """
    hab = Habitat(temp=True)
    assert hab.name == "test"

    hab.db.close(clear=True)
    hab.ks.close(clear=True)

    """End Test"""


def test_habitat_reinitialization():
    """
    Test Reinitializing Habitat class
    """
    name = "bob-test"
    with dbing.openDB(name=name, temp=False) as db, keeping.openKS(name=name, temp=False) as ks:
        hab = basing.Habitat(name=name, ks=ks, db=db, icount=1, temp=False)

        opre = hab.pre
        opub = hab.kever.verfers[0].qb64
        odig = hab.kever.serder.dig
        assert hab.ridx == 0

    with dbing.openDB(name=name, temp=False) as db, keeping.openKS(name=name, temp=False) as ks:
        hab = basing.Habitat(name=name, ks=ks, db=db, icount=1, temp=False)
        hab.rotate()

        assert hab.ridx == 1
        assert opub != hab.kever.verfers[0].qb64
        assert odig != hab.kever.serder.dig

        npub = hab.kever.verfers[0].qb64
        ndig = hab.kever.serder.dig

        assert opre == hab.pre
        assert hab.kever.verfers[0].qb64 == npub
        assert hab.ridx == 1

        assert hab.kever.serder.dig != odig
        assert hab.kever.serder.dig == ndig

        hab.db.close(clear=True)
        hab.ks.close(clear=True)
    """End Test"""


def test_habitat_idempotent_reinitialization():
    """
    Test Reinitializing Habitat class
    """
    name = "bob-test"
    with dbing.openDB(name=name, temp=False) as db, keeping.openKS(name=name, temp=False) as ks:
        basing.Habitat(name=name, ks=ks, db=db, icount=1, temp=False)

    with dbing.openDB(name=name, temp=False) as db, keeping.openKS(name=name, temp=False) as ks:
        hab = basing.Habitat(name=name, ks=ks, db=db, icount=1, temp=False)
        hab.rotate()

        key = fnKey(pre=hab.pre, sn=0)
        dig = hab.db.getFe(key=key)
        raw = hab.db.getEvt(key=dgKey(pre=hab.pre, dig=dig))
        serder = Serder(raw=bytes(raw))

        assert serder.ked["t"] == "icp"

        key1 = fnKey(pre=hab.pre, sn=1)
        dig1 = hab.db.getFe(key=key1)
        raw1 = hab.db.getEvt(key=dgKey(pre=hab.pre, dig=dig1))
        serder1 = Serder(raw=bytes(raw1))

        assert serder1.ked["t"] == "rot"

        hab.db.close(clear=True)
        hab.ks.close(clear=True)
    """End Test"""


def test_kom_happy_path():
    """
    Test Komer object class
    """

    @dataclass
    class Record:
        first: str  # first name
        last: str  # last name
        street: str  # street address
        city: str  # city name
        state: str  # state code
        zip: int  # zip code

        def __iter__(self):
            return iter(asdict(self))

    jim = Record(first="Jim",
                 last="Black",
                 street="100 Main Street",
                 city="Riverton",
                 state="UT",
                 zip=84058)

    jimser = json.dumps(asdict(jim)).encode("utf-8")
    jim = helping.datify(Record, json.loads(bytes(jimser).decode("utf-8")))
    assert isinstance(jim, Record)

    with dbing.openLMDB() as db:
        assert isinstance(db, dbing.LMDBer)
        assert db.name == "test"
        assert db.opened

        mydb = basing.Komer(db=db, schema=Record, subdb='records.')
        assert isinstance(mydb, basing.Komer)

        sue = Record(first="Susan",
                     last="Black",
                     street="100 Main Street",
                     city="Riverton",
                     state="UT",
                     zip=84058)

        keys = ("test_key", "0001")
        mydb.put(keys=keys, data=sue)
        actual = mydb.get(keys=keys)

        assert actual.first == "Susan"
        assert actual.last == "Black"
        assert actual.street == "100 Main Street"
        assert actual.city == "Riverton"
        assert actual.state == "UT"
        assert actual.zip == 84058

        mydb.rem(keys)

        actual = mydb.get(keys=keys)
        assert actual is None

    assert not os.path.exists(db.path)
    assert not db.opened


def test_put_invalid_dataclass():
    @dataclass
    class Record:
        first: str

        def __iter__(self):
            return iter(asdict(self))

    @dataclass
    class AnotherClass:
        age: int

    with dbing.openLMDB() as db:
        mydb = basing.Komer(db=db, schema=AnotherClass, subdb='records.')
        sue = Record(first="Susan")
        keys = ("test_key", "0001")

        with pytest.raises(ValueError):
            mydb.put(keys=keys, data=sue)


def test_get_invalid_dataclass():
    @dataclass
    class Record:
        first: str

        def __iter__(self):
            return iter(asdict(self))

    @dataclass
    class AnotherClass:
        age: int

    with dbing.openLMDB() as db:
        mydb = basing.Komer(db=db, schema=Record, subdb='records.')
        sue = Record(first="Susan")
        keys = ("test_key", "0001")
        mydb.put(keys=keys, data=sue)

        mydb = basing.Komer(db=db, schema=AnotherClass, subdb='records.')
        with pytest.raises(ValueError):
            mydb.get(keys)


def test_not_found_entity():
    @dataclass
    class Record:
        first: str

        def __iter__(self):
            return iter(asdict(self))

    with dbing.openLMDB() as db:
        mydb = basing.Komer(db=db, schema=Record, subdb='records.')
        sue = Record(first="Susan")
        keys = ("test_key", "0001")

        mydb.put(keys=keys, data=sue)
        actual = mydb.get(("not_found", "0001"))
        assert actual is None


def test_serialization():
    @dataclass
    class Record:
        first: str  # first name
        last: str  # last name
        street: str  # street address
        city: str  # city name
        state: str  # state code
        zip: int  # zip code

    jim = Record(first="Jim",
                 last="Black",
                 street="100 Main Street",
                 city="Riverton",
                 state="UT",
                 zip=84058)

    with dbing.openLMDB() as db:
        k = basing.Komer(db=db, schema=Record, subdb='records.')
        srl = k._serializer(Serials.mgpk)

        expected = b'\x86\xa5first\xa3Jim\xa4last\xa5Black\xa6street\xaf100 Main Street\xa4city\xa8Riverton\xa5state\xa2UT\xa3zip\xce\x00\x01HZ'
        assert srl(jim) == expected

        srl = k._serializer(Serials.cbor)
        expected = b'\xa6efirstcJimdlasteBlackfstreeto100 Main StreetdcityhRivertonestatebUTczip\x1a\x00\x01HZ'
        assert srl(jim) == expected

        srl = k._serializer(Serials.json)
        expected = b'{"first":"Jim","last":"Black","street":"100 Main Street","city":"Riverton","state":"UT","zip":84058}'
        assert srl(jim) == expected


def test_deserialization():
    @dataclass
    class Record:
        first: str  # first name
        last: str  # last name
        street: str  # street address
        city: str  # city name
        state: str  # state code
        zip: int  # zip code

    msgp = b'\x86\xa5first\xa3Jim\xa4last\xa5Black\xa6street\xaf100 Main Street\xa4city\xa8Riverton\xa5state\xa2UT\xa3zip\xce\x00\x01HZ'
    cbor = b'\xa6efirstcJimdlasteBlackfstreeto100 Main StreetdcityhRivertonestatebUTczip\x1a\x00\x01HZ'
    json = b'{"first": "Jim", "last": "Black", "street": "100 Main Street", "city": "Riverton", "state": "UT", "zip": 84058}'

    with dbing.openLMDB() as db:
        k = basing.Komer(db=db, schema=Record, subdb='records.')

        desrl = k._deserializer(Serials.mgpk)
        actual = helping.datify(Record, desrl(msgp))
        assert actual.first == "Jim"
        assert actual.last == "Black"
        assert actual.street == "100 Main Street"
        assert actual.city == "Riverton"
        assert actual.state == "UT"
        assert actual.zip == 84058

        desrl = k._deserializer(Serials.json)
        actual = helping.datify(Record, desrl(json))
        assert actual.first == "Jim"
        assert actual.last == "Black"
        assert actual.street == "100 Main Street"
        assert actual.city == "Riverton"
        assert actual.state == "UT"
        assert actual.zip == 84058

        desrl = k._deserializer(Serials.cbor)
        actual = helping.datify(Record, desrl(cbor))
        assert actual.first == "Jim"
        assert actual.last == "Black"
        assert actual.street == "100 Main Street"
        assert actual.city == "Riverton"
        assert actual.state == "UT"
        assert actual.zip == 84058


if __name__ == "__main__":
    test_kom_happy_path()
