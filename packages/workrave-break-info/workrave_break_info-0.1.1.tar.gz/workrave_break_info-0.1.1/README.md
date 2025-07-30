This is basically the packaging of `workrave_break_info.py` from
`https://github.com/rcaelers/workrave/tree/main/contrib/waybar-yambar-poss-other-applets`
as a module, for use cases where just putting it in the same directory
as the Python script that imports it is inconvenient or not good enough.

Installing this module also provides a script `workrave-break-info`,
which basically runs this module as a script.

Currently, documentation is mostly in the form of comments at the top
of the module and the output of `workrave-break-info --help` (or
`workrave_break_info.py --help`).

Changes
-------

* 0.1.0: First release
* 0.1.1: Fix broken workrave-break-info script
