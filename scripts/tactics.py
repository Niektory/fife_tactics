#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

from fife import fife
from fife.extensions.pychan.pychanbasicapplication import PychanApplicationBase
from fife.extensions.cegui.ceguibasicapplication import CEGUIApplicationBase, CEGUIEventListener
from fife.extensions.soundmanager import SoundManager
import pickle
from traceback import print_exc
import cProfile
from multiprocessing import Process, Pipe

from input import TacticsMouseListener, TacticsKeyListener
from view import TacticsView
from timeline import RealTimeline
from character import TacticsCharacter
from world import World
from worldvisual import WorldVisual
from pather import TacticsPather
from actions import CombatActions
from obstacle import Obstacle
from trap import Trap
from surface import SurfaceTar, SurfaceIce
from gui import TacticsGUI
import serializer
from battlecontroller import BattleController
from ai import AI
from replay import Replay

class TacticsListener(CEGUIEventListener):
	def __init__(self, app):
		super(TacticsListener, self).__init__(app)

	def keyPressed(self, evt):
		pass

class TacticsApplication(CEGUIApplicationBase, PychanApplicationBase):
	def __init__(self, settings):
		print "* Initializing application..."
		super(TacticsApplication, self).__init__(settings)
		self.settings = settings
		self.model = self.engine.getModel()
		self.mapLoader = fife.MapLoader(self.model, 
									self.engine.getVFS(), 
									self.engine.getImageManager(), 
									self.engine.getRenderBackend())
		self.objectLoader = fife.ObjectLoader(self.model, 
									self.engine.getVFS(), 
									self.engine.getImageManager())
		self.atlasLoader = fife.AtlasLoader(self.model, 
									self.engine.getVFS(), 
									self.engine.getImageManager())
		self.map = None
		self.view = None

		self.eventmanager = self.engine.getEventManager()
		self.mouselistener = TacticsMouseListener(self)
		self.keylistener = TacticsKeyListener(self)
		self.eventmanager.addMouseListenerFront(self.mouselistener)
		self.eventmanager.addKeyListenerFront(self.keylistener)
		self.soundmanager = SoundManager(self.engine)
		self.fifesoundmanager = self.engine.getSoundManager()
		print "* Application initialized!"

		self.combat_actions = CombatActions()
		self.gui = TacticsGUI(self)
		self.real_timeline = RealTimeline()
		self.engine.getTimeManager().registerEvent(self.real_timeline)
		self.pather = TacticsPather(self)
		self.engine.getTimeManager().registerEvent(self.pather)

		self.loadObject("objects/tile.xml")
		self.loadObject("objects/boy/object.xml")
		self.loadObject("objects/dot_red.xml")
		self.loadObject("objects/shadow.xml")
		self.loadObject("objects/effects/fire.xml")
		self.loadObject("objects/effects/explosion.xml")
		self.loadObject("objects/effects/freeze.xml")
		self.loadObject("objects/projectiles/stone.xml")
		self.loadObject("objects/projectiles/fireball.xml")
		self.loadObject("objects/projectiles/tarball.xml")
		self.loadAtlas("objects/nature.xml")
		self.loadObject("objects/caltrops.xml")
		self.loadObject("objects/tar.xml")
		self.loadObject("objects/ice.xml")
		self.loadObject("objects/water_under.xml")
		self.loadObject("objects/water.xml")
		self.loadObject("objects/block_gray.xml")
		self.loadObject("objects/block_grass.xml")

		self.music = self.soundmanager.createSoundEmitter("music/music1.ogg")
		self.sound_attack = self.soundmanager.createSoundEmitter("sfx/attack-1.ogg")
		self.sound_fire = self.soundmanager.createSoundEmitter("sfx/fire-1.ogg")
		self.music.looping = True
		if not self.settings.get("FIFE", "PlaySounds"):
			self.fifesoundmanager.setVolume(0.0)
		self.music.play()

		self.unloadMap()

	def createListener(self):
		self._listener = TacticsListener(self)
		return self._listener

	def loadObject(self, filename):
		if self.objectLoader.isLoadable(filename):
			self.objectLoader.load(filename)
		else:
			print "can't load ", filename

	def loadAtlas(self, filename):
		if self.atlasLoader.isLoadable(filename):
			self.atlasLoader.load(filename)
		else:
			print "can't load ", filename

	def loadMap(self, map_name):
		filename = "maps/" + map_name + ".xml"
		if self.mapLoader.isLoadable(filename):
			print "* Loading map " + map_name
			self.map = self.mapLoader.load(filename)
			self.camera = self.map.getCamera("camera1")
			self.maplayer = self.map.getLayer("layer1")
			print "* Map loaded!"
		else:
			print "can't load map"

	def unloadMap(self):
		if self.map:
			self.model.deleteMap(self.map)
		self.map = None
		self.world = None
		self.view = None
		self.animations = []
		self.replaying = False
		self.ai_play = False
		self.selected_action = None

	def newGame(self):
		print "* Starting new game..."
		self.unloadMap()
		self.loadMap("map1")
		self.world = World(self, self.maplayer)
		self.world.visual = WorldVisual()
		self.world.visual.initFromMap(self, self.maplayer, self.world)
		self.battle_controller = BattleController(self, self.world)
		self.ai = AI(self, self.world)
		self.view = TacticsView(self)
		self.gui.showHUD()

	def saveGame(self, save_name):
		serializer.save(self.world, "saves/" + save_name + ".sav")
		self.gui.combat_log.printMessage("Game saved.")

	def loadGame(self, save_name):
		self.unloadMap()
		self.world = serializer.load("saves/" + save_name + ".sav")
		self.world.application = self
		self.battle_controller = BattleController(self, self.world)
		self.ai = AI(self, self.world)
		self.createVisual()
		print "* Game loaded!"

	def createVisual(self):
		self.loadMap("empty")
		self.world.maplayer = self.maplayer
		self.world.visual = WorldVisual()
		self.world.visual.initFromWorld(self, self.maplayer, self.world)
		self.view = TacticsView(self)
		self.gui.showHUD()

	def startReplay(self):
		self.unloadMap()
		self.replay = Replay()
		self.world = self.replay.loadWorld()
		self.world.application = self
		self.battle_controller = BattleController(self, self.world)
		self.ai = AI(self, self.world)
		self.createVisual()
		self.replay.loadCommands()

	def selectAction(self, action_name):
		if self.current_character:
			self.selected_action = self.combat_actions.getAction(action_name)

	def endTurn(self, args):
		try:
			if self.world.current_character_turn:
				self.battle_controller.endTurn()
		except:
			print_exc()
			raise

	def addAnimation(self, animation):
		self.animations.append(animation)

	def removeAnimation(self, animation):
		if self.animations.count(animation):
			self.animations.remove(animation)
			if not self.animating() and self.world.current_character_turn:
				self.world.createMovementGrid(self.world.current_character_turn)

	def animating(self):
		return len(self.animations) > 0

	@property
	def current_character(self):
		return self.world.current_character_turn

	@property
	def selected_action(self):
		if self.current_character:
			return self._selected_action
		else:
			return None

	@selected_action.setter
	def selected_action(self, value):
		self._selected_action = value

	def AIMove(self):
		if not self.animating() and self.world.current_character_turn:
			#cProfile.runctx("self.AI_command = self.ai.getCommand()", globals(), locals(), sort = "cumulative")
			#self.AI_command = self.ai.getCommand()
			self.ai_output, ai_input = Pipe(False)
			#cProfile.runctx("self.ai.getCommand(ai_input)", globals(), locals(), sort = "cumulative")
			Process(target = self.ai.getCommand, args = (ai_input,)).start()
			self.addAnimation(self.ai)
			self.gui.ai_status.show()

	def startAIPlay(self):
		self.ai_play = True

	def _pump(self):
		if self.world:
			if not self.animating() and self.replaying and self.world.current_character_turn:
				command = self.replay.getCommand()
				if command:
					self.battle_controller.executeCommand(command)
				else:
					self.replaying = False
			elif not self.animating() and self.ai_play and self.world.current_character_turn:
				if len(self.world.getSurvivingTeams()) > 1:
					self.AIMove()
				else:
					self.ai_play = False
					for character in self.world.characters:
						if character.cur_HP > 0:
							self.gui.sayBubble(character.visual.instance, "Victory!")
			elif not self.animating() and self.world.current_character_turn:
				if self.world.current_character_turn.cur_AP <= 0:
					self.battle_controller.endTurn()
			elif not self.animating() and not self.world.current_character_turn:
				action = self.world.timeline.popAction()
				if action:
					action()
			elif self.animations.count(self.ai) > 0:
				ai_message = None
				while self.ai_output.poll():
					ai_message = self.ai_output.recv()
					#print ai_message, type(ai_message)
					if type(ai_message) == Replay:
						self.replay = ai_message
						self.replaying = True
						self.removeAnimation(self.ai)
						self.gui.ai_status.window.hide()
						break
				if type(ai_message) == float:
					self.gui.ai_status.progress_bar.setProgress(ai_message)
			#if not self.world.visual and not self.replaying:
			#	self.createVisual()
			if self.world.visual:
				self.gui.pump()
				self.view.pump()
		if self._listener.quitrequested:
			self.quit()
			

