# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife
from random import randint

from timeline import TacticsTimer
from damage import DamagePacket
import gridhelper
from charactervisual import CharacterVisual

class TacticsCharacter(object):
	"""Represents a character."""
	def __init__(self, name, tile, world):
		self.world = world
		if name == "":
			self.name = "Nameless"
		else:
			self.name = name
		self.team = 0
		self.tile = tile
		self.visual = None
		self.height = 3
		self.max_AP = 6
		self.cur_AP = 0
		self.max_HP = 20
		self.cur_HP = self.max_HP
		self.timer = TacticsTimer(self.name + "'s turn", 20, 1, self.beginTurn)
		self.fire_timer = None
		self.freeze_timer = None
		self.world.timeline.addTimer(self.timer)
		self.combat_actions = []
		self.max_opportunity_attacks = 0
		self.opportunity_attacks = 0
		self.fall_damage = 0

	@property
	def coords(self):
		return self.tile.coords

	def onMoveFinished(self):
		if self.visual:
			self.visual.onMoveFinished()
		if self.fall_damage > 0:
			self.takeDamage(DamagePacket("fall", self, self.fall_damage, "fall"))
			self.fall_damage = 0
		for trap in self.tile.traps:
			trap.trigger(self)

	def move(self, dest_tile):
		self.tile.visitors.remove(self)
		self.tile.blocker = False
		dest_tile.visitors.append(self)
		dest_tile.blocker = True
		self.tile = dest_tile

	def tempMove(self, dest_tile, cost):
		self.cur_AP -= cost
		self.move(dest_tile)

	def run(self, route):
		self.cur_AP -= route.destination.movement_cost
		if self.visual:
			self.visual.run(route)
		self.move(route.destination)
		if not self.visual:
			self.onMoveFinished()

	def push(self, dest_tile):
		self.fall_damage = max(0, self.coords.z - dest_tile.coords.z - 3)
		if self.visual:
			self.visual.push(dest_tile)
		self.move(dest_tile)
		if not self.visual:
			self.onMoveFinished()

	def planRoute(self, dest_tile):
		return self.world.application.pather.planMove(self, dest_tile).path

	def opportunityAttack(self, target):
		if self.visual:
			self.visual.opportunityAttack(target)
		target.takeDamage(DamagePacket(self, target, 6, "kinetic"))
		self.opportunity_attacks -= 1

	def beginTurn(self):
		self.cur_AP = self.max_AP
		self.world.current_character_turn = self
		self.timer = None
		self.world.createMovementGrid(self)
		if self.visual:
			self.visual.beginTurn()
	
	def endTurn(self):
		if self.visual:
			self.visual.endTurn()
		self.timer = TacticsTimer(self.name + "'s turn", 20 - self.cur_AP * 6 / self.max_AP, 1, self.beginTurn)
		self.cur_AP = 0
		self.world.timeline.addTimer(self.timer)
		self.world.current_character_turn = None
		self.opportunity_attacks = self.max_opportunity_attacks

	def die(self):
		self.cur_AP = 0
		if self.world.current_character_turn == self:
			self.world.current_character_turn = None
		self.stopBurning()
		self.unfreeze()
		if self.timer:
			self.world.timeline.timers.remove(self.timer)
			self.timer = None
		if self.visual:
			self.visual.die()

	def takeDamage(self, damage_packet):
		if self.cur_HP > 0:
			self.cur_HP -= damage_packet.final_damage
			if self.visual:
				self.visual.takeDamage(damage_packet)
			if self.cur_HP <= 0:
				self.die()

		if self.cur_HP > 0:
			if damage_packet.add_effect == "knockback":
				self.pushBack(gridhelper.calcDirection(damage_packet.source.coords, self.coords))
			if damage_packet.add_effect == "pull":
				self.pushBack(gridhelper.calcDirection(self.coords, damage_packet.source.coords))
			if damage_packet.add_effect == "burn":
				self.startBurning()
			if damage_packet.add_effect == "freeze":
				self.freeze()
			if damage_packet.add_effect == "reduce AP":
				self.cur_AP -= 2

	def getResistance(self, dmg_type):
		return 0
			
	def startBurning(self):
		if not self.fire_timer and (self.tile.getSurface() != "Water"):
			self.unfreeze()
			self.fire_timer = TacticsTimer(self.name + " stops burning", 12, 1, self.stopBurning, self.burn, 3)
			self.world.timeline.addTimer(self.fire_timer)
			if self.visual:
				self.visual.startBurning()

	def burn(self):
		self.takeDamage(DamagePacket("fire", self, 1, "fire"))

	def stopBurning(self):
		if self.fire_timer:
			if self.world.timeline.timers.count(self.fire_timer):
				self.world.timeline.timers.remove(self.fire_timer)
			self.fire_timer = None
			if self.visual:
				self.visual.stopBurning()

	def freeze(self):
		if not self.freeze_timer:
			self.stopBurning()
			if randint(0, 2) == 0:
				self.freeze_timer = TacticsTimer(self.name + " unfreezes", 4, 1, self.unfreeze)
				self.world.timeline.addTimer(self.freeze_timer)
				if self.world.timeline.timers.count(self.timer):
					self.world.timeline.timers.remove(self.timer)
				self.timer = None
				if self.visual:
					self.visual.freeze()

	def unfreeze(self):
		if self.freeze_timer:
			if self.world.timeline.timers.count(self.freeze_timer):
				self.world.timeline.timers.remove(self.freeze_timer)
			self.freeze_timer = None
			self.timer = TacticsTimer(self.name + "'s turn", 20, 1, self.beginTurn)
			self.world.timeline.addTimer(self.timer)
			if self.visual:
				self.visual.unfreeze()

	def fallDownTo(self, new_tile):
		if self.visual:
			self.visual.fallDownTo(new_tile)
		self.move(new_tile)

	def pushBack(self, direction):
		tile_column = self.world.getTilesByLocation(self.coords + direction)
		for tile in tile_column:
			if (not tile.blocker) and (tile.coords.z <= self.coords.z):
				self.push(tile)
				break

	def addAction(self, action):
		self.combat_actions.append(action)

	def hasAction(self, action_str):
		for action in self.combat_actions:
			if action.name == action_str:
				return True
		return False
		#return action_str in self.combat_actions

	def isThreatening(self, tile):
		if (self.opportunity_attacks > 0) and self.timer and gridhelper.inMeleeRange(self.coords, tile.coords):
			return True
		else:
			return False

	def createVisual(self):
		self.visual = CharacterVisual(self.world.application, self)
