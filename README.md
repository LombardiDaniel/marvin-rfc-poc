# marvin-rfc-poc

### Install
Run from repo root:
```sh
echo 'export "MARVIN_PATH"="$(pwd)/src" && export PATH=$PATH:$MARVIN_PATH' >> ~/.bashrc
```

#### Usage example:
On project folder:
```sh
marvin init
```

To compile and upload pipeline dependencies (after creation of pipeline.yaml):
```sh
marvin compile_and_upload -f piepeline.yaml
```

next step: get tarball and upload to kfp
