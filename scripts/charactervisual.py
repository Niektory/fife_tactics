# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

from timeline import TacticsTimer
from damage import DamagePacket
import gridhelper

class CharacterListener(fife.InstanceActionListener):
	"""Receives fife events related to the character. Kept separate for serialization purposes."""
	def __init__(self, character):
		fife.InstanceActionListener.__init__(self)
		self.character = character

	def onInstanceActionFinished(self, instance, action):
		self.character.onInstanceActionFinished(action)

class CharacterVisual(object):
	"""Visual representation of a character."""
	STATE_IDLE, STATE_RUN, STATE_ATTACK = xrange(3)
	
	def __init__(self, application, character):
		self.application = application
		self.character = character
		self.listener = CharacterListener(self)

		self.instance = self.application.maplayer.createInstance(self.application.model.getObject("boy", "tactics"), self.character.coords)
		self.instance.setCellStackPosition(120)
		fife.InstanceVisual.create(self.instance).setStackPosition(120)
		self.instance.addActionListener(self.listener)

		self.shadow = self.application.maplayer.createInstance(self.application.model.getObject("shadow", "tactics"), self.character.coords)
		self.shadow.setCellStackPosition(116)
		fife.InstanceVisual.create(self.shadow).setStackPosition(116)

		self.fire = self.application.maplayer.createInstance(self.application.model.getObject("fire", "tactics"), self.character.coords)
		self.fire.setCellStackPosition(125)
		fife.InstanceVisual.create(self.fire).setStackPosition(125)

		if character.freeze_timer:
			self.fire.act('freeze', True)
		elif character.fire_timer:
			self.fire.act('burn', True)

		self.idle()

	def inWater(self):
		tile = self.application.world.findTileByLocation(self.instance.getLocation().getLayerCoordinates())
		if tile:
			if tile.getSurface() == "Water":
				return True
		return False

	def moveInstance(self, coords, rotation = None):
		next_loc = self.instance.getLocation()
		next_loc.setExactLayerCoordinates(gridhelper.toExact(coords))
		self.instance.setLocation(next_loc)
		if rotation != None:
			self.instance.setRotation(rotation)

		# change animation and shadow depending on whether we're in water or on land
		if self.inWater():
			if self.instance.getCurrentAction().getId() != "stand_water":
				self.instance.act("stand_water", True)
				self.shadow.act("ripples", True)
		elif self.instance.getCurrentAction().getId() != "run":
			self.instance.act("run", True)
			self.shadow.act("shadow", True)

		# move shadows under characters and fire
		self.shadow.setLocation(self.application.world.shadowLocation(next_loc))
		self.fire.setLocation(next_loc)

	def onMoveFinished(self):
		self.idle()

	def onInstanceActionFinished(self, action):
		self.idle()

	def idle(self):
		self.application.removeAnimation(self)
		self.state = self.STATE_IDLE
		if self.character.tile.getSurface() == "Water":
			self.instance.act("stand_water", True)
			self.shadow.act("ripples", True)
		else:
			self.instance.act("stand", True)
			self.shadow.act("shadow", True)

	def run(self, route):
		self.application.addAnimation(self)
		self.state = self.STATE_RUN
		if not self.inWater():
			self.instance.act("run", True)
		self.application.pather.move(self.character, route, 1)

	def push(self, dest_tile):
		self.application.addAnimation(self)
		self.application.pather.push(self.character, dest_tile, 1)

	def opportunityAttack(self, target):
		self.attack(target, "Opportunity Attack", "kick")

	def attack(self, target, attack_type, animation):
		self.application.addAnimation(self)
		self.state = self.STATE_ATTACK
		self.instance.act(animation, target.visual.instance.getLocation())
		self.application.gui.sayBubble(self.instance, attack_type)

	def beginTurn(self):
		#self.application.camera.setLocation(self.instance.getLocation())
		self.application.camera.attach(self.instance)
	
	def endTurn(self):
		self.application.gui.combat_log.printMessage(self.character.name + "'s turn ended with " + str(self.character.cur_AP) + " spare AP.")

	def die(self):
		self.instance.act('dead', True)
		self.application.gui.sayBubble(self.instance, "I regret nothing!")
		self.application.gui.combat_log.printMessage(self.character.name + " kicked the bucket.")
		
	def takeDamage(self, damage_packet):
		self.application.gui.combat_log.printMessage(self.character.name + " received " + str(damage_packet.final_damage) + " " + damage_packet.type + " damage. " + str(self.character.cur_HP) + " HP left." + " " + self.application.gui.combat_log.createLink("<details>", self.application.gui.help.createPage(damage_packet.infoString())))
		if self.character.cur_HP > 0:
			self.application.gui.sayBubble(self.instance, "Ouch!")

	def displayStats(self):
		char_msg = ''
		char_msg += str(self.character.cur_AP) + '/' + str(self.character.max_AP) + ' AP; '
		char_msg += str(self.character.cur_HP) + '/' + str(self.character.max_HP) + ' HP\n'
		if self.character.timer:
			char_msg += str(self.character.timer.getTicks()) + ' ticks to next turn'
		if self.character == self.application.world.current_character_turn:
			char_msg += 'current turn'
		if self.character.cur_HP <= 0:
			char_msg += 'dead'
		self.application.gui.sayBubble(self.instance, char_msg)

	def startBurning(self):
		self.fire.act('burn', True)
		self.application.gui.combat_log.printMessage(self.character.name + " became a walking bonfire.")

	def stopBurning(self):
		self.fire.act('none', True)
		self.application.gui.combat_log.printMessage(self.character.name + " stopped burning.")

	def freeze(self):
		self.fire.act('freeze', True)
		self.application.gui.combat_log.printMessage(self.character.name + " became an icicle.")

	def unfreeze(self):
		self.fire.act('none', True)
		self.application.gui.combat_log.printMessage(self.character.name + " unfroze.")

	def fallDownTo(self, new_tile):
		self.application.pather.fall(self.character, new_tile, 0)

