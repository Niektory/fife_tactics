# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

from damage import DamagePacket

class Trap(object):
	def __init__(self, tile, world):
		self.tile = tile
		self.world = world
		self.visual = None
		self.name = "Caltrops"

	@property
	def coords(self):
		return self.tile.coords

	def fallDownTo(self, new_tile):
		if self.visual:
			self.visual.fallDownTo(new_tile)
		self.tile = new_tile
		self.tile.traps.append(self)

	def onMoveFinished(self):
		return

	def trigger(self, character):
		character.takeDamage(DamagePacket(self, character, 2, "piercing", "reduce AP"))
		self.destroy()

	def destroy(self):
		self.tile.traps.remove(self)
		if self.visual:
			self.visual.destroy()

	def createVisual(self):
		self.visual = TrapVisual(self.world.application, self)


class TrapVisual(object):
	def __init__(self, application, trap):
		self.application = application
		self.trap = trap
		self.instance = self.application.maplayer.createInstance(self.application.model.getObject("caltrops", "tactics"), self.trap.coords)
		self.instance.setCellStackPosition(118)
		fife.InstanceVisual.create(self.instance).setStackPosition(118)

	def fallDownTo(self, new_tile):
		self.application.pather.fall(self, new_tile, 0)

	def destroy(self):
		self.application.maplayer.deleteInstance(self.instance)
