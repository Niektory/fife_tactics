# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

#from functools import total_ordering

from fife import fife

#@total_ordering
class TacticsTimer:
	def __init__(self, name, time, tick_speed, action, tick_action = None, tick_action_delay = 1):
		self.name = name
		self.time = time
		self.tick_speed = tick_speed
		self.action = action
		self.tick_action = tick_action
		self.tick_action_delay = tick_action_delay
		self.tick_action_counter = tick_action_delay
	
	def tick(self, time = 1):
		#print self.name, self.time, self.tick_speed
		if self.tick_action:
			self.tick_action_counter -= 1
			if self.tick_action_counter == 0:
				self.tick_action()
				self.tick_action_counter = self.tick_action_delay
		self.time -= self.tick_speed * time
		
	def getTicks(self):
		return self.time / self.tick_speed

#	def __eq__(self, other):
#		return (self.getTicks() == other.getTicks())
#	def __lt__(self, other):
#		return (self.getTicks() < other.getTicks())

class TacticsTimeline:
	def __init__(self):
		self.timers = []

	def tick(self):
		for timer in self.timers:
			timer.tick()
	
	def addTimer(self, timer):
		self.timers.append(timer)
		self.timers.sort(key=TacticsTimer.getTicks)
	
	def popAction(self):
		while len(self.timers) > 0:
			for timer in self.timers:
				if timer.time <= 0:
					action = timer.action
					self.timers.remove(timer)
					return action
			self.tick()
			
class RealTimeline(fife.TimeEvent):
	def __init__(self):
		super(RealTimeline, self).__init__(0)
		self.timers = []

	def tick(self, time):
		for timer in self.timers:
			timer.tick(time)
	
	def addTimer(self, timer):
		self.timers.append(timer)
	
	def updateEvent(self, time):
		if self.timers == []:
			return None
		for timer in self.timers:
			if timer.time <= 0:
				action = timer.action
				self.timers.remove(timer)
				action()
				#return #test
		self.tick(time)
