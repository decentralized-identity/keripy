### Interop

Demos are built on new pushes to `master`, they can be used to test integration with other core KERI libraries
    * [keripy](https://github.com/decentralized-identity/keripy)
    * [kerigo](https://github.com/decentralized-identity/kerigo)

#### Running demos

##### Bob
```shell
docker run --rm -i -p 5620-5621 --name keripy-bob ghcr.io/decentralized-identity/keripy/keripy-interop  bash -c 'python -m keri.demo.demo_bob'
```

##### Eve
```shell
docker run --rm -i -p 5620-5621 --name keripy-eve ghcr.io/decentralized-identity/keripy/keripy-interop  bash -c 'python -m keri.demo.demo_eve'
```

##### Sam
```shell
docker run --rm -i -p 5620-5621 --name keripy-sam ghcr.io/decentralized-identity/keripy/keripy-interop  bash -c 'python -m keri.demo.demo_sam'
```