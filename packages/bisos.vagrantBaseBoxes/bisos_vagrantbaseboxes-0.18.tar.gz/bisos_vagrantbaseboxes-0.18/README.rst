======================================================================================
bisos.vagrantBaseBoxes: Facilities for Creating and Managing Vagrant Packer Base Boxes
======================================================================================

.. contents::
   :depth: 3
..

+--------------------------+------------------------------------------+
| ``Blee Panel Controls``: | `Show-All <elisp:(show-all)>`__ :        |
|                          | `Overview <elisp:(org-shifttab)>`__ :    |
|                          | `Content <elisp:                         |
|                          | (progn (org-shifttab) (org-content))>`__ |
|                          | : `(1) <elisp:(delete-other-windows)>`__ |
|                          | :                                        |
|                          | `S&Q <elisp                              |
|                          | :(progn (save-buffer) (kill-buffer))>`__ |
|                          | : `Save <elisp:(save-buffer)>`__ :       |
|                          | `Quit <elisp:(kill-buffer)>`__ :         |
|                          | `Bury <elisp:(bury-buffer)>`__           |
+--------------------------+------------------------------------------+
| ``Panel Links``:         | `Repo Blee                               |
|                          | Panel <./panels/bisos.fac                |
|                          | ter/_nodeBase_/fullUsagePanel-en.org>`__ |
|                          | – `Blee                                  |
|                          | Panel </bisos/git/auth/b                 |
|                          | xRepos/bisos-pip/facter/panels/bisos.fac |
|                          | ter/_nodeBase_/fullUsagePanel-en.org>`__ |
+--------------------------+------------------------------------------+
| ``See Also``:            | `At                                      |
|                          | PYPI <h                                  |
|                          | ttps://pypi.org/project/bisos.facter>`__ |
|                          | :                                        |
|                          | `bisos.PyC                               |
|                          | S <https://github.com/bisos-pip/pycs>`__ |
+--------------------------+------------------------------------------+

Overview
========

*bisos.vagrantBaseBoxes* provides various facilities for creation and
management of Vagrant Packer Base Boxes.

*bisos.vagrantBaseBoxes* is a python package that uses the
`PyCS-Framework <https://github.com/bisos-pip/pycs>`__ for its
implementation. It is a BISOS-Capability and a Standalone-BISOS-Package.

Much of *bisos.vagrantBaseBoxes* is based on
https://github.com/rgl/debian-vagrant but our general data driven
approach is different.

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `About vagrantBaseBoxes Data (packer base box
   specifications) <#about-vagrantbaseboxes-data-packer-base-box-specifications>`__
-  `Part of BISOS — ByStar Internet Services Operating
   System <#part-of-bisos-----bystar-internet-services-operating-system>`__
-  `bisos.vagrantBaseBoxes as a Standalone Piece of
   BISOS <#bisosvagrantbaseboxes-as-a-standalone-piece-of-bisos>`__
-  `Installation <#installation>`__

   -  `Installation With pip <#installation-with-pip>`__
   -  `Installation With pipx <#installation-with-pipx>`__

-  `Usage <#usage>`__

   -  `First Install the packer box
      specifications. <#first-install-the-packer-box-specifications>`__
   -  `vagrantBoxProc.cs Menu <#vagrantboxproccs-menu>`__

-  `Support <#support>`__
-  `Planned Improvements <#planned-improvements>`__

About vagrantBaseBoxes Data (packer base box specifications)
============================================================

*bisos.vagrantBaseBoxes* is data driven. By itself it is useless. It
operates on well structured directories which contain packer base box
specifications.

In BISOS, the packer base box specifications are in the form of a BISOS
Repo Object (BRO). The github url for the BRO is:

https://github.com/bxObjects/bro_vagrantDebianBaseBoxes

In BISOS, the defaults are:

.. code:: bash

   cd /bisos/git/bxRepos/bxObjects
   git clone https://github.com/bxObjects/bro_vagrantDebianBaseBoxes.git

You can clone that repo anywhere and then just adjust the command line
path to it.

Part of BISOS — ByStar Internet Services Operating System
=========================================================

| Layered on top of Debian, **BISOS**: (By\* Internet Services Operating
  System) is a unified and universal framework for developing both
  internet services and software-service continuums that use internet
  services. See `Bootstrapping ByStar, BISOS and
  Blee <https://github.com/bxGenesis/start>`__ for information about
  getting started with BISOS.
| **BISOS** is a foundation for **The Libre-Halaal ByStar Digital
  Ecosystem** which is described as a cure for losses of autonomy and
  privacy in a book titled: `Nature of
  Polyexistentials <https://github.com/bxplpc/120033>`__

bisos.vagrantBaseBoxes as a Standalone Piece of BISOS
=====================================================

bisos.vagrantBaseBoxes is a standalone piece of BISOS. It can be used as
a self-contained Python package separate from BISOS. Follow the
installation and usage instructions below for your own use.

Installation
============

The sources for the bisos.vagrantBaseBoxes pip package are maintained
at: https://github.com/bisos-pip/vagrantBaseBoxes.

The bisos.vagrantBaseBoxes pip package is available at PYPI as
https://pypi.org/project/bisos.vagrantBaseBoxes

You can install bisos.vagrantBaseBoxes with pip or pipx.

Installation With pip
---------------------

If you need access to bisos.vagrantBaseBoxes as a python module, you can
install it with pip:

.. code:: bash

   pip install bisos.vagrantBaseBoxes

Installation With pipx
----------------------

If you only need access to bisos.vagrantBaseBoxes on command-line, you
can install it with pipx:

.. code:: bash

   pipx install bisos.vagrantBaseBoxes

The following commands are made available:

-  vagrantBaseBoxes-sbom.cs (Software Bill of Material)
-  vagrantBoxProc.cs

Usage
=====

First Install the packer box specifications.
--------------------------------------------

Clone the packer box specifications somewhere. Perhaps in your home
directory.

.. code:: bash

   git clone https://github.com/bxObjects/bro_vagrantDebianBaseBoxes.git

vagrantBoxProc.cs Menu
----------------------

Run:

.. code:: bash

   vagrantBoxProc.cs

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact

Planned Improvements
====================

-  Fully absorb all of lcaVagrantXX.sh
