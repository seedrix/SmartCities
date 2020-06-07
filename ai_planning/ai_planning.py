import subprocess

class Solver():
    def __init__(self, path_to_ff):
        """susceptible to injection attacks if path_to_ff can be specified by an attacker"""
        self.solver_path = path_to_ff

    def solve(self, domain_file="domain.pddl", problem_file="problem.pddl"):
        output = subprocess.run([self.solver_path, "-o", domain_file, "-f", problem_file], capture_output=True)

        if output.returncode == 1:
            stderr = output.stderr.decode("utf-8")
            print("Error at parsing pddl files: ")
            print(stderr)
            
        else: 
            stdout = output.stdout.decode("utf-8")
            print(stdout)

if __name__ == "__main__":
    solver = Solver("../../Metric-FF/ff")
    solver.solve()
