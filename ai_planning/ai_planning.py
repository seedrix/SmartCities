import subprocess

class Solver():
    def __init__(self, path_to_ff: str):
        """susceptible to injection attacks if path_to_ff can be specified by an attacker"""
        self.solver_path = path_to_ff

    def _solve(self, domain_file="domain.pddl", problem_file="problem.pddl"):
        output = subprocess.run([self.solver_path, "-o", domain_file, "-f", problem_file], capture_output=True)

        if output.returncode == 1:
            stderr = output.stderr.decode("utf-8")
            print("Error at parsing pddl files: ")
            print(stderr)
            print(output.stdout.decode("utf-8"))
            
        else: 
            stdout = output.stdout.decode("utf-8")
            print(stdout)

    def solve_problem(self, planning_instance):
        with open('problem_created.pddl', 'w') as f:
            f.write(planning_instance.to_problem_string())
        self._solve(problem_file="problem_created.pddl")



class PlanningInstance():
    def __init__(self, name, number_of_shops, number_of_lists, people_at_shop: [int], shop_options: [(int, int)]):
        self.number_of_shops = number_of_shops
        self.number_of_lists = number_of_lists
        self.name = name
        self.people_at_shop = people_at_shop
        self.shop_options = shop_options
        if len(people_at_shop) != number_of_shops:
            print("number of shops and len(people at shop) must be equal")
            return

    def to_problem_string(self) -> str:
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
        problem += """(:goal            
        (and (forall (?l - list)
            (list-set ?l)
        )
        (forall (?s - shop)
            (<= (people-at-shop ?s) """ + str(average) + """)
        )
                    
        )
    )
)
        """
        return problem

    def _compute_average(self) -> int:
        average = (sum(self.people_at_shop) + self.number_of_lists / self.number_of_shops) + 1
        print(average)
        return average


            
    
    


if __name__ == "__main__":
    solver = Solver("../../Metric-FF/ff")
    number_of_shops = 3
    number_of_lists = 5
    people_at_shop = [0 for i in range(number_of_shops)]
    shop_options = []
    for i in range(number_of_lists):
        shop_options.append((i, 0))
        shop_options.append((i, 1))
        shop_options.append((i, 2))
    planning_instance = PlanningInstance("week2", number_of_shops, number_of_lists, people_at_shop, shop_options)
    solver.solve_problem(planning_instance)
