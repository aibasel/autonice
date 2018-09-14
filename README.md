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
and `infai_2``partitions of the Slurm instance at the University of
Basel. For `autonice` to work effectively, every user must run
`autonice` for all partitions they use.

# Usage

Start `autonice` in the background with:

```bash
nohup ./autonice.py <partition> &
```
replacing ```<partition>``` with a Slurm partition such as `infai_1`
or `infai_2`.

After running this command, log out.

If you want to stop `autonice` later, for example before a restart,
use

```bash
killall autonice.py
```

Running `autonice` under `nohup` redirects all output to a file called
`nohup.out`, which you can safely delete when `autonice` is not
running. Deleting the file while `autonice` is running will likely lead
to quirky behavior of the file system.

# Known Issues

Many. The current version of `autonice` is very much a prototype.
See `notes.org` for some information on known limitations, RFEs etc.

# Version History

* `autonice 0.2` was tagged on TODO. Changes:
  * Port code from Bash to Python.
  * Ignore non-array jobs.
  * Write to stdout instead of hard-coded logfile.

* `autonice 0.1` was tagged on October 17, 2017. It is the first
  public release of `autonice`.

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
