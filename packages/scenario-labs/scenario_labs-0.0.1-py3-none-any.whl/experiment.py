import argparse
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from xai_sdk import Client
from xai_sdk.chat import system

from agents.LLMAgent import LLMAgent
from simulations.prison import PrisonSimulation


def read_config(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Reads a YAML configuration file and returns its content as a dictionary.

    Args:
        file_path (Path): The path to the YAML configuration file.

    Returns:
        Optional[Dict[str, Any]]: Parsed configuration dictionary, or None if the file is missing or invalid.
    """
    if not file_path.exists():
        print(f"[Error] Configuration file '{file_path}' does not exist.")
        return None

    with file_path.open("r") as file:
        return yaml.safe_load(file)


def run_simulation(config_path: Path):
    """
    Runs the LLM-based Prison Simulation using the provided configuration file.

    Args:
        config_path (Path): Path to the simulation configuration YAML file.
    """
    api_key = os.getenv("XAI_API_KEY")
    client = Client(api_key=api_key)

    config = read_config(config_path)
    simulation_config = config["simulation_config"]

    agents = {}
    simulation_name = simulation_config["name"]
    max_turns = simulation_config["max_turns"]

    for agent in simulation_config.get("agents", []):
        if "id" not in agent or "role" not in agent:
            print("[Warning] Skipping agent with missing 'id' or 'role'.")
            continue

        initial_prompt = "\n".join(
            [simulation_config.get("system_prompt", ""), agent["initial_prompt"]]
        )
        session = client.chat.create(
            model="grok-3",
            messages=[system(initial_prompt)],
        )

        agents[agent["id"]] = LLMAgent(
            agent_id=agent["id"],
            role=agent["role"],
            initial_prompt=agent["initial_prompt"],
            session=session,
        )

        print(f"[Info] Agent created: {agent['id']} ({agent['role']})")

    simulation = PrisonSimulation(simulation_name, agents, max_turns=max_turns)
    simulation.run()


def main():
    parser = argparse.ArgumentParser(description="Run the LLM-based Prison Simulation.")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("starbound_config.yaml"),
        help="Path to the simulation configuration YAML file (default: starbound_config.yaml)",
    )
    args = parser.parse_args()
    run_simulation(args.config)


if __name__ == "__main__":
    main()
