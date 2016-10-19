# TeXarchive
This provides a Python script to convert a set of TeX documents into a single
TeX source file suitable for submitting to journals and to create a single
archive containing the TeX source and figures.

It reads TeX sources recursively and serialize them into a single TeX source.
The serialized TeX source is stored in a gunzip archive as `ms.tex`.
The bibliography information in a `.bbl` file is also included in `ms.tex`.
Note that the `.bbl` file should have the same basename as the master TeX
source file. Figure files are also stored in the archive. The name of the
figures are automatically converted like `f001.eps`.


## How to Install
Create a symbolic link in `/usr/local/bin`.

~~~sh
sudo ln -s ${PWD}/texarchive.py /usr/local/bin/texarchive
~~~


## Usage
`texarchive` requires two arguments: The first argument is the master TeX
source file; The second argument is the name of the archive file to be created.

~~~sh
texarchive master.tex archive.tar.gz
~~~
