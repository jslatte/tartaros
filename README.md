Tartaros
============



Submodules:

* Cerberus: user interface (now using web2py).
* Charon: SQLite database API.
* Danaides: diagnostic utility.
* Hestia: ViM.
* Ixion: GPS simulation.
* Minos: Build management (TeamCity).
* Orpheus: Test reporting (TestRail).
* Sisyphus: Test data generation.
* Tantalus: DVR simulation.

Potential UI Functions:
* Make performance and stress tests referable outside of normal regression.
* Add/edit license configurations.
* Add/edit depot sites (DVRs).
* Edit procedure steps (including verification flag).
* Unhide procedure on loading test case.
* Set TestRail Plan ID.
* Adding procedure step retains and refreshes current procedure layout.
* Can insert steps into procedure layout.
* Version dependent procedure steps.
* Click-to-edit view of testcases w/ summary.
* Show expected variables when adding/modifying input steps.
* site/dvr type configuration (e.g., changing "clip downloading site" from DVR 1 to 2, parameters).
* add activation option for testcases to activate/deactivate.

Bugs:
* If specifying a "full" license with a 3.2 installation, will attempt to configure 3.4 full license.