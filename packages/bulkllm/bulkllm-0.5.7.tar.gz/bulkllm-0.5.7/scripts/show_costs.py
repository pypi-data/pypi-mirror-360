from datetime import UTC, datetime

import litellm

from bulkllm.model_registration.main import register_models


def calculate_costs_for_all_models(input_tokens=1612249, completion_tokens=1464563, output_csv=None):
    """
    Calculate costs for specified token amounts across all litellm models.

    Args:
        input_tokens (int): Number of input tokens to calculate cost for (default: 1,612,249)
        completion_tokens (int): Number of completion tokens to calculate cost for (default: 1,464,563)
        output_csv (str): Path to save the CSV output (default: None, which prints to console)

    Returns:
        dict: Dictionary mapping model names to calculated costs
    """
    import csv

    register_models()

    costs = {}

    # Calculate costs for each model
    for model_name, model_info in litellm.model_cost.items():
        input_cost = 0
        output_cost = 0

        # Get input cost if available
        if "input_cost_per_token" in model_info and model_info["input_cost_per_token"] is not None:
            input_cost = model_info["input_cost_per_token"] * input_tokens

        # Get output cost if available
        if "output_cost_per_token" in model_info and model_info["output_cost_per_token"] is not None:
            output_cost = model_info["output_cost_per_token"] * completion_tokens

        total_cost = input_cost + output_cost
        costs[model_name] = {"input_cost": input_cost, "output_cost": output_cost, "total_cost": total_cost}

    # Sort models by total cost
    sorted_costs = dict(sorted(costs.items(), key=lambda item: item[1]["total_cost"], reverse=True))

    # Generate default CSV filename if output_csv is None
    if output_csv is True or output_csv == "":
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        output_csv = f"model_costs_{timestamp}.csv"

    # Write results to CSV if output_csv is specified
    if output_csv:
        with open(output_csv, "w", newline="") as csvfile:
            fieldnames = ["model_name", "input_tokens", "completion_tokens", "input_cost", "output_cost", "total_cost"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for model_name, cost_info in sorted_costs.items():
                writer.writerow(
                    {
                        "model_name": model_name,
                        "input_tokens": input_tokens,
                        "completion_tokens": completion_tokens,
                        "input_cost": cost_info["input_cost"],
                        "output_cost": cost_info["output_cost"],
                        "total_cost": cost_info["total_cost"],
                    }
                )

            print(f"Cost data written to {output_csv}")
    else:
        # Print to console if no CSV output is specified
        for model_name, cost_info in sorted_costs.items():
            print(f"{model_name}: Total Cost = ${cost_info['total_cost']:.2f}")

    return sorted_costs
