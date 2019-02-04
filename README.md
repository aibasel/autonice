# About

`autonice` is a load-balancing script for users of the Slurm workload
manager.

`autonice` runs in the background and periodically checks which
proportion of the available computational resources the user is using.
If it is more than their fair share, their array jobs are deprioritized.
If it is less than their fair share, they are prioritized. Non-array
jobs are always ignored by `autonice`.

Priorities are adjusted by setting `nice` values, so `autonice` will
overwrite all manually set `nice` values.

The current version of `autonice` is hard-coded for use in the `infai_1`
and `infai_2` partitions of the Slurm instance at the University of
Basel. For `autonice` to work effectively, every user must run
`autonice` for all partitions they use.

# Usage

Start `autonice` in the background with:

```bash
nohup ./autonice.py [--log-file LOG_FILE] <partition> &
```
replacing ```<partition>``` with a Slurm partition, such as `infai_1`
and `infai_2`. `autonice` will keep running after you log out.
For multiple partitions, use multiple invocations of `autonice`.

Running `autonice` under `nohup` redirects all output to a file called
`nohup.out`, which you can safely delete when `autonice` is not
running. Deleting the file while `autonice` is running will likely lead
to quirky behavior of the file system.

# Example

```bash
nohup ./autonice.py --log-file ~/autonice_infai_1.log infai_1 &
nohup ./autonice.py --log-file ~/autonice_infai_2.log infai_2 &
exit
```
# Stopping

To stop `autonice`, for example before a restart, a brute-force
method is

```bash
killall python
```

but of course this is not advisable if you run other Python processes.
A safer alternative is

```bash
ps x | grep autonice
```
and then kill just the relevant process IDs.

# Reserving memory

You can set the amount of memory `sbatch` allocates to each core with
the `--mem-per-cpu` option. (Note that `cpu` refers to a core/processor
in Slurm parameter strings.) Autonice assumes that you only allocate as
much memory as is available per core. This is `3872M` on `infai_1` and
`6354M` on `infai_2`. If you need more memory, you must allocate
multiple cores to each task by using the `--cpus-per-task` option.

# Ordering jobs

To let Slurm run job 123 before job 456, you can use the command
`scontrol update dependency=123 jobid=456`. This is useful to order your
own jobs, but also if you want to let someone else's jobs finish before
yours start.

# Known Issues

Many. The current version of `autonice` is very much a prototype.
See `notes.org` for some information on known limitations, RFEs etc.

# Version History

## autonice 0.3 (January 4, 2019)
- Count the number of used cores instead of running jobs.
- Use more robust format string for obtaining pending jobs.

## autonice 0.2 (September 14, 2018)
- Port code from Bash to Python.
- Ignore non-array jobs.
- Log file configurable (now defaults to stdout).

## autonice 0.1 (October 17, 2017)
- First public release of `autonice`.

# License

`autonice` is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

`autonice` is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
