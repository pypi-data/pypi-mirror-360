#!/usr/bin/env python

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/auth/bxRepos/bisos-pip/vagrantBaseBoxes/py3/bin/exmpl-vagBox.cs
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/vagrantBaseBoxes/py3/bin/exmpl-vagBox.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/lcnt/lcntScreencasting/subTitles/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers
#+end_org """

from bisos import b
from bisos.b import cs

from bisos.vagrantBaseBoxes import vagBoxSeed
vb = vagBoxSeed.vagBox

vagBoxList = [
]

vagBoxSeed.setup(
    seedType="common",
    vagBoxList=vagBoxList,
    # examplesHook=qmail_binsPrep.examples_csu,
)
