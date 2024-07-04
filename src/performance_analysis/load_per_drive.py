import matplotlib.pyplot as plt
import numpy as np


def process_dispatched_trucks(instance_nr, simu_run):
  """
  Processes dispatched truck data and calculates relevant statistics.

  Args:
    instance_nr: Instance number for simulation run.
    simu_run: Simulation run number.
    output_file: Path to the output file for writing results.
    output_fig: Path to the output figure file (optional).
  """
  output_fig = f"./generated_files/{instance_nr}_{simu_run}_truck_loads_plot.png"
  output_file = f"./generated_files/{instance_nr}_{simu_run}_processed_data.txt"
  input_filename = f"./generated_files/{instance_nr}_{simu_run}_dispatched_truck_status.txt"

  with open(input_filename, "r") as file:
    data = file.read()
  lines = data.strip().split('\n')[1:]

  # Initialize variables
  truck_loads = []
  truck_ids = []
  current_truck_id = current_time_step = None
  current_volume_sum = 0
  truck_capacity = 32                                                   # max capacity of all trucks, always is 32
  total_empty_runs = num_truck_drives = avg_empty_runs = 0
  max_total_load = percentages = average_percentage = drive_ids = 0

  # Process each line
  for line in lines:
    parts = line.split()
    curr_time_step = int(parts[0])
    truck_id = int(parts[1])

    # Ignore rows with origin equal to destination
    if int(parts[2]) != int(parts[3]):
      volume = int(parts[-1])                                           # Access the last integer as volume

      # Update volume and truck information
      if (current_truck_id != truck_id and curr_time_step == current_time_step) or curr_time_step != current_time_step:
        if current_truck_id is not None:
          truck_loads.append(current_volume_sum)
          truck_ids.append(current_truck_id)
        current_truck_id = truck_id
        current_volume_sum = volume
        current_time_step = curr_time_step
      else:
        current_volume_sum += volume

  # Append the volume sum for the last truck_id
  if current_truck_id is not None:
    truck_loads.append(current_volume_sum)
    truck_ids.append(current_truck_id)

  # Calculate remaining statistics
  empty_runs = [truck_capacity - load for load in truck_loads]
  total_empty_runs = sum(empty_runs)
  num_truck_drives = len(truck_loads)
  avg_empty_runs = total_empty_runs / num_truck_drives

  # Calculate maximum total load, percentages, and average percentage
  max_total_load = max(truck_loads)
  percentages = [load / max_total_load * 100 for load in truck_loads]
  average_percentage = np.mean(percentages)
  drive_ids = range(1, len(truck_loads) + 1)

  # Write data to output file
  with open(output_file, 'w') as file:
    file.write(f"Number of truck drives: {num_truck_drives}\n")
    file.write(f"Average empty runs per truck load: {avg_empty_runs:.10f}\n")
    file.write(f"Maximum total load: {max_total_load}\n")
    file.write(f"Load per drive: {[load for load in truck_loads]}\n")
    file.write(f"Average load percentage: {average_percentage:.10f}%\n")

  # Plot data and save figure (optional)
  if output_fig:
    plt.figure(figsize=(8, 6))
    plt.bar(drive_ids, percentages, color='skyblue')
    plt.title('Total Load per Truck Drive [%]')
    plt.xlabel('Drive ID')
    plt.ylabel('Total Load [%]')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(drive_ids)  

    # Plot the average line
    plt.axhline(y=average_percentage, color='red', linestyle='-', label=f'Average Load: {average_percentage:.2f}%')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_fig)
    plt.close("all")

# Example of usage
# process_dispatched_trucks(instance_nr = 11, simu_run = 1)
