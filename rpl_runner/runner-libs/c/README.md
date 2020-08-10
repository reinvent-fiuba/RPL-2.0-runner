## Info
It is a custom build of the lib Criterion (https://github.com/Snaipe/Criterion).
Fork available here: https://github.com/alelevinas/Criterion

## Compilation
Follow this guide, https://criterion.readthedocs.io/en/latest/setup.html#building-from-source but change URL to our custom fork 
https://github.com/alelevinas/Criterion

You need:
- meson  https://mesonbuild.com/Quick-guide.html
- ninja https://github.com/ninja-build/ninja/
- Others described in the readme https://criterion.readthedocs.io/en/latest/setup.html#building-from-source


### Steps

1. git clone --recursive https://github.com/alelevinas/Criterion
2. meson build
3. ninja -C build

If meson build fails because of `libffi` failing to compile, then disable the `theories` feature by replacing `enabled` to `disabled` in the meson_options.txt

After step 3 you should have all files installed locally. Let's gather them in a tar file.

1. `cd build`
2. `mkdir criterion_rpl_v2`
3. `mkdir criterion_rpl_v2/lib && cp src/libcriterion.* criterion_rpl_v2/lib`
4. `mkdir criterion_rpl_v2/include && cp -r /usr/local/include/criterion criterion_rpl_v2/include`
5. `mkdir -p criterion_rpl_v2/share/pkgconfig`
6. Put file `criterion.pc` in `criterion_rpl_v2/share/pkgconfig`
7. `tar -czvf criterion_rpl_v2.tar.gz *`
8. `mv criterion_rpl_v2.tar.gz ....../rpl_runner/runner-libs/c`
9. If the filename changed, change it in `.../rpl_runner/Dockerfile`

## Installation
`tar -zxvf criterion-v2.3.0-rc2-custom.tar.gz`
`cp -r criterion-v2.3.0-rc2/. /usr`

## Usage
Add the following command line to get the custom output:
`./test
