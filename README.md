# IPC Producer-Consumer Systems

A distributed systems course project exploring Interprocess Communication (IPC) mechanisms through two producer-consumer implementations.

## Project Overview

This project implements producer-consumer patterns using different IPC mechanisms and synchronization techniques:

1. **Pipes-based Producer-Consumer**: Inter-process communication using anonymous pipes
2. **Semaphore-based Producer-Consumer**: Multithreaded implementation with shared memory


## Part 1: Pipes-based Producer-Consumer

### Overview

A two-process implementation where a producer and consumer communicate through anonymous pipes. The producer generates integer sequences that the consumer validates for primality.

### Producer Behavior

Generates growing sequences of random integers according to:

$$N_i = N_{i-1} + \Delta,\; N_0 = 1,\; \Delta \in [1,100]$$

Where:
- $N_0 = 1$ (initial value)
- $\Delta$ is a random integer between 1 and 100 (inclusive)
- The producer generates a configurable number of integers

### Consumer Behavior

- Receives integers from the producer via pipe
- Checks if each integer is a prime number
- Prints results to the terminal
- Terminates upon receiving 0

### Implementation Notes

- Both processes (parent and child) access both ends of the pipe after `fork()`
- **Critical**: Numbers are converted to fixed-size strings (20 bytes) before writing to the pipe
- Fixed-size I/O prevents message fragmentation and ensures reliable communication

### Usage

```bash
./producer-consumer <number_of_integers>
```

Example:
```bash
./producer-consumer 1000
```

## Part 2: Semaphore-based Producer-Consumer

### Overview

A multithreaded implementation using shared memory and semaphores for synchronization between multiple producer and consumer threads.

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

### Usage

```bash
./producer-consumer-semaphore <buffer_size> <num_producers> <num_consumers> <total_numbers>
```

Example:
```bash
./producer-consumer-semaphore 100 2 4 100000
```

## Repository Structure

```
├── README.md                      # This file
├── project-description.md         # Original project specification
├── part1/
│   ├── producer.c                 # Part 1 producer implementation
│   └── consumer.c                 # Part 1 consumer implementation
├── part2/
│   ├── producer_consumer.c        # Part 2 implementation
│   └── analysis/
│       ├── performance_times.csv   # Execution times for all combinations
│       ├── graphs/                 # Generated graphs
│       └── report/                 # Final report
└── Makefile
```

## Building

```bash
make              # Build all programs
make clean        # Remove compiled binaries
make run-part1    # Run Part 1 tests
make run-part2    # Run Part 2 experiments
```

## Key Concepts

- **IPC**: Inter-process communication mechanisms
- **Pipes**: Unnamed pipes for process communication
- **Semaphores**: Synchronization primitives for thread coordination
- **Race Conditions**: Concurrent access issues and mitigation strategies
- **Producer-Consumer Pattern**: Classic synchronization problem
- **Primality Testing**: Algorithmic verification of prime numbers

## Notes

- Part 1 focuses on process-based IPC with pipes
- Part 2 emphasizes thread synchronization and shared memory coordination
- Both parts include primality checking as the computational workload
- Proper handling of fixed-size messages is critical in Part 1

---

**Status**: In development  
**Last Updated**: April 2026
