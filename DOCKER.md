# Build

```
TARGETS="kli keri"
for target in ${TARGETS}
do
  docker build \
    --target ${target} \
    -t keripy/${target} .
done
```

# Run

* Run `kli`:
`docker run -it keripy/kli --help`
* Run `keri`: 
`docker run -it keripy/keri --help`
