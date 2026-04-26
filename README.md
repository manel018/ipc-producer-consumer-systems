# IPC Producer-Consumer Systems

Project exploring Interprocess Communication (IPC) mechanisms and synchronization techniques through two producer-consumer implementations:

1. **Pipes-based Producer-Consumer**: Inter-process communication using anonymous pipes
2. **Semaphore-based Producer-Consumer**: Multithreaded implementation with shared memory


## Repository Structure

```
├── .gitignore   
├── Makefile                       # Build and run scripts    
├── README.md                      # This file
├── analysis/                      # Folder created when running Part 2 experiments
│   └── part2/
│       ├── data/
│       │   ├── execution_times.csv   # Execution times for all combinations
│       │   └── occupancy_*.txt       # Buffer occupancy traces
│       └── plots/                    # Generated graphs                  
├── part1.c                        # Pipes implementation
├── part2-analysis.py              # Script for generating plots from Part 2 data
├── part2.c                        # Semaphores implementation
└── requirements.txt               # Dependencies for the project
```

## Building

```bash
make              # Build all programs
```

## Running
Run part 1 with a specified number of integers as an argument:

```bash
./part1 <number_of_integers>    # Run Part 1

# or using Makefile with an environment variable

make run-part1 NUM=1000          # Run Part 1 with 1000 integers
```

Run part 2 to execute all experiments and generate data:

```bash
./part2                     # Run Part 2 experiments

# or using Makefile

make run-part2              # Run Part 2 experiments
```

This will execute all combinations of producer/consumer threads and buffer sizes, writing the results to `analysis/part2/data/`.

Then, generate plots from the Part 2 data:

```bash
make analyze      # Generate plots from Part 2 data in 'analysis/part2/plots/'
```

🔎  Open the generated plots in **`analysis/part2/plots/`** and analyze the results.

Finally, you can clean up compiled binaries and analysis data/plots:

```bash
make clean        # Remove only compiled binaries
make clean-all    # Remove binaries and all analysis data and plots
```


## Part 1: Pipes-based Producer-Consumer

### Overview

A two-process implementation where a producer and consumer communicate through anonymous pipes. The producer generates integer sequences that the consumer validates for primality.

This program receives a command-line argument specifying how many integers to produce/consume, allowing for flexible testing

### Key Implementation Details

- Both processes (parent and child) access both ends of the pipe after `fork()`
- **Critical**: Numbers are converted to fixed-size strings (20 bytes) before writing to the pipe
- Fixed-size I/O prevents message fragmentation and ensures reliable communication


## Part 2: Semaphore-based Producer-Consumer

### Overview

A multithreaded implementation using shared memory and semaphores for synchronization between multiple producer and consumer threads.

This program consists of two parts: the main logic in `part2.c` and the analysis/plotting in `part2-analysis.py`. The main program runs experiments with various configurations of producers, consumers, and buffer sizes, while the analysis script generates visualizations from the collected data.

### Architecture

- **Shared Memory**: Vector of N integer slots
- **Producers** ($Np$ threads): Generate random integers (1 to $10^7$) and write to empty slots
- **Consumers** ($Nc$ threads): Read integers from filled slots and check primality

### Synchronization

- **Mutex Semaphore**: Protects shared memory access (prevents race conditions)
- **Counter Semaphores**: Coordinate full/empty buffer conditions
  - Producers wait when buffer is full
  - Consumers wait when buffer is empty

### Study Case Parameters

**Target**: Process $M = 10^5$ numbers before termination

**Buffer sizes**: $N \in \{1, 10, 100, 1000\}$

**Thread combinations**: $(Np, Nc) \in \{(1,1), (1,2), (1,4), (1,8), (2,1), (4,1), (8,1)\}$

### Analysis and Plots

- **Execution Time**: Total time to process $M$ numbers for each configuration
- **Buffer Occupancy**: Time series of buffer occupancy during execution
- **Heatmaps**: Average buffer occupancy across configurations for each $N$

