#!/bin/bash

# Define the output file
OUTPUT_FILE="cpu_usage_log.txt"

# Get the current date and time
echo "==== CPU UTILIZATION REPORT: $(date) ====" > "$OUTPUT_FILE"

# Capture overall CPU utilization
echo "Overall CPU Utilization:" >> "$OUTPUT_FILE"
top -bn1 | grep "Cpu(s)" | awk '{print "CPU Load: " $2 + $4 "%"}' >> "$OUTPUT_FILE"

# Capture the top 5 CPU-consuming processes
echo -e "\nTop 5 Processes by CPU Usage:" >> "$OUTPUT_FILE"
ps -eo pid,ppid,cmd,%cpu --sort=-%cpu | head -n 6 >> "$OUTPUT_FILE"

# Confirm the script execution
echo "CPU usage and top 5 processes have been saved to $OUTPUT_FILE"
