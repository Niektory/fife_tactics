# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from random import uniform

from battlecommand import BattleCommand
from character import TacticsCharacter
from damage import DamagePacket
import serializer
from battlecontroller import BattleController
from actions import TargetingRules
from replay import Replay
import gridhelper

class AI(object):
	def __init__(self, application, world):
		self.application = application
		self.world = world

	def scoreHate(self, source, target):
		if source.team == target.team:
			return -1.2
		else:
			return 1

	def scoreDamage(self, damage):
		score = float(damage.final_damage) / damage.target.cur_HP * 0.6
		if score >= 0.6:
			score = 1
		else:
			if not damage.target.fire_timer and not damage.target.freeze_timer:
				if damage.add_effect == "burn":
					score += 2.0 / damage.target.cur_HP
				elif damage.add_effect == "freeze":
					score += 0.2
			score = min(score, 0.9)
		#if damage.source == damage.target:
		#	score *= -1
		score *= self.scoreHate(damage.source, damage.target)
		return score

	def scoreAP(self, AP_cost, character):
		return float(AP_cost) / character.max_AP

	def scoreEndTurn(self, character):
		return 0.01

	def scoreAction(self, action, target, world):
		score = 0
		if action.name == "Kick":
			score += self.scoreDamage(DamagePacket(world.current_character_turn, target, 6, "kinetic", "push"))
		elif action.name == "Throw Stone":
			score += self.scoreDamage(DamagePacket(world.current_character_turn, target, 4, "kinetic"))
		elif action.name == "Fireball":
			targeting_rules = TargetingRules(action.targeting_rules.trajectory, action.targeting_rules.area, False, True, False, False)
			targets = world.getTargetsInArea(world.current_character_turn, target, targeting_rules)
			for aoe_target in targets:
				if type(aoe_target) == TacticsCharacter:
					if aoe_target.cur_HP > 0:
						score += self.scoreDamage(DamagePacket(world.current_character_turn, aoe_target, 5 - 2 * gridhelper.horizontalDistance(target.coords, aoe_target.coords), "fire", "burn"))
		elif action.name == "Cone of Cold":
			targeting_rules = TargetingRules(action.targeting_rules.trajectory, action.targeting_rules.area, False, True, False, False)
			targets = world.getTargetsInArea(world.current_character_turn, target, targeting_rules)
			for aoe_target in targets:
				if type(aoe_target) == TacticsCharacter:
					if aoe_target.cur_HP > 0:
						score += self.scoreDamage(DamagePacket(world.current_character_turn, aoe_target, 4, "cold", "freeze"))
		self.actions_considered += 1
		return score * uniform(1, 1.1)

	def scoreMove(self, move, turns, world):
		#world = serializer.restore(world_buffer)
		#controller = BattleController(self.application, world)
		move_cost = move.movement_cost
		move_source = world.current_character_turn.tile
		if turns > 0:
			original_AP = world.current_character_turn.cur_AP
			world.current_character_turn.cur_AP = world.current_character_turn.max_AP * turns
		world.current_character_turn.tempMove(move, move_cost)
		best_command = None
		best_score = 0
		best_score_nocost = 0
		best_score_cost = 0

		for action in world.current_character_turn.combat_actions:
			if action.AP_cost <= world.current_character_turn.cur_AP:
				valid_targets = world.getValidTargets(world.current_character_turn, action.targeting_rules)
				for target in valid_targets:
					score_nocost = self.scoreAction(action, target, world)
					score = score_nocost / self.scoreAP(action.AP_cost, world.current_character_turn)
					if score > best_score:
						best_command = BattleCommand("executeAction", target.ID, action)
						best_score = score
						best_score_nocost = score_nocost
						best_score_cost = action.AP_cost
		if best_score > 0:
		#	print "Best action for move", move.ID, "score:", best_score
			pass
		else:
			self.actions_considered += 1

		world.current_character_turn.tempMove(move_source, -move_cost)
		if turns > 0:
			world.current_character_turn.cur_AP = original_AP
		return best_score_nocost / self.scoreAP(move_cost + best_score_cost, self.world.current_character_turn) * uniform(1, 1.1), best_command

	def getCommand(self, pipe):
		#world_buffer = serializer.dump(self.world)
		best_commands = [BattleCommand("endTurn")]
		best_score = self.scoreEndTurn(self.world.current_character_turn)
		self.actions_considered = 1

		# action without movement with current AP
		for action in self.world.current_character_turn.combat_actions:
			if action.AP_cost <= self.world.current_character_turn.cur_AP:
				valid_targets = self.world.getValidTargets(self.world.current_character_turn, action.targeting_rules)
				for target in valid_targets:
					score = self.scoreAction(action, target, self.world) / self.scoreAP(action.AP_cost, self.world.current_character_turn)
					if score > best_score:
						best_commands = [BattleCommand("executeAction", target.ID, action)]
						best_score = score

		#if best_commands[0].command == "executeAction":
		#	print "Best action score:", best_score

		# movement + action with current AP
		possible_moves = self.world.possibleMoves()
		counter = 0
		for move in possible_moves:
			score, action = self.scoreMove(move, 0, self.world)
			if score > best_score:
				best_commands = [BattleCommand("run", move.ID), action]
				best_score = score
			counter += 1
			pipe.send(float(counter) / len(possible_moves))

		# if no move was found yet we'll try multiturn moves
		if best_commands[0].command == "endTurn":
			# action with increased AP
			for action in self.world.current_character_turn.combat_actions:
				valid_targets = self.world.getValidTargets(self.world.current_character_turn, action.targeting_rules)
				for target in valid_targets:
					score = self.scoreAction(action, target, self.world) / self.scoreAP(action.AP_cost, self.world.current_character_turn)
					if score > best_score:
						best_commands = [BattleCommand("executeAction", target.ID, action), BattleCommand("endTurn")]
						best_score = score

			# movement + action with increased AP
			turns = 1
			while True:
				possible_moves = self.world.possibleMoves(turns)
				#print "turns:", turns, "; len(possible_moves):", len(possible_moves)
				if len(possible_moves) == 0:
					break
				counter = 0
				for move in possible_moves:
					score, action = self.scoreMove(move, turns, self.world)
					if score > best_score:
						best_commands = [BattleCommand("run", move.ID), action, BattleCommand("endTurn")]
						best_score = score
					counter += 1
					#if (counter % 4) == 0:
					pipe.send(float(counter) / len(possible_moves))
				if best_commands[0].command != "endTurn":
					break
				turns += 1

		#if best_commands[0].command == "run":
		#	print "Best move score:", best_score

		#print "Commands considered:", self.actions_considered
		#return best_command
		replay = Replay()
		replay.commands = best_commands
		pipe.send(replay)
