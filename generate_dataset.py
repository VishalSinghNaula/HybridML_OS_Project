import csv
import random
from datetime import datetime, timedelta

def generate_label(cpu, wait, conflict, priority, deadline):
    # Get simulated system state (20-100%)
    system_load = random.randint(20, 100)
    
    # Rule 1: Immediate rejects
    if system_load > 90 and cpu > 15:
        return 0
    if conflict > 3 and random.random() < 0.7:  # 70% reject if many conflicts
        return 0
        
    # Rule 2: Immediate accepts
    if deadline < 2:  # Urgent deadline
        return 1
    if priority == 5 and system_load < 80:
        return 1
        
    # Scoring system
    score = 0
    score += priority * 2
    score += min(wait, 10)
    score -= cpu / 10
    score -= conflict * 2
    score -= 5 if system_load > 70 else 0
    
    # Dynamic threshold
    threshold = 15 + (system_load / 10)
    return 1 if score >= threshold else 0

def generate_data(num_samples=1000, filename="thread_data.csv"):
    with open(filename, mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["cpu", "wait", "conflict", "priority", "deadline", "label"])
        
        for _ in range(num_samples):
            cpu = random.randint(0, 100)
            wait = random.randint(0, 15)
            conflict = random.randint(0, 5)
            priority = random.randint(0, 5)
            deadline = random.randint(0, 10)  # 0-10 urgency scale
            
            label = generate_label(cpu, wait, conflict, priority, deadline)
            writer.writerow([cpu, wait, conflict, priority, deadline, label])

if __name__ == "__main__":
    generate_data()