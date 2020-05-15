#coding: utf-8
import math
import random
import argparse
from functools import partial
from time import time
from tqdm import tqdm
 
ALPHA = 0.85

def annealing_algorithm(number, capacity, weight_cost, init_temp=100, steps=100):
    start_sol = init_solution(weight_cost, capacity)
    best_cost, solution = simulate(start_sol, weight_cost, capacity, init_temp, steps)
    best_combination = [0] * number
    for idx in solution:
        best_combination[idx] = 1
    return best_cost, best_combination


def init_solution(weight_cost, max_weight):
    solution = []
    allowed_positions = list(range(len(weight_cost)))
    while len(allowed_positions) > 0:
        idx = random.randint(0, len(allowed_positions) - 1)
        selected_position = allowed_positions.pop(idx)
        if get_cost_and_weight_of_knapsack(solution + [selected_position], weight_cost)[1] <= max_weight:
            solution.append(selected_position)
        else:
            break
    return solution


def get_cost_and_weight_of_knapsack(solution, weight_cost):
    cost, weight = 0, 0
    for item in solution:
        weight += weight_cost[item][0]
        cost += weight_cost[item][1]
    return cost, weight


def moveto(solution, weight_cost, max_weight):
    moves = []
    for idx, _ in enumerate(weight_cost):
        if idx not in solution:
            move = solution[:]
            move.append(idx)
            if get_cost_and_weight_of_knapsack(move, weight_cost)[1] <= max_weight:
                moves.append(move)
    for idx, _ in enumerate(solution):
        move = solution[:]
        del move[idx]
        if move not in moves:
            moves.append(move)
    return moves


def simulate(solution, weight_cost, max_weight, init_temp, steps):
    temperature = init_temp
    best = solution
    best_cost = get_cost_and_weight_of_knapsack(solution, weight_cost)[0]

    current_sol = solution
    while True:
        current_cost = get_cost_and_weight_of_knapsack(best, weight_cost)[0]
        for i in range(0, steps):
            moves = moveto(current_sol, weight_cost, max_weight)
            idx = random.randint(0, len(moves) - 1)
            random_move = moves[idx]
            delta = get_cost_and_weight_of_knapsack(random_move, weight_cost)[0] - best_cost
            if delta > 0:
                best = random_move
                best_cost = get_cost_and_weight_of_knapsack(best, weight_cost)[0]
                current_sol = random_move
            else:
                if math.exp(delta / float(temperature)) > random.random():
                    current_sol = random_move

        temperature *= ALPHA
        if current_cost >= best_cost or temperature <= 0:
            break
    return best_cost, best

def parse_line(line):
    parts = [int(value) for value in line.split()]
    inst_id, number, capacity = parts[0:3]
    weight_cost = [(parts[i], parts[i + 1]) for i in range(3, len(parts), 2)]
    return inst_id, number, capacity, weight_cost

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script solving the 0/1 knapsack problem')
    parser.add_argument('-f', '--inst-file', required=True, type=str, dest="inst_file_path", 
                        help='Path to inst *.dat file')
    parser.add_argument('-o', type=str, dest="solution_file_path", default="output.sol.dat",
                        help='Path to file where solutions will be saved. Default value: output.sol.dat')
    parser.add_argument('-r', type=int, dest="repeat", default=1,
                        help='Number of repetitions. Default value: 1')
    parser.add_argument('-t', type=int, dest="temperature", default=100,
                        help='Initial temperature for annealing approach. Default value: 100')
    parser.add_argument('-n', type=int, dest="steps", default=100,
                        help='Number of steps for annealing approach iteration. Default value: 100')
    args = parser.parse_args()
    
    inst_file = open(args.inst_file_path, "r")
    sol_file = open(args.solution_file_path, "w")
    
    for line in tqdm(inst_file):
        inst_id, number, capacity, weight_cost = parse_line(line)
        # get best cost and variables combination
        best_cost, best_combination = annealing_algorithm(number, capacity, weight_cost,init_temp=args.temperature, steps=args.steps)
        best_combination_str = " ".join("%s" % i for i in best_combination)
        # write best result to file
        sol_file.write("%s %s %s  %s\n" % (inst_id, number, best_cost, best_combination_str))

    inst_file.close()
    sol_file.close()
    
