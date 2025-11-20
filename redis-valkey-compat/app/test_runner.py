# app/test_runner.py

"""
Redis vs. Valkey Compatibility Test Runner

This script automates the process of testing compatibility between a Redis
and a Valkey instance.

It works as follows:
1.  Imports connection configurations from `config.py`.
2.  Dynamically discovers all test scenarios in the `scenarios/` directory.
3.  For each target (Redis, Valkey):
    a. Establishes a connection.
    b. Executes every discovered test scenario.
    c. Collects the results.
4.  Compares the results from both targets.
5.  Prints a summary table to the console using `rich`.
6.  Saves the detailed results to JSON files for further analysis.
"""

import os
import importlib
import json
import redis
from rich.console import Console
from rich.table import Table

# --- Configuration ---
from config import TARGETS

# --- Main Application Logic ---

def discover_scenarios():
    """
    Finds all runnable test scenarios in the 'scenarios' directory.
    A scenario is any Python file with a `run(client)` function.
    """
    scenarios = []
    scenario_dir = os.path.join(os.path.dirname(__file__), 'scenarios')
    for filename in os.listdir(scenario_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = f"scenarios.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, 'run') and callable(module.run):
                    scenarios.append(module)
            except ImportError as e:
                print(f"Error importing scenario {module_name}: {e}")
    return scenarios

def run_tests_for_target(target_name, conn_params, scenarios):
    """
    Connects to a target and runs all test scenarios against it.
    """
    results = []
    print(f"--- Running tests for {target_name} ---")
    try:
        client = redis.Redis(decode_responses=False, **conn_params)
        client.ping()
        client.flushdb() # Clear the database before running tests
        print(f"Connection to {target_name} successful. Database flushed.")
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to {target_name}: {e}")
        # Report failure for all scenarios if connection fails
        for scenario in scenarios:
            scenario_name = scenario.__name__.split('.')[-1]
            results.append({
                "scenario_name": scenario_name,
                "status": "ERROR",
                "detail": f"Connection to {target_name} failed."
            })
        return results

    for scenario in scenarios:
        scenario_name = scenario.__name__.split('.')[-1]
        print(f"  Executing scenario: {scenario_name}...")
        result = scenario.run(client)
        results.append(result)
    
    client.close()
    return results

def compare_results(results_a, results_b, name_a, name_b):
    """
    Compares two sets of results and identifies differences.
    """
    diffs = []
    results_b_map = {res['scenario_name']: res for res in results_b}

    for res_a in results_a:
        s_name = res_a['scenario_name']
        if s_name in results_b_map:
            res_b = results_b_map[s_name]
            if res_a['status'] != res_b['status'] or res_a['detail'] != res_b['detail']:
                diffs.append({
                    "scenario_name": s_name,
                    f"{name_a}_status": res_a['status'],
                    f"{name_b}_status": res_b['status'],
                    f"{name_a}_detail": res_a['detail'],
                    f"{name_b}_detail": res_b['detail'],
                })
    return diffs

def main():
    """
    Main function to orchestrate the test execution and reporting.
    """
    console = Console()
    scenarios = discover_scenarios()
    
    if not scenarios:
        console.print("[bold red]No test scenarios found in 'scenarios/' directory.[/bold red]")
        return

    all_results = {}
    for target_name, conn_params in TARGETS.items():
        results = run_tests_for_target(target_name, conn_params, scenarios)
        all_results[target_name] = results
        
        # Save individual results to JSON
        output_filename = f"results_{target_name}.json"
        with open(output_filename, 'w') as f:
            json.dump(results, f, indent=2)
        console.print(f"Results for {target_name} saved to [cyan]{output_filename}[/cyan]")

    # --- Display Results in a Table ---
    table = Table(title="Redis vs. Valkey Compatibility Test Results")
    table.add_column("Scenario", justify="left", style="cyan", no_wrap=True)
    table.add_column("Target", justify="left", style="magenta")
    table.add_column("Status", justify="center")
    table.add_column("Detail", justify="left", style="green")

    for target_name, results in all_results.items():
        for result in results:
            status_style = "green"
            if result['status'] == 'FAIL':
                status_style = "red"
            elif result['status'] == 'WARN':
                status_style = "yellow"
            elif result['status'] == 'ERROR':
                status_style = "bold red"
            
            table.add_row(
                result['scenario_name'],
                target_name,
                f"[{status_style}]{result['status']}[/{status_style}]",
                result['detail']
            )

    console.print(table)

    # --- Compare and Highlight Differences ---
    target_names = list(TARGETS.keys())
    if len(target_names) == 2:
        name_a, name_b = target_names[0], target_names[1]
        diffs = compare_results(all_results[name_a], all_results[name_b], name_a, name_b)
        
        if diffs:
            diff_table = Table(title=f"Result Differences ({name_a} vs. {name_b})")
            diff_table.add_column("Scenario", style="cyan")
            diff_table.add_column(f"{name_a} Status", style="yellow")
            diff_table.add_column(f"{name_b} Status", style="yellow")
            diff_table.add_column("Details", style="red")

            for diff in diffs:
                details = f"[{name_a}] {diff[f'{name_a}_detail']}\n[{name_b}] {diff[f'{name_b}_detail']}"
                diff_table.add_row(
                    diff['scenario_name'],
                    diff[f'{name_a}_status'],
                    diff[f'{name_b}_status'],
                    details
                )
            console.print(diff_table)
        else:
            console.print("\n[bold green]✅ No functional differences detected between targets.[/bold green]")


if __name__ == "__main__":
    main()
