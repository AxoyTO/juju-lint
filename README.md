= Juju Lint =

== Introduction ==

This is intended to be run against a yaml or json dump of Juju status, a YAML
dump of a juju bundle, or a remote cloud or clouds via SSH.

To generate a status if you just want to audit placement:

    juju status --format yaml > status.yaml

For auditing configuration, you would want (you need charm defaults to avoid
false positives):

    juju export-bundle --include-charm-defaults > bundle.yaml

Then run `juju-lint` (using a rules file of `lint-rules.yaml`):

    juju-lint status.yaml (or bundle.yaml)

You can also enable additional checks for specific cloud types by specifying
the cloud type with `-t` as such:

    juju-lint -t openstack bundle.yaml

For remote or mass audits, you can remote audit clouds via SSH.
To do this, you will need to add the clouds to your config file in:

    ~/.config/juju-lint/config.yaml

See the example config file in the `jujulint` directory of this repo.
This tool will use your existing SSH keys, SSH agent, and SSH config.
If you are running from the snap, you will need to connect the `ssh-keys`
interface in order to grant access to your SSH configuation.

To use a different rules file:

    juju-lint -c my-rules.yaml

For all other options, consult `juju-lint --help`

== Example ==

A typical use case is linting an openstack cloud:

    juju status -m openstack --format=json > juju-status.json
    juju export-bundle --include-charm-defaults -m openstack > bundle.yaml
    juju-lint -c /snap/juju-lint/current/contrib/openstack-focal-ovn.yaml \
        -t openstack juju-status.json
    juju-lint -c /snap/juju-lint/current/contrib/openstack-focal-ovn.yaml \
        -t openstack bundle.yaml

== Rules File ==

For an example of a rules file, see `example-lint-rules.yaml`.

Supported top-level options for your rules file:

 1. `subordinates` - required subordinates.
 2. `known charms` - all primary charms should be in this list.
 3. `operations [mandatory|optional|subordinate]`
 4. `openstack [mandatory|optional|subordinate]`
 5. `config` - application configuration auditing
 6. `[openstack|kubernetes] config` - config auditing for specific cloud types.
 7. `space checks` - enforce/ignore checks for relation binding space
    mismatches.
 8. `!include <relative path>` - Extension to yaml to include files.

 === Space checks ===

All relations defined within a bundle, except for cross-model relationships,
will be checked for mismatches of their space bindings.  By default, mismatches
are logged as warnings as this is not necessarily a critical error.

The following options are available to either log such mismatches as errors or
to ignore them entirely:

 1. `enforce endpoints` - A list of <charm>:<endpoint> strings.  If a mismatch
    matches one of these endpoints, it will be flagged as an error.
 2. `enforce relations` - A list of two-item <charm>:<endpoint> string lists,
    representing the two linked endpoints of a relation.  If a mismatch
    matches one of these relations, it will be flagged as an error.
 1. `ignore endpoints` - A list of <charm>:<endpoint> strings.  If a mismatch
    matches one of these endpoints, it will be ignored.
 1. `ignore relations` - A list of two-item <charm>:<endpoint> string lists,
    representing the two linked endpoints of a relation.  If a mismatch
    matches one of these relations, it will be ignored.

In the case of a mismatch matching both enforce and ignore rules, the enforce
rule will "win" and it will be flagged as an error.

Note that all the above checks use charm names rather than application names
in their endpoint strings.

== License ==

Copyright 2020 Canonical Limited.
License granted by Canonical Limited.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3, as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranties of
MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
