#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function


import signal
import sys
import textwrap
from optparse import OptionParser, OptionValueError


import portage
from portage import os
from emaint.module import Modules
from emaint.progress import ProgressHandler


def usage(module_controller):
		_usage = "usage: emaint [options] COMMAND"

		desc = "The emaint program provides an interface to system health " + \
			"checks and maintenance. See the emaint(1) man page " + \
			"for additional information about the following commands:"

		_usage += "\n\n"
		for line in textwrap.wrap(desc, 65):
			_usage += "%s\n" % line
		_usage += "\nCommands:\n"
		_usage += "  %s" % "all".ljust(15) + \
			"Perform all supported commands\n"
		for mod in module_controller.module_names:
			_usage += "  %s%s\n" % (mod.ljust(15),
				module_controller.get_description(mod))
		return _usage


def emaint_main(myargv):

	# Similar to emerge, emaint needs a default umask so that created
	# files (such as the world file) have sane permissions.
	os.umask(0o22)

	osp = os.path
	module_controller = Modules()
	modules = module_controller.modules
	module_names = module_controller.module_names[:]
	module_names.insert(0, "all")

	def exclusive(option, *args, **kw):
		var = kw.get("var", None)
		if var is None:
			raise ValueError("var not specified to exclusive()")
		if getattr(parser, var, ""):
			raise OptionValueError("%s and %s are exclusive options" % (getattr(parser, var), option))
		setattr(parser, var, str(option))

	parser = OptionParser(usage=usage(module_controller), version=portage.VERSION)
	parser.add_option("-c", "--check", help="check for problems",
		action="callback", callback=exclusive, callback_kwargs={"var":"action"})
	parser.add_option("-f", "--fix", help="attempt to fix problems",
		action="callback", callback=exclusive, callback_kwargs={"var":"action"})
	parser.action = None

	(options, args) = parser.parse_args(args=myargv)
	if len(args) != 1:
		parser.error("Incorrect number of arguments")
	if args[0] not in module_names:
		parser.error("%s target is not a known target" % args[0])

	if parser.action:
		action = parser.action
	else:
		print("Defaulting to --check")
		action = "-c/--check"

	if args[0] == "all":
		tasks = []
		for m in module_names[1:]:
			tasks.append(module_controller.get_class(m))
	else:
		tasks = [module_controller.get_class(args[0] )]

	if action == "-c/--check":
		status = "Checking %s for problems"
		func = "check"
	else:
		status = "Attempting to fix %s"
		func = "fix"

	isatty = os.environ.get('TERM') != 'dumb' and sys.stdout.isatty()
	for task in tasks:
		print(status % task.name())
		inst = task()
		onProgress = None
		if isatty:
			progressBar = portage.output.TermProgressBar()
			progressHandler = ProgressHandler()
			onProgress = progressHandler.onProgress
			def display():
				progressBar.set(progressHandler.curval, progressHandler.maxval)
			progressHandler.display = display
			def sigwinch_handler(signum, frame):
				lines, progressBar.term_columns = \
					portage.output.get_term_size()
			signal.signal(signal.SIGWINCH, sigwinch_handler)
		result = getattr(inst, func)(onProgress=onProgress)
		if isatty:
			# make sure the final progress is displayed
			progressHandler.display()
			print()
			signal.signal(signal.SIGWINCH, signal.SIG_DFL)
		if result:
			print()
			print("\n".join(result))
			print("\n")

	print("Finished")

if __name__ == "__main__":
	emaint_main(sys.argv[1:])
