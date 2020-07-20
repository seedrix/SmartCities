import subprocess
import math
import sys

assert sys.version_info >= (3, 7)

class Solver():
    def __init__(self, path_to_ff: str):
        """susceptible to injection attacks if path_to_ff can be specified by an attacker"""
        self.solver_path = path_to_ff

    def _call_solver(self, domain_file="domain.pddl", problem_file="problem.pddl"):
        output = subprocess.run([self.solver_path, "-o", domain_file, "-f", problem_file], capture_output=True)

        if output.returncode == 1:
            stderr = output.stderr.decode("utf-8")
            print("Error at parsing pddl files: ")
            print(stderr)
            print(output.stdout.decode("utf-8"))
            return None
            
        else: 
            stdout = output.stdout.decode("utf-8")

            if "first search space empty" in stdout:
                return None
            
            else:
                result = self._parse(stdout)
                return result

    def _parse(self, output):
        split = output.split("ff: found legal plan as follows")[1]
        split = split.split("time spent")[0]
        # remove empty lines
        text = "".join([s for s in split.splitlines(True) if s.strip("\n")])

        result = []
        for line in text.split("\n"):
            if "CHOOSE" in line:
                list_shop = line.split("CHOOSE")[1].strip()
                list_shop_array = list_shop.split(" ")
                result.append(list_shop_array)               
        return result

    def _solve_single_problem(self, problem_str):
        with open('problem_created.pddl', 'w') as f:
            f.write(problem_str)
        return self._call_solver(problem_file="problem_created.pddl")

    def solve(self, planning_instance):
        i = 0
        while True:
            result = self._solve_single_problem(planning_instance.to_problem_string(i))
            i += 1
            if result is not None:
                break
        return result



class PlanningInstance():
    def __init__(self, name, number_of_shops, number_of_lists, people_at_shop: [int], shop_options: [(int, int)], cap_at_shop: [int]):
        self.number_of_shops = number_of_shops
        self.number_of_lists = number_of_lists
        self.name = name
        self.people_at_shop = people_at_shop
        self.shop_options = shop_options
        self.cap_at_shop = cap_at_shop
        if len(people_at_shop) != number_of_shops:
            print("number of shops and len(people at shop) must be equal")
            return
        

    def to_problem_string(self, run_number = 0) -> str:
        problem = "(define (problem " + self.name + ")\n"
        problem += "(:domain Guidance)\n"
        problem += "(:objects "
        for i in range(self.number_of_shops):
            problem += "shop" + str(i) + " "
        problem += "- shop\n" 

        for i in range(self.number_of_lists):
            problem += "list" + str(i) + " "
        problem += "- list)\n" 
        problem += "(:init "
        
        for i, people in enumerate(self.people_at_shop):
            problem += "(= (people-at-shop shop" + str(i) + ") " + str(people) + ")\n"

        for (list_number, shop_number) in self.shop_options:
            problem += "(shop-option list" + str(list_number) + " shop" + str(shop_number) + ")\n"
        problem += ")\n"

        average = self._compute_average()
        current_cap = average + run_number

        problem += """(:goal            
        (and (forall (?l - list)
            (list-set ?l)
        )"""

        for (i, cap) in enumerate(self.cap_at_shop):
            problem += "(and (<= (people-at-shop shop" + str(i) + ") " + str(cap + run_number) + "))\n"

        # (forall (?s - shop)
        #     (<= (people-at-shop ?s) """ + str(current_cap) + """)
        # )

        problem += """
                    
        )
        )
        )
        """
        return problem

    def _compute_average(self) -> int:
        average = math.ceil(sum(self.people_at_shop) + self.number_of_lists / self.number_of_shops)
        return average


            
    
    


if __name__ == "__main__":
    solver = Solver("../../Metric-FF/ff")
    number_of_shops = 3
    number_of_lists = 5
    people_at_shop = [0 for i in range(number_of_shops)]
    people_at_shop[1] = 10
    cap_at_shop = [4,5,6]
    shop_options = []
    for i in range(number_of_lists):
        # shop_options.append((i, 0))
        shop_options.append((i, 1))
        shop_options.append((i, 2))
    planning_instance = PlanningInstance("week2", number_of_shops, number_of_lists, people_at_shop, shop_options, cap_at_shop)
    result = solver.solve(planning_instance)
    print(result)
