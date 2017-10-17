# About

`autonice` is a load-balancing script for users of the Slurm workload
manager.

`autonice` runs in the background and periodically checks which
proportion of the available computational resources the user is using.
If it is more than their fair share, their jobs are deprioritized. If
it is less than their fair share, their jobs are prioritized.
Priorities are adjusted by setting `nice` values, so `autonice` will
overwrite all manually set `nice` values.

The current version of `autonice` is hard-coded for use in the `infai`
partition of the Slurm instance at the University of Basel. For
`autonice` to work effectively, every user of the partition must run
`autonice`.

# Usage

Start `autonice` in the background with:

```bash
nohup ./autonice_prototype.sh --silent &
```

After running this command, log out.

If you want to stop `autonice` later, for example before a restart,
use

```bash
killall autonice_prototype.sh
```

Running `autonice` under `nohup` leaves behind an empty file called
`nohup.out`, which you can safely delete when `autonice` is not
running. Deleting the file while autonice is running is not dangerous,
but will likely lead to quirky behavior of the file system.

# Known Issues

Many. The current version of `autonice` is very much a prototype.
See `notes.org` for some information on known limitations, RFEs etc.

# Version History

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
