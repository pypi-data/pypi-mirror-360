#!/usr/bin/env python3
"""
Performance benchmark utility for HACS + LangGraph workflow.

This script provides comprehensive performance analysis of the clinical workflow,
including execution time, memory usage, and throughput metrics.
"""

import time
import statistics
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional psutil import for detailed memory monitoring
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  psutil not available - memory monitoring will be limited")
    print("   Install with: uv add psutil")

from graph import run_example


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""

    # Timing metrics (milliseconds)
    min_time_ms: float
    max_time_ms: float
    avg_time_ms: float
    median_time_ms: float
    p95_time_ms: float
    p99_time_ms: float

    # Memory metrics (MB)
    peak_memory_mb: float
    avg_memory_mb: float
    memory_increase_mb: float

    # Throughput metrics
    total_iterations: int
    success_rate: float
    throughput_per_second: float

    # Error tracking
    errors: List[str]


def get_memory_usage() -> float:
    """
    Get current memory usage in MB.

    Returns:
        Memory usage in MB, or 0 if unavailable
    """
    if HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB
    else:
        # Fallback - return 0 (memory monitoring disabled)
        return 0.0


def measure_single_execution() -> Dict[str, Any]:
    """
    Measure a single workflow execution.

    Returns:
        Dictionary with timing, memory, and success metrics
    """
    initial_memory = get_memory_usage()

    start_time = time.perf_counter()

    try:
        final_state = run_example()
        success = True
        error = None
    except Exception as e:
        success = False
        error = str(e)
        final_state = None

    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000

    peak_memory = get_memory_usage()
    memory_increase = peak_memory - initial_memory if HAS_PSUTIL else 0

    return {
        "execution_time_ms": execution_time_ms,
        "peak_memory_mb": peak_memory,
        "memory_increase_mb": memory_increase,
        "success": success,
        "error": error,
        "final_state": final_state,
    }


def benchmark_sequential(iterations: int = 100) -> BenchmarkResult:
    """
    Run sequential benchmark of the workflow.

    Args:
        iterations: Number of iterations to run

    Returns:
        BenchmarkResult with comprehensive metrics
    """
    print("🏃 Running sequential benchmark with {iterations} iterations...")

    results = []
    errors = []
    memory_measurements = []
    successful_runs = 0

    start_time = time.perf_counter()

    for i in range(iterations):
        if (i + 1) % 10 == 0:
            print("  Progress: {i + 1}/{iterations}")

        result = measure_single_execution()
        results.append(result["execution_time_ms"])
        memory_measurements.append(result["peak_memory_mb"])

        if result["success"]:
            successful_runs += 1
        else:
            errors.append(result["error"])

    total_time = time.perf_counter() - start_time

    # Calculate statistics
    execution_times = [r for r in results if r is not None]

    return BenchmarkResult(
        min_time_ms=min(execution_times) if execution_times else 0,
        max_time_ms=max(execution_times) if execution_times else 0,
        avg_time_ms=statistics.mean(execution_times) if execution_times else 0,
        median_time_ms=statistics.median(execution_times) if execution_times else 0,
        p95_time_ms=statistics.quantiles(execution_times, n=20)[18]
        if len(execution_times) >= 20
        else max(execution_times, default=0),
        p99_time_ms=statistics.quantiles(execution_times, n=100)[98]
        if len(execution_times) >= 100
        else max(execution_times, default=0),
        peak_memory_mb=max(memory_measurements) if memory_measurements else 0,
        avg_memory_mb=statistics.mean(memory_measurements)
        if memory_measurements
        else 0,
        memory_increase_mb=max(memory_measurements) - min(memory_measurements)
        if memory_measurements
        else 0,
        total_iterations=iterations,
        success_rate=successful_runs / iterations * 100,
        throughput_per_second=successful_runs / total_time,
        errors=errors,
    )


def benchmark_concurrent(iterations: int = 50, max_workers: int = 4) -> BenchmarkResult:
    """
    Run concurrent benchmark of the workflow.

    Args:
        iterations: Number of iterations to run
        max_workers: Maximum number of concurrent workers

    Returns:
        BenchmarkResult with comprehensive metrics
    """
    print(
        "🏃‍♂️ Running concurrent benchmark with {iterations} iterations, {max_workers} workers..."
    )

    results = []
    errors = []
    memory_measurements = []
    successful_runs = 0

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = [executor.submit(measure_single_execution) for _ in range(iterations)]

        # Collect results as they complete
        for i, future in enumerate(as_completed(futures)):
            if (i + 1) % 10 == 0:
                print("  Progress: {i + 1}/{iterations}")

            try:
                result = future.result()
                results.append(result["execution_time_ms"])
                memory_measurements.append(result["peak_memory_mb"])

                if result["success"]:
                    successful_runs += 1
                else:
                    errors.append(result["error"])
            except Exception as e:
                errors.append(str(e))

    total_time = time.perf_counter() - start_time

    # Calculate statistics
    execution_times = [r for r in results if r is not None]

    return BenchmarkResult(
        min_time_ms=min(execution_times) if execution_times else 0,
        max_time_ms=max(execution_times) if execution_times else 0,
        avg_time_ms=statistics.mean(execution_times) if execution_times else 0,
        median_time_ms=statistics.median(execution_times) if execution_times else 0,
        p95_time_ms=statistics.quantiles(execution_times, n=20)[18]
        if len(execution_times) >= 20
        else max(execution_times, default=0),
        p99_time_ms=statistics.quantiles(execution_times, n=100)[98]
        if len(execution_times) >= 100
        else max(execution_times, default=0),
        peak_memory_mb=max(memory_measurements) if memory_measurements else 0,
        avg_memory_mb=statistics.mean(memory_measurements)
        if memory_measurements
        else 0,
        memory_increase_mb=max(memory_measurements) - min(memory_measurements)
        if memory_measurements
        else 0,
        total_iterations=iterations,
        success_rate=successful_runs / iterations * 100,
        throughput_per_second=successful_runs / total_time,
        errors=errors,
    )


def stress_test(duration_seconds: int = 60) -> Dict[str, Any]:
    """
    Run stress test for a specified duration.

    Args:
        duration_seconds: How long to run the stress test

    Returns:
        Stress test results
    """
    print("🔥 Running stress test for {duration_seconds} seconds...")

    start_time = time.perf_counter()
    end_time = start_time + duration_seconds

    iterations = 0
    successful_runs = 0
    errors = []
    execution_times = []

    while time.perf_counter() < end_time:
        result = measure_single_execution()
        iterations += 1

        if result["success"]:
            successful_runs += 1
            execution_times.append(result["execution_time_ms"])
        else:
            errors.append(result["error"])

        if iterations % 10 == 0:
            elapsed = time.perf_counter() - start_time
            print(
                f"  {elapsed:.1f}s elapsed, {iterations} iterations, {successful_runs} successful"
            )

    total_time = time.perf_counter() - start_time

    return {
        "duration_seconds": total_time,
        "total_iterations": iterations,
        "successful_runs": successful_runs,
        "success_rate": successful_runs / iterations * 100 if iterations > 0 else 0,
        "throughput_per_second": successful_runs / total_time,
        "avg_execution_time_ms": statistics.mean(execution_times)
        if execution_times
        else 0,
        "errors": errors,
    }


def print_benchmark_results(result: BenchmarkResult, title: str = "Benchmark Results"):
    """Print formatted benchmark results."""
    print("\n{'=' * 60}")
    print("📊 {title}")
    print("{'=' * 60}")

    # Timing metrics
    print("⏱️  Execution Time Metrics:")
    print("   Min:     {result.min_time_ms:.2f}ms")
    print("   Max:     {result.max_time_ms:.2f}ms")
    print("   Average: {result.avg_time_ms:.2f}ms")
    print("   Median:  {result.median_time_ms:.2f}ms")
    print("   P95:     {result.p95_time_ms:.2f}ms")
    print("   P99:     {result.p99_time_ms:.2f}ms")

    # Performance assessment
    target_time = 100  # ms from documentation
    if result.avg_time_ms < target_time:
        print(
            "   ✅ Performance target met (avg: {result.avg_time_ms:.1f}ms < {target_time}ms)"
        )
    else:
        print(
            "   ⚠️  Performance target missed (avg: {result.avg_time_ms:.1f}ms > {target_time}ms)"
        )

    # Memory metrics
    print("\n💾 Memory Metrics:")
    print("   Peak Memory:    {result.peak_memory_mb:.2f}MB")
    print("   Average Memory: {result.avg_memory_mb:.2f}MB")
    print("   Memory Increase: {result.memory_increase_mb:.2f}MB")

    # Memory assessment
    target_memory = 10  # MB from documentation
    if result.peak_memory_mb < target_memory:
        print(
            "   ✅ Memory target met (peak: {result.peak_memory_mb:.1f}MB < {target_memory}MB)"
        )
    else:
        print(
            "   ⚠️  Memory target exceeded (peak: {result.peak_memory_mb:.1f}MB > {target_memory}MB)"
        )

    # Throughput metrics
    print("\n🚀 Throughput Metrics:")
    print("   Total Iterations: {result.total_iterations}")
    print("   Success Rate:     {result.success_rate:.1f}%")
    print("   Throughput:       {result.throughput_per_second:.2f} workflows/second")

    # Error summary
    if result.errors:
        print("\n❌ Errors ({len(result.errors)}):")
        error_counts = {}
        for error in result.errors:
            error_counts[error] = error_counts.get(error, 0) + 1

        for error, count in error_counts.items():
            print("   {count}x: {error}")
    else:
        print("\n✅ No errors encountered")


def main():
    """Run comprehensive benchmark suite."""
    print("🏥 HACS + LangGraph Workflow Benchmark Suite")
    print("=" * 60)

    # Sequential benchmark
    sequential_result = benchmark_sequential(iterations=100)
    print_benchmark_results(sequential_result, "Sequential Benchmark (100 iterations)")

    # Concurrent benchmark
    concurrent_result = benchmark_concurrent(iterations=50, max_workers=4)
    print_benchmark_results(
        concurrent_result, "Concurrent Benchmark (50 iterations, 4 workers)"
    )

    # Stress test
    print("\n{'=' * 60}")
    stress_result = stress_test(duration_seconds=30)
    print("📊 Stress Test Results (30 seconds)")
    print("{'=' * 60}")
    print("Duration:           {stress_result['duration_seconds']:.1f}s")
    print("Total Iterations:   {stress_result['total_iterations']}")
    print("Successful Runs:    {stress_result['successful_runs']}")
    print("Success Rate:       {stress_result['success_rate']:.1f}%")
    print(
        "Throughput:         {stress_result['throughput_per_second']:.2f} workflows/second"
    )
    print("Avg Execution Time: {stress_result['avg_execution_time_ms']:.2f}ms")

    if stress_result["errors"]:
        print("Errors:             {len(stress_result['errors'])}")
    else:
        print("Errors:             None ✅")

    # Summary
    print("\n{'=' * 60}")
    print("📋 Summary")
    print("{'=' * 60}")

    # Overall performance assessment
    all_results = [sequential_result, concurrent_result]
    avg_performance = statistics.mean([r.avg_time_ms for r in all_results])
    max_memory = max([r.peak_memory_mb for r in all_results])
    min_success_rate = min([r.success_rate for r in all_results])

    print("Overall Average Performance: {avg_performance:.2f}ms")
    print("Peak Memory Usage:           {max_memory:.2f}MB")
    print("Minimum Success Rate:        {min_success_rate:.1f}%")

    # Final assessment
    performance_ok = avg_performance < 100
    memory_ok = max_memory < 10
    reliability_ok = min_success_rate >= 99

    if performance_ok and memory_ok and reliability_ok:
        print("\n🎉 All performance targets met! Workflow is production-ready.")
    else:
        print("\n⚠️  Some performance targets not met:")
        if not performance_ok:
            print("   - Performance: {avg_performance:.1f}ms > 100ms target")
        if not memory_ok:
            print("   - Memory: {max_memory:.1f}MB > 10MB target")
        if not reliability_ok:
            print("   - Reliability: {min_success_rate:.1f}% < 99% target")


if __name__ == "__main__":
    main()
