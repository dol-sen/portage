# Copyright 2012 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

import re
import textwrap

import portage
from portage import os
from portage.tests import TestCase
from portage.tests.resolver.ResolverPlayground import ResolverPlayground
from portage.util import ensure_dirs
from portage._global_updates import _do_global_updates

class UpdateDbentryTestCase(TestCase):

	def testUpdateDbentryTestCase(self):

		ebuilds = {

			"dev-libs/A-2::dont_apply_updates" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4",
				"SLOT": "2",
			},

			"dev-libs/B-2::dont_apply_updates" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4",
				"SLOT": "2",
			},

		}

		installed = {

			"dev-libs/A-1::test_repo" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4",
			},

			"dev-libs/A-2::dont_apply_updates" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4",
				"SLOT": "2",
			},

			"dev-libs/B-1::test_repo" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4-python",
			},

			"dev-libs/M-1::test_repo" : {
				"EAPI": "4",
			},

			"dev-libs/N-1::test_repo" : {
				"EAPI": "4",
			},

			"dev-libs/N-2::test_repo" : {
				"EAPI": "4-python",
			},

		}

		binpkgs = {

			"dev-libs/A-1::test_repo" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4",
			},

			"dev-libs/A-2::dont_apply_updates" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4",
				"SLOT": "2",
			},

			"dev-libs/B-1::test_repo" : {
				"RDEPEND" : "dev-libs/M dev-libs/N dev-libs/P",
				"EAPI": "4-python",
			},

		}

		world = ["dev-libs/M", "dev-libs/N"]

		updates = textwrap.dedent("""
			move dev-libs/M dev-libs/M-moved
			move dev-libs/N dev-libs/N.moved
		""")

		playground = ResolverPlayground(binpkgs=binpkgs,
			ebuilds=ebuilds, installed=installed, world=world)

		settings = playground.settings
		trees = playground.trees
		eroot = settings["EROOT"]
		portdir = settings["PORTDIR"]
		portdb = trees[eroot]["porttree"].dbapi
		vardb = trees[eroot]["vartree"].dbapi
		bindb = trees[eroot]["bintree"].dbapi
		setconfig = trees[eroot]["root_config"].setconfig
		selected_set = setconfig.getSets()["selected"]

		updates_dir = os.path.join(portdir, "profiles", "updates")

		try:
			ensure_dirs(updates_dir)
			with open(os.path.join(updates_dir, "1Q-2010"), 'w') as f:
				f.write(updates)

			# Create an empty updates directory, so that this
			# repo doesn't inherit updates from the main repo.
			ensure_dirs(os.path.join(
				portdb.getRepositoryPath("dont_apply_updates"),
				"profiles", "updates"))

			global_noiselimit = portage.util.noiselimit
			portage.util.noiselimit = -2
			try:
				_do_global_updates(trees, {})
			finally:
				portage.util.noiselimit = global_noiselimit

			# Workaround for cache validation not working
			# correctly when filesystem has timestamp precision
			# of 1 second.
			vardb._clear_cache()

			# M -> M-moved
			old_pattern = re.compile(r"\bdev-libs/M(\s|$)")
			rdepend = vardb.aux_get("dev-libs/A-1", ["RDEPEND"])[0]
			self.assertTrue(old_pattern.search(rdepend) is None)
			self.assertTrue("dev-libs/M-moved" in rdepend)
			rdepend = bindb.aux_get("dev-libs/A-1", ["RDEPEND"])[0]
			self.assertTrue(old_pattern.search(rdepend) is None)
			self.assertTrue("dev-libs/M-moved" in rdepend)
			rdepend = vardb.aux_get("dev-libs/B-1", ["RDEPEND"])[0]
			self.assertTrue(old_pattern.search(rdepend) is None)
			self.assertTrue("dev-libs/M-moved" in rdepend)
			rdepend = vardb.aux_get("dev-libs/B-1", ["RDEPEND"])[0]
			self.assertTrue(old_pattern.search(rdepend) is None)
			self.assertTrue("dev-libs/M-moved" in rdepend)

			# EAPI 4-python N -> N.moved
			rdepend = vardb.aux_get("dev-libs/B-1", ["RDEPEND"])[0]
			old_pattern = re.compile(r"\bdev-libs/N(\s|$)")
			self.assertTrue(old_pattern.search(rdepend) is None)
			self.assertTrue("dev-libs/N.moved" in rdepend)
			rdepend = bindb.aux_get("dev-libs/B-1", ["RDEPEND"])[0]
			self.assertTrue(old_pattern.search(rdepend) is None)
			self.assertTrue("dev-libs/N.moved" in rdepend)
			self.assertRaises(KeyError,
				vardb.aux_get, "dev-libs/N-2", ["EAPI"])
			vardb.aux_get("dev-libs/N.moved-2", ["RDEPEND"])[0]

			# EAPI 4 does not allow dots in package names for N -> N.moved
			rdepend = vardb.aux_get("dev-libs/A-1", ["RDEPEND"])[0]
			self.assertTrue("dev-libs/N" in rdepend)
			self.assertTrue("dev-libs/N.moved" not in rdepend)
			rdepend = bindb.aux_get("dev-libs/A-1", ["RDEPEND"])[0]
			self.assertTrue("dev-libs/N" in rdepend)
			self.assertTrue("dev-libs/N.moved" not in rdepend)
			vardb.aux_get("dev-libs/N-1", ["RDEPEND"])[0]
			self.assertRaises(KeyError,
				vardb.aux_get, "dev-libs/N.moved-1", ["EAPI"])

			# dont_apply_updates
			rdepend = vardb.aux_get("dev-libs/A-2", ["RDEPEND"])[0]
			self.assertTrue("dev-libs/M" in rdepend)
			self.assertTrue("dev-libs/M-moved" not in rdepend)
			rdepend = bindb.aux_get("dev-libs/A-2", ["RDEPEND"])[0]
			self.assertTrue("dev-libs/M" in rdepend)
			self.assertTrue("dev-libs/M-moved" not in rdepend)

			selected_set.load()
			self.assertTrue("dev-libs/M" not in selected_set)
			self.assertTrue("dev-libs/M-moved" in selected_set)
			self.assertTrue("dev-libs/N" not in selected_set)
			self.assertTrue("dev-libs/N.moved" in selected_set)

		finally:
			playground.cleanup()
