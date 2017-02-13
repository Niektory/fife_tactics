# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

import gridhelper

class Obstacle(object):
	def __init__(self, tile, height, world):
		self.world = world
		self.tile = tile
		self.height = height
		self.visual = None
		self.name = "Mr. Mushroom"
		self.top_tile = None
		self.max_HP = 10
		self.cur_HP = self.max_HP

	@property
	def coords(self):
		return self.tile.coords

	def takeDamage(self, damage_packet):
		if self.cur_HP > 0:
			self.cur_HP -= damage_packet.final_damage
			if self.visual:
				self.visual.takeDamage(damage_packet)
			if self.cur_HP <= 0:
				if self.visual:
					self.visual.destroy()
				self.world.removeObstacle(self)

	def getResistance(self, dmg_type):
		return 0

	def fallDownTo(self, new_tile):
		if self.visual:
			self.visual.fallDownTo(new_tile)
		self.tile = new_tile
		self.tile.visitors.append(self)
		self.tile.blocker = True
		# replace the tile on top of the obstacle
		self.world.removeTile(self.top_tile)
		top_coordinates = new_tile.coords
		top_coordinates.z += gridhelper.getObjectZSize(self.instance.getObject().getId())
		self.top_tile = self.world.addTile(top_coordinates, self.instance.getObject().getId())
		for visitor in self.top_tile.visitors:
			visitor.fallDownTo(new_top_tile)

	def onMoveFinished(self):
		return

	def createVisual(self):
		self.visual = ObstacleVisual(self.world.application, self)

	def burn(self):
		return


class ObstacleVisual(object):
	def __init__(self, application, obstacle):
		self.application = application
		self.obstacle = obstacle
		self.instance = self.application.maplayer.createInstance(self.application.model.getObject("mushroom", "tactics"), self.obstacle.tile.coords)
		self.instance.setCellStackPosition(120)
		fife.InstanceVisual.create(self.instance).setStackPosition(120)

	def takeDamage(self, damage_packet):
		self.application.gui.combat_log.printMessage(self.obstacle.name + " received " + str(damage_packet.final_damage) + " " + damage_packet.type + " damage. " + str(self.obstacle.cur_HP) + " HP left." + " " + self.application.gui.combat_log.createLink("<details>", self.application.gui.help.createPage(damage_packet.infoString())))
		self.application.gui.sayBubble(self.instance, "hit")

	def destroy(self):
		self.application.gui.combat_log.printMessage(self.obstacle.name + " was destroyed.")
		self.application.maplayer.deleteInstance(self.instance)

	def fallDownTo(self, new_location):
		self.application.pather.fall(self.obstacle, new_location, 0)
