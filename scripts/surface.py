# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

from timeline import TacticsTimer

class SurfaceTar(object):
	def __init__(self, tile, world):
		self.tile = tile
		self.world = world
		self.visual = None
		self.name = "Tar"
		self.fire_timer = None

	@property
	def coords(self):
		return self.tile.coords

	def startBurning(self):
		if not self.fire_timer:
			self.fire_timer = TacticsTimer(self.name + " burns out", 24, 1, self.burnOut, self.burn, 3)
			self.world.timeline.addTimer(self.fire_timer)
			if self.visual:
				self.visual.startBurning()

	def burn(self):
		for visitor in self.tile.visitors:
			visitor.burn()

	def burnOut(self):
		if self.fire_timer:
			if self.world.timeline.timers.count(self.fire_timer):
				self.world.timeline.timers.remove(self.fire_timer)
			self.tile.surface_effects.remove(self)
			if self.visual:
				self.visual.burnOut()
				self.visual.destroy()

	def stopBurning(self):
		if self.fire_timer:
			if self.world.timeline.timers.count(self.fire_timer):
				self.world.timeline.timers.remove(self.fire_timer)
			self.fire_timer = None
			if self.visual:
				self.visual.stopBurning()

	def createVisual(self):
		self.visual = TarVisual(self.world.application, self)


class TarVisual(object):
	def __init__(self, application, surface):
		self.application = application
		self.surface = surface
		self.instance = self.application.maplayer.createInstance(self.application.model.getObject("tar", "tactics"), self.surface.coords)
		self.instance.setCellStackPosition(114)
		fife.InstanceVisual.create(self.instance).setStackPosition(114)
		if self.surface.fire_timer:
			self.instance.actRepeat("burn")
		else:
			self.instance.actRepeat("tar")

	def destroy(self):
		self.application.maplayer.deleteInstance(self.instance)

	def startBurning(self):
		self.instance.actRepeat("burn")
		self.application.gui.combat_log.printMessage(self.surface.name + " caught fire.")

	def burnOut(self):
		self.application.gui.combat_log.printMessage(self.surface.name + " burned out.")

	def stopBurning(self):
		self.application.gui.combat_log.printMessage(self.surface.name + " stopped burning.")
		self.instance.actRepeat("tar")


class SurfaceIce(object):
	def __init__(self, tile, world):
		self.tile = tile
		self.world = world
		self.visual = None
		self.name = "Ice"
		self.fire_timer = None

	@property
	def coords(self):
		return self.tile.coords

	def startBurning(self):
		if self.visual:
			self.visual.startBurning()
		self.tile.surface_effects.remove(self)
		for trap in self.tile.traps:
			trap.destroy()
#		for visitor in self.application.grid.findTileByLocation(self.instance.getLocation()).visitors:
#			visitor.idle()
		if self.visual:
			self.visual.destroy()

	def stopBurning(self):
		return

	def createVisual(self):
		self.visual = IceVisual(self.world.application, self)


class IceVisual(object):
	def __init__(self, application, surface):
		self.application = application
		self.surface = surface
		self.instance = self.application.maplayer.createInstance(self.application.model.getObject("ice", "tactics"), self.surface.coords)
		self.instance.setCellStackPosition(114)
		fife.InstanceVisual.create(self.instance).setStackPosition(114)

	def destroy(self):
		self.application.maplayer.deleteInstance(self.instance)

	def startBurning(self):
		self.application.gui.combat_log.printMessage(self.surface.name + " melted.")
