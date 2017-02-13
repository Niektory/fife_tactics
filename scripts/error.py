# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import print_function

from traceback import print_exception, format_exception
from datetime import datetime

from config.version import version

ERROR_FILE = "error.log"

#def printException():
#	with open(ERROR_FILE, "a") as f:
#		f.write(str(datetime.now()))
#		f.write("\n\n")
#		print_exc(file=f)
#		f.write("\n-----\n\n")
#	print("FATAL ERROR! Exception logged in", ERROR_FILE)

class LogException:
	past_errors = []

	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if exc_type is None:
			# no exception, nothing to do
			return
		# log/display each error once; ignore further identical errors
		if format_exception(exc_type, exc_value, exc_traceback) not in LogException.past_errors:
			traceback = format_exception(exc_type, exc_value, exc_traceback)
			LogException.past_errors.append(traceback)
			print("\n============================================================\n")
			print_exception(exc_type, exc_value, exc_traceback)
			try:
				with open(ERROR_FILE, "a") as f:
					f.write(version + "\n")
					f.write(str(datetime.now()))
					f.write("\n\n")
					print_exception(exc_type, exc_value, exc_traceback, file=f)
					f.write("\n-----\n\n")
			except IOError:
				error_message = "An unhandled exception occured!\n"\
					"Could not open file '{}' for writing. Exception could not be logged.\n"\
					"Please copy/screenshot the error and send it to the developers."\
					.format(ERROR_FILE)
			else:
				error_message = "An unhandled exception occured!\n"\
					"The exception has been logged in file '{}'. "\
					"Please send that file to the developers."\
					.format(ERROR_FILE)
			print()
			print(error_message)
			print("\n============================================================\n")
			try:
				import Tkinter
				import tkMessageBox
			except ImportError:
				pass
			else:
				window = Tkinter.Tk()
				window.wm_withdraw()
				short_traceback = traceback[:]
				if len(short_traceback) > 6:
					short_traceback[1:-5] = ["(...)\n"]
				tkMessageBox.showerror(
					title="".join(
						format_exception(exc_type, exc_value, exc_traceback, limit=0)[1:]),
					message=error_message + "\n\n" + "".join(short_traceback))
		# don't propagate the exception
		return True

def LogExceptionDecorator(function):
	def innerFunction(*args, **kwargs):
		with LogException():
			return function(*args, **kwargs)
	return innerFunction
