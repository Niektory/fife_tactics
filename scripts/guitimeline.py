#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

import PyCEGUI

class GUITimeline:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("Timeline.layout","Timeline/")
		self.list = self.window.getChild("Timeline/TextBox")

	def update(self):
		self.list.resetList()
		self.items = []
		if self.application.world.current_character_turn:
			self.items.append(PyCEGUI.ListboxTextItem(self.application.world.current_character_turn.name + "'s turn (current)"))
			self.items[-1].setAutoDeleted(False)
			self.items[-1].setTextColours(PyCEGUI.colour(0xFFFFD000))
			self.list.addItem(self.items[-1])

		last_timer_name = None
		duplicate_timer_count = 1
		for timer in self.application.world.timeline.timers:
			if last_timer_name:
				if last_timer_name == timer.name:
					duplicate_timer_count += 1
				else:
					if duplicate_timer_count > 1:
						last_timer_name += (" (x" + str(duplicate_timer_count) + ")")
					self.items.append(PyCEGUI.ListboxTextItem(last_timer_name))
					self.items[-1].setAutoDeleted(False)
					self.list.addItem(self.items[-1])
					duplicate_timer_count = 1
			last_timer_name = timer.name
		if last_timer_name:
			if duplicate_timer_count > 1:
				last_timer_name += (" (x" + str(duplicate_timer_count) + ")")
			self.items.append(PyCEGUI.ListboxTextItem(last_timer_name))
			self.items[-1].setAutoDeleted(False)
			self.list.addItem(self.items[-1])

