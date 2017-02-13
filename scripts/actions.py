# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from character import TacticsCharacter
from tile import TacticsTile
from effects import Explosion, Projectile
from damage import DamagePacket
import gridhelper

class Trajectory(object):
	"""
	determines method used to check if a target can be targeted at all
	SINGLE - can target everything within a radius from the source
	LINE - requires line of sight between the source and the target
	ARC - requires that an arc could be drawn between the source and the target (for projectiles affected by gravity)
	"""
	TRAJECTORY_SINGLE, TRAJECTORY_LINE, TRAJECTORY_ARC = xrange(3)
	
class TrajectorySingle(Trajectory):
	def __init__(self, range_horizontal, range_up, range_down):
		self.type = self.TRAJECTORY_SINGLE
		self.range = range_horizontal
		self.range_up = range_up
		self.range_down = range_down

class TrajectoryLine(Trajectory):
	def __init__(self, range_horizontal, range_up, range_down):
		self.type = self.TRAJECTORY_LINE
		self.range = range_horizontal
		self.range_up = range_up
		self.range_down = range_down

class TrajectoryArc(Trajectory):
	def __init__(self, range_horizontal):
		self.type = self.TRAJECTORY_ARC
		self.range = range_horizontal

class Area(object):
	"""
	determines method used to determine the area of effect given a valid single target
	SINGLE - affects only the target
	CIRCLE - affects everything within a radius from the target
	LINE - affects everything in between the source and the target
	CONE - affects everything in a cone originating at the source and facing the target
	"""
	AREA_SINGLE, AREA_CIRCLE, AREA_LINE, AREA_CONE = xrange(4)

class AreaSingle(Area):
	def __init__(self):
		self.type = self.AREA_SINGLE

class AreaCircle(Area):
	def __init__(self, radius, range_up, range_down):
		self.type = self.AREA_CIRCLE
		self.radius = radius
		self.range_up = range_up
		self.range_down = range_down

class AreaLine(Area):
	def __init__(self, length):
		self.type = self.AREA_LINE
		self.length = length
		
class AreaCone(Area):
	def __init__(self, radius, range_up, range_down):
		self.type = self.AREA_CONE
		self.radius = radius
		self.range_up = range_up
		self.range_down = range_down

class TargetingRules(object):
	def __init__(self, trajectory, area, can_target_self, can_target_other, can_target_tile, can_target_obstacle):
		self.trajectory = trajectory
		self.area = area
		self.can_target_self = can_target_self
		self.can_target_other = can_target_other
		self.can_target_tile = can_target_tile
		self.can_target_obstacle = can_target_obstacle


class CombatAction(object):
	def execute(self, source, initial_target, target_list):
		self.source = source
		self.initial_target = initial_target
		self.target_list = target_list
		if source.cur_AP < self.AP_cost:
			if source.visual:
				self.application.gui.sayBubble(source.visual.instance, "Not enough AP")
			return
		source.cur_AP -= self.AP_cost
		self.initialAction()

	def initialAction(self):
		pass

	def targetAction(self):
		pass
		
		
class KickAction(CombatAction):
	name = "Kick"
	targeting_rules = TargetingRules(TrajectorySingle(1, 1, 3), AreaSingle(), False, True, False, True)
	AP_cost = 2
	def __init__(self, application):
		self.application = application

	def initialAction(self):
		if self.source.visual:
			self.application.sound_attack.play()
			self.source.visual.attack(self.initial_target, "Kick", "kick")
		self.targetAction()

	def targetAction(self):
		self.initial_target.takeDamage(DamagePacket(self.source, self.initial_target, 6, "kinetic", "knockback"))


class ThrowStoneAction(CombatAction):
	name = "Throw Stone"
	targeting_rules = TargetingRules(TrajectoryArc(5), AreaSingle(), False, True, False, False)
	AP_cost = 2
	def __init__(self, application):
		self.application = application
	
	def initialAction(self):
		if self.source.visual:
			self.application.sound_attack.play()
			self.source.visual.attack(self.initial_target, "Throw Stone", "cheer")
			self.projectile = Projectile(self.application, self.source.coords, self.initial_target.coords, self.targetAction, "stone", self.targeting_rules.trajectory)
		else:
			self.targetAction()

	def targetAction(self):
		self.initial_target.takeDamage(DamagePacket(self.source, self.initial_target, 4, "kinetic"))


class FireballAction(CombatAction):
	name = "Fireball"
	targeting_rules = TargetingRules(TrajectoryArc(5), AreaCircle(3, 2, 3), False, True, True, False)
	AP_cost = 4
	def __init__(self, application):
		self.application = application
		self.explosions = []

	def initialAction(self):
		if self.source.visual:
			self.source.visual.attack(self.initial_target, "Fireball", "cheer")
			self.projectile = Projectile(self.application, self.source.coords, self.initial_target.coords, self.targetAction, "fireball", self.targeting_rules.trajectory)
		else:
			self.targetAction()

	def targetAction(self):
		if self.source.visual:
			self.application.sound_fire.play()
		for target in self.target_list:
			if type(target) == TacticsCharacter:
				target.takeDamage(DamagePacket(self.source, target, 5 - 2 * gridhelper.horizontalDistance(target.coords, self.initial_target.coords), "fire", "burn"))
			if type(target) == TacticsTile:
				if target.visual:
					self.explosions.append(Explosion(self.application, target.coords, "explosion"))
				for surface in target.surface_effects:
					surface.startBurning()
		
		
class ConeOfColdAction(CombatAction):
	name = "Cone of Cold"
	targeting_rules = TargetingRules(TrajectoryLine(5, 2, 3), AreaCone(6, 2, 3), False, True, True, False)
	AP_cost = 4
	def __init__(self, application):
		self.application = application
		self.explosions = []

	def initialAction(self):
		if self.source.visual:
			self.source.visual.attack(self.initial_target, "Cone of Cold", "talk")
		self.targetAction()

	def targetAction(self):
		for target in self.target_list:
			if type(target) == TacticsCharacter:
				target.takeDamage(DamagePacket(self.source, target, 4, "cold", "freeze"))
			if type(target) == TacticsTile:
				if target.visual:
					self.explosions.append(Explosion(self.application, target.coords, "freeze"))
				for surface in target.surface_effects:
					surface.stopBurning()
				if target.getSurface() == "Water":
					self.application.world.addSurfaceAt(target, "ice")


class PlantMushroomAction(CombatAction):
	name = "Plant Mushroom"
	targeting_rules = TargetingRules(TrajectorySingle(1, 1, 3), AreaSingle(), False, False, True, False)
	AP_cost = 3
	def __init__(self, application):
		self.application = application

	def initialAction(self):
		if self.source.visual:
			self.source.visual.attack(self.initial_target, "Plant Mushroom", "talk")
		self.targetAction()

	def targetAction(self):
		self.application.world.addObstacleAt(self.initial_target, "mushroom")


class CaltropsAction(CombatAction):
	name = "Caltrops"
	targeting_rules = TargetingRules(TrajectorySingle(1, 1, 3), AreaSingle(), False, False, True, False)
	AP_cost = 3
	def __init__(self, application):
		self.application = application

	def initialAction(self):
		if self.source.visual:
			self.source.visual.attack(self.initial_target, "Caltrops", "talk")
		self.targetAction()

	def targetAction(self):
		self.application.world.addTrapAt(self.initial_target, "caltrops")


class TarballAction(CombatAction):
	name = "Tarball"
	targeting_rules = TargetingRules(TrajectoryArc(4), AreaCircle(2, 1, 3), False, False, True, False)
	AP_cost = 3
	def __init__(self, application):
		self.application = application
		self.explosions = []

	def initialAction(self):
		if self.source.visual:
			self.source.visual.attack(self.initial_target, "Tarball", "cheer")
			self.projectile = Projectile(self.application, self.source.coords, self.initial_target.coords, self.targetAction, "tarball", self.targeting_rules.trajectory)
		else:
			self.targetAction()

	def targetAction(self):
		for target in self.target_list:
			if target.getSurface() not in ["Water", "Ice"]:
				self.application.world.addSurfaceAt(target, "tar")


class PersonalMagnetismAction(CombatAction):
	name = "Personal Magnetism"
	targeting_rules = TargetingRules(TrajectorySingle(5, 8, 8), AreaSingle(), False, True, False, False)
	AP_cost = 2
	def __init__(self, application):
		self.application = application
	
	def initialAction(self):
		if self.source.visual:
			self.source.visual.attack(self.initial_target, "Personal Magnetism", "talk")
		self.targetAction()

	def targetAction(self):
		self.initial_target.takeDamage(DamagePacket(self.source, self.initial_target, 0, "mental", "pull"))


class CombatActions(object):
	def __init__(self):
		self.actions = []
		self.actions.append(KickAction)
		self.actions.append(ThrowStoneAction)
		self.actions.append(FireballAction)
		self.actions.append(ConeOfColdAction)
		self.actions.append(PlantMushroomAction)
		self.actions.append(CaltropsAction)
		self.actions.append(TarballAction)
		self.actions.append(PersonalMagnetismAction)
		
	def getAction(self, name):
		for action in self.actions:
			if action.name == name:
				return action
