'''
Population class for Deep HyperNEAT

Felix Sosa
'''
import numpy as np
# import seaborn as sns
import matplotlib.pyplot as plt 

from genome import Genome
from reproduction import Reproduction
from six_util import iteritems,itervalues,iterkeys
from species import SpeciesSet
from reporters import report_fitness, report_species
class Population():

	def __init__(self, key, size, elitism=1, state=None):
		self.key = key
		self.size = size
		self.best_genome = None
		self.max_complex_genome = None
		self.min_complex_genome = None
		self.last_best = 0
		self.current_gen = 0
		self.elitism = elitism
		self.reproduction = Reproduction()
		self.species = SpeciesSet(4.5)

		if state == None:
			# Create new population
			self.population = self.reproduction.create_new_population(self.size)
			self.species.speciate(self.population,0)
		else:
			# Assign values from state
			self.population, self.reproduction = state
			
	def run_without_speciation(self, fitness_function, generations=None):
		current_gen = 0
		goal = 0.97
		reached_goal = False
		# Plot data
		best_y = []
		# Iterate for a number of generations or infinitely
		while current_gen < generations and not reached_goal:
			# Average fitness
			avg_fitness = 0
			# Assess fitness of current population
			fitness_function(list(iteritems(self.population)))
			# Find best genome in current generation and update avg fitness
			curr_best = None
			for genome in itervalues(self.population):
				avg_fitness += genome.fitness
				if curr_best is None or genome.fitness > curr_best.fitness:
					curr_best = genome
			# Update global best genome if possible
			if self.best_genome is None or curr_best.fitness > self.best_genome.fitness:
				self.best_genome = curr_best
			best_y.append(self.best_genome.fitness)
			# Reached fitness goal, we can stop
			if self.best_genome.fitness > goal:
				reached_goal = True

			# Return new population and continue to next generation
			print("\nCurrent Generation: {}".format(current_gen))
			print("Current Best Fitness: {}".format(self.best_genome.fitness))
			print("From Genome {}".format(self.best_genome.key))
			print("Average Fitness: {}".format(avg_fitness/self.size))
			for node in self.best_genome.nodes.values():
				print("Node {0} of type {1}".format(node.key, node.activation))
			for conn in self.best_genome.connections.values():
				print("Conn {0} of weight {1}".format(conn.key, conn.weight))

			# Order population by descending fitness
			pop_by_fitness = list(iteritems(self.population))
			pop_by_fitness.sort(reverse=True,key=lambda x: x[1].fitness)
			# Create new population
			new_population = {}
			new_pop_to_add = {}
			# Preserve elites of current population
			for gid, genome in pop_by_fitness[:self.elitism]:
				new_population[gid] = genome
			new_population_keys = list(iterkeys(new_population))
			print(new_population_keys)
			# Fill in rest of new population with mutants
			for _ in range(self.size - self.elitism):
				# Randomly choose elite to mutate
				idx = np.random.choice(new_population.keys())
				mutant_key = next(self.reproduction.genome_indexer)
				mutant = Genome(mutant_key)
				mutant.copy(new_population[idx])
				# print("Same?: {}".format(new_population[idx] is mutant))
				mutant.mutate()
				new_pop_to_add[mutant_key] = mutant
			new_population.update(new_pop_to_add)
			self.population = new_population
			current_gen += 1

		return self.best_genome
		
	def run_without_speciation_with_stag(self, fitness_function, generations=None):
		current_gen = 0
		goal = 0.97
		reached_goal = False
		stagnation = 20
		# Plot data
		best_y = []
		# Iterate for a number of generations or infinitely
		while current_gen < generations and not reached_goal:
			# Average fitness
			avg_fitness = 0
			# Assess fitness of current population
			fitness_function(list(iteritems(self.population)))
			# Find best genome in current generation and update avg fitness
			curr_best = None
			for genome in itervalues(self.population):
				avg_fitness += genome.fitness
				if curr_best is None or genome.fitness > curr_best.fitness:
					curr_best = genome
			# Update global best genome if possible
			if self.best_genome is None or curr_best.fitness > self.best_genome.fitness:
				self.best_genome = curr_best
			best_y.append(self.best_genome.fitness)
			# Reached fitness goal, we can stop
			if self.best_genome.fitness > goal:
				reached_goal = True
			# Order population by descending fitness
			pop_by_fitness = list(iteritems(self.population))
			pop_by_fitness.sort(reverse=True,key=lambda x: x[1].fitness)
			# Create new population
			new_population = {}
			
			if self.last_best > stagnation:
				self.population = self.reproduction.create_new_population(self.size)
				print("\nStagnated, replacing population")
				self.last_best = 0
				self.best_genome = None
				# Return new population and continue to next generation
				print("Current Generation: {}".format(current_gen))
				print("Average Fitness: {}".format(avg_fitness/self.size))
			else:
				# Preserve elites of current population
				for gid, genome in pop_by_fitness[:self.elitism]:
					new_population[gid] = genome
				new_population_keys = list(iterkeys(new_population))
				# Fill in rest of new population with mutants
				for _ in range(self.size - self.elitism):
					# Randomly choose elite to mutate
					idx = np.random.choice(new_population.keys())
					mutant_key = next(self.reproduction.genome_indexer)
					mutant = Genome(mutant_key)
					mutant.copy(new_population[idx])
					mutant.mutate()
					new_population[mutant_key] = mutant
				self.population = new_population
				# Return new population and continue to next generation
				print("\nCurrent Generation: {}".format(current_gen))
				print("Current Best Fitness: {}".format(self.best_genome.fitness))
				print("From Genome {}".format(self.best_genome.key))
				print("Average Fitness: {}".format(avg_fitness/self.size))
				for node in self.best_genome.nodes.values():
					print("Node {0} of type {1}".format(node.key, node.activation))
				for conn in self.best_genome.connections.values():
					print("Conn {0} of weight {1}".format(conn.key, conn.weight))
			
			current_gen += 1
			self.last_best += 1
		
		if reached_goal:
			best_x = range(current_gen)
			plt.plot(best_x, best_y)
			plt.yticks([y/10.0 for y in range(11)])
			plt.ylabel("Fitness")
			plt.xlabel("Generation")
			plt.show()
		return self.best_genome

	def run_and_complexify(self, fitness_function, generations=None):
		current_gen = 0
		goal = 0.97
		reached_goal = False
		# Plot data
		best_y = []
		max_complexity_y = []
		min_complexity_y = []
		avg_complexity_y = []
		# Iterate for a number of generations or infinitely
		while current_gen < generations:
			# Average fitness
			avg_fitness = 0
			avg_complexity = 0
			# Assess fitness of current population
			fitness_function(list(iteritems(self.population)))
			# Find best genome in current generation and update avg fitness
			curr_best = None
			# Find most and least complex genomes in current generation
			# and update avg complexity
			curr_max_complex = None
			curr_min_complex = None
			for genome in itervalues(self.population):
				avg_fitness += genome.fitness
				avg_complexity += genome.complexity()
				
				if curr_best is None or genome.fitness > curr_best.fitness:
					curr_best = genome
				
				if curr_max_complex is None or genome.complexity() > curr_max_complex.complexity():
					curr_max_complex = genome
				
				if curr_min_complex is None or genome.complexity() < curr_min_complex.complexity():
					curr_min_complex = genome
			
			# Update global best genome if possible
			if self.best_genome is None or curr_best.fitness > self.best_genome.fitness:
				self.best_genome = curr_best
			
			# Update global maximum and minimum complexity genomes
			if self.max_complex_genome is None or genome.complexity() > self.max_complex_genome.complexity():
				self.max_complex_genome = genome
			if self.min_complex_genome is None or genome.complexity() < self.min_complex_genome.complexity():
				self.min_complex_genome = genome
			
			best_y.append(self.best_genome.fitness)
			max_complexity_y.append(self.max_complex_genome.complexity())
			min_complexity_y.append(self.min_complex_genome.complexity())
			avg_complexity_y.append((avg_complexity+0.0)/self.size)
			# Reached fitness goal, we can stop
			if self.best_genome.fitness > goal:
				reached_goal = True

			# Return new population and continue to next generation
			print("\nCurrent Generation: {}".format(current_gen))
			print("Current Best Fitness: {}".format(self.best_genome.fitness))
			print("Current Best Complexity: {}".format(self.best_genome.complexity()))
			print("Current Max Complexity: {}".format(self.max_complex_genome.complexity()))
			print("Current Min Complexity: {}".format(self.min_complex_genome.complexity()))
			print("From Genome {}".format(self.best_genome.key))
			print("Average Fitness: {}".format(avg_fitness/self.size))
			print("Average Complexity: {}".format(avg_complexity/self.size))
			for node in self.best_genome.nodes.values():
				print("Node {0} of type {1}".format(node.key, node.activation))
			for conn in self.best_genome.connections.values():
				print("Conn {0} of weight {1}".format(conn.key, conn.weight))

			# Order population by descending fitness
			pop_by_fitness = list(iteritems(self.population))
			pop_by_fitness.sort(reverse=True,key=lambda x: x[1].fitness)
			# Create new population
			new_population = {}
			new_pop_to_add = {}
			population_set = {}
			# Preserve elites of current population
			for gid, genome in pop_by_fitness[:50]:
				new_population[gid] = genome

			# for gid, genome in pop_by_fitness[2:]:
			# 	if genome.fitness == self.best_genome.fitness:
			# 		new_population[gid] = genome

			new_population_keys = list(iterkeys(new_population))
			print(new_population_keys)
			# Fill in rest of new population with mutants
			print(len(new_population))
			for _ in range(self.size - len(new_population)):
				# Randomly choose elite to mutate
				idx = np.random.choice(new_population.keys())
				mutant_key = next(self.reproduction.genome_indexer)
				mutant = Genome(mutant_key)
				mutant.copy(new_population[idx])
				# print("Same?: {}".format(new_population[idx] is mutant))
				mutant.mutate()
				new_pop_to_add[mutant_key] = mutant
			new_population.update(new_pop_to_add)
			self.population = new_population
			current_gen += 1
		best_x = range(current_gen)
		plt.plot(best_x, best_y, best_x, max_complexity_y, best_x, min_complexity_y,best_x, avg_complexity_y)
		plt.ylabel("Fitness")
		plt.xlabel("Generation")
		plt.legend(['fitness','max_comp', 'min_comp', 'avg_comp'])
		plt.show()
		return self.best_genome

	def run_with_speciation(self,fitness_function, generations=None):
		self.current_gen = 0
		goal = 0.97
		reached_goal = False

		while self.current_gen < generations and not reached_goal:
			# Assess fitness of current population
			fitness_function(list(iteritems(self.population)))
			# Find best genome in current generation and update avg fitness
			curr_best = None
			for genome in itervalues(self.population):
				if curr_best is None or genome.fitness > curr_best.fitness:
					curr_best = genome
			# Update global best genome if possible
			if self.best_genome is None or curr_best.fitness > self.best_genome.fitness:
				self.best_genome = curr_best
			# Reached fitness goal, we can stop
			if self.best_genome.fitness > goal:
				reached_goal = True
			report_fitness(self)
			report_species(self.species)
			# Create new unspeciated popuation based on current population's fitness
			self.population = self.reproduction.reproduce_with_species(self.species,
																	   self.size, 
																	   self.current_gen)
			# Check for species extinction (species did not perform well)
			if not self.species.species:
				raise ValueError("Species went extinct")
		
			# Speciate new population
			self.species.speciate(self.population, self.current_gen)

			self.current_gen += 1

		return self.best_genome