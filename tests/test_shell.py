import pytest
from onesync.shell import shell


async def test_long_cmd():
    cmd = """for (( i = 0; i < 3; i++ )); do echo "Current time: $(date +"%T")"; sleep 1; done"""
    # sync_run(cmd, stdout=sys.stdout, shell=True, executable=EXECUTABLE)
    await shell(cmd)


async def test_err_cmd():
    cmd = "cat non_existent_file.txt"
    await shell(cmd)


# async def test_async_group():
#     await asyncio.gather(test_long_cmd(), test_err_cmd())



