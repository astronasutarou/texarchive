#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (
  absolute_import, division, print_function,unicode_literals)

import re, codecs, os, logging
from tempfile import NamedTemporaryFile
from tarfile import TarFile
from argparse import ArgumentParser as ap

logging.basicConfig(
  level=logging.INFO, format='%(message)s')
LOGGER = logging.getLogger()

FIGURE_PATH = []
MISC_PATH   = []

RE_TEXFILE  = re.compile(ur'\.tex$')
RE_RMINDENT = re.compile(ur'^\s*')
RE_COMMENT  = re.compile(ur'^\s*%')
RE_INPUT    = re.compile(ur'\\input{(.*)}')

RE_BIBSTLE  = re.compile(ur'\\bibliographystyle{.*}')
RE_BIBTEX   = re.compile(ur'\\bibliography{.*}')

RE_EXT      = re.compile(ur'.*\.(.*)')
RE_INCFIG   = re.compile(ur'\\includegraphics(\[.*\])?{(.*)}')
RE_PLTONE   = re.compile(ur'\\plotone{(.*)}')
RE_PLTTWO   = re.compile(ur'\\plottwo{(.*)}{(.*)}')

def recursive_print(filename, fout):
  with codecs.open(filename,'r','utf-8') as fd:
    for line in fd:
      if RE_COMMENT.match(line): continue
      if RE_BIBSTLE.search(line): continue
      line = RE_RMINDENT.sub('',line)
      if len(line) == 0: continue

      inp = RE_INPUT.search(line)
      if inp is not None:
        fn = inp.groups()[0]
        if RE_TEXFILE.search(fn):
          recursive_print(fn, fout)
        else:
          recursive_print(fn+'.tex', fout)
        continue

      bib = RE_BIBTEX.search(line)
      if bib is not None:
        bbl_print(filename, fout)
        continue

      fig = RE_INCFIG.search(line)
      if fig is not None:
        opt,figpath = fig.groups()
        ext = RE_EXT.findall(figpath)[-1]
        figname = 'f{0:03d}.{1}'.format(len(FIGURE_PATH)+1,ext)
        line = line.replace(figpath, figname)
        FIGURE_PATH.append({figpath:figname})
        if ext != 'eps' and ext != 'ps':
          MISC_PATH.append(
            {re.sub(u'{}$'.format(ext),u'xbb',figpath):
             re.sub(u'{}$'.format(ext),u'xbb',figname)})

      fig = RE_PLTONE.search(line)
      if fig is not None:
        figpath = fig.groups()[0]
        ext = RE_EXT.findall(figpath)[-1]
        figname = 'f{0:03d}.{1}'.format(len(FIGURE_PATH)+1,ext)
        line = line.replace(figpath, figname)
        FIGURE_PATH.append({figpath:figname})
        if ext != 'eps' and ext != 'ps':
          MISC_PATH.append(
            {re.sub(u'{}$'.format(ext),u'xbb',figpath):
             re.sub(u'{}$'.format(ext),u'xbb',figname)})

      fig = RE_PLTTWO.search(line)
      if fig is not None:
        figpath1, figpath2 = fig.groups()
        ext1 = RE_EXT.findall(figpath1)[-1]
        ext2 = RE_EXT.findall(figpath2)[-1]
        figname1 = 'f{0:03d}a.{1}'.format(len(FIGURE_PATH)+1,ext1)
        figname2 = 'f{0:03d}b.{1}'.format(len(FIGURE_PATH)+1,ext2)
        line = line.replace(figpath1, figname1)
        line = line.replace(figpath2, figname2)
        FIGURE_PATH.append({figpath1:figname1, figpath2:figname2})
        if ext1 != 'eps' and ext1 != 'ps':
          MISC_PATH.append(
            {re.sub(u'{}$'.format(ext),u'xbb',figpath1):
             re.sub(u'{}$'.format(ext),u'xbb',figname1)})
        if ext2 != 'eps' and ext2 != 'ps':
          MISC_PATH.append(
            {re.sub(u'{}$'.format(ext),u'xbb',figpath2):
             re.sub(u'{}$'.format(ext),u'xbb',figname2)})

      fout.write(line)

def bbl_print(filename, fout):
  filename = filename.replace(ur'.tex',ur'.bbl')
  with codecs.open(filename, 'r', 'utf-8') as bbl:
    for line in bbl:
      fout.write(line)


if __name__ == '__main__':
  parser = ap(
    description='Make a multi-file tex documents into a single tex file.')
  parser.add_argument(
    'master_tex', metavar='master', type=unicode,
    help='master .tex file to be converted.')
  parser.add_argument(
    'archive', metavar='archive', type=unicode,
    help='output archive file (tar.gz).')

  args = parser.parse_args()

  archive_base = re.sub(ur'\.tar\.gz$',u'',args.archive)
  archive_file = archive_base + '.tar.gz'

  master = args.master_tex

  with TarFile.gzopen(archive_file, 'w') as arv:
    LOGGER.info('Create archive "{}":'.format(archive_file))
    with NamedTemporaryFile(prefix='texarv_') as tempfile:
      with tempfile.file as tmp:
        recursive_print(master, tmp)
      arv.add(tempfile.name, arcname='ms.tex')
      LOGGER.info('  append manuscript file "ms.tex"')
      for items in FIGURE_PATH:
        for figpath,arcname in items.iteritems():
          arv.add(figpath, arcname=arcname)
          LOGGER.info(
            '  append figure file "{}" as "{}"'.format(figpath, arcname))
      for items in MISC_PATH:
        for miscpath,arcname in items.iteritems():
          if os.path.exists(miscpath):
            arv.add(miscpath, arcname=arcname)
            LOGGER.info(
              '  append misc file "{}" as "{}"'.format(figpath, arcname))
