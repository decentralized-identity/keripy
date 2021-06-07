# -*- encoding: utf-8 -*-
"""
keri.kli.commands module

"""
import argparse

from ...app import keeping
from ...app.habbing import Habitat
from ...db import basing

parser = argparse.ArgumentParser(description='view info')
parser.set_defaults(handler=lambda args: info(args.name))
parser.add_argument('--name', '-n', help='Humane reference')


def info(name):
    with basing.openDB(name=name, temp=False) as db, keeping.openKS(name=name, temp=False) as ks:
        hab = Habitat(name=name, ks=ks, db=db, temp=False)

        print(f'Prefix {hab.pre}')
        print(f'Public Key {hab.kever.verfers[0].qb64}')
        print(f'Current rotation index {hab.ridx}')
