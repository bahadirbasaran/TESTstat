import os
import asyncio
from math import ceil
from collections import defaultdict

from core.teststat import TestStat
from core.utils import get_batch, compare_output_equality


async def run_version_comparison(
    host,
    batch_size,
    txt_path,
    limit,
    dc_with_versions,
    comparison_fields
):

    async def _run_routine(test_input):

        expected_output = {"status_code": "200"}
        test_output = await teststat.run_test(dc, test_input, expected_output, return_data=True)
        output_per_version[test_input.split('&')[0]].append(test_output)

    teststat = TestStat(host)
    output_per_version = defaultdict(list)
    test_inputs = []
    mismatched_inputs = []
    dc, *versions = dc_with_versions.split('_')

    with open(txt_path) as file_reader:

        if not limit:
            lines = file_reader.readlines()

        elif '-' in limit:
            lines = file_reader.readlines()[int(limit.split('-')[0]):int(limit.split('-')[1])]

        else:
            lines = []
            try:
                for _ in range(int(limit)):
                    lines.append(next(file_reader))
            except StopIteration:
                pass

        resources = [resource.replace('\"', '').replace(',', '').strip() for resource in lines]

    for resource in resources:
        for version in versions:
            test_inputs.append(f"resource={resource}&preferred_version={version}")

    total_test_cases = len(test_inputs)
    num_mismatch = 0
    num_batches = ceil(total_test_cases / batch_size)

    # Create an event loop for a batch of coroutines, and proceed to the next when it's done
    for batch_index, batch in enumerate(get_batch(test_inputs, batch_size), 1):

        await asyncio.gather(*[_run_routine(test_input) for test_input in batch])

        print(f"-> Batch {batch_index}/{num_batches} has been completed!")

    # Close the session when all batches are done
    await teststat.session.close()

    for input, outputs in output_per_version.items():
        if compare_output_equality(comparison_fields, *outputs) is not True:
            num_mismatch += 1
            mismatched_inputs.append(input.split('=')[1])

    if not num_mismatch:
        print(
            f"\n\nAll {dc} test resources ({total_test_cases}) return the same response for "
            f"{comparison_fields} in versions {', '.join(versions)}\n\n"
        )
    else:
        with open(f"data/{dc_with_versions}.txt", 'w') as file_writer:
            file_writer.write('\n'.join(mismatched_inputs))

        print(f"\n\nTotal Test Inputs:  {total_test_cases:,}")
        print(f"Failed Test Inputs: {num_mismatch:,}\n")

        output_path = f"{os.path.abspath('..')}/data/{dc_with_versions}.txt"
        print(
            f"{dc} test resources that do not return the same response for {comparison_fields} "
            f"in versions {', '.join(versions)} have been listed at:\n\n{output_path}\n"
        )
