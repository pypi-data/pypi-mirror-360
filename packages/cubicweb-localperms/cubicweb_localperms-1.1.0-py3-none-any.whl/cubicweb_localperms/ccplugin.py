# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-ctl plugin providing the check-localperms command"""

from __future__ import print_function

__docformat__ = "restructuredtext en"

import os

from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL

try:
    from cubicweb.devtools.instrument import PropagationAnalyzer, warn, get_color

    register_command = True
except ImportError:
    # either devtools (development package) or instrumentalize (insufficient
    # version) is uninstalled, skip the command
    register_command = False
else:

    class PermissionPropagationAnalyzer(PropagationAnalyzer):
        prop_rel = "require_permission"

        def is_root(self, eschema):
            return "granted_permission" in eschema.subjrels

        def should_include(self, eschema):
            """override to also include type using require_permission in some read
            rql expression
            """
            return super(PermissionPropagationAnalyzer, self).should_include(
                eschema
            ) or any(
                self.prop_rel in rqlexpr.expression
                for rqlexpr in eschema.get_rqlexprs("read")
            )


def read_permission_edges(eschemas):
    """return a set of edges where <from node>'s read perms are referencing <to
    node>'s permissions.

    Each edge is defined by a 4-uple (from node, to node, rtype, package) where
    `rtype` is the relation type bringing from <from node> to <to node> and
    `package` is the cube defining the read permission rql expresssion.
    """
    perm_edges = set()
    for eschema in eschemas:
        for rqlexpr in eschema.get_rqlexprs("read"):
            triplets = [expr.split() for expr in rqlexpr.expression.split(",")]
            triplets = [
                triplet
                for triplet in triplets
                if len(triplet) == 3 and triplet[1] != "has_group_permission"
            ]
            for triplet in triplets:
                subjvar, rel, objvar = triplet
                if rel == "require_permission":
                    if subjvar != "X":
                        searchvar = subjvar
                        break
            else:
                continue
            for triplet in triplets:
                subjvar, rel, objvar = triplet
                if rel == "require_permission":
                    continue
                if subjvar == searchvar:
                    if objvar != "X":
                        print(
                            "Oops, unhandled 2 hops",
                            eschema,
                            triplet,
                            searchvar,
                            objvar,
                        )
                        continue
                    for target in eschema.objrels[rel].targets(eschema, "object"):
                        if target in eschemas:
                            perm_edges.add(
                                (eschema.type, target.type, rel, rqlexpr.package)
                            )
                elif objvar == searchvar:
                    if subjvar != "X":
                        print(
                            "Oops, unhandled 2 hops",
                            eschema,
                            triplet,
                            searchvar,
                            subjvar,
                        )
                        continue
                    for target in eschema.subjrels[rel].targets(eschema, "subject"):
                        if target in eschemas:
                            perm_edges.add(
                                (eschema.type, target.type, rel, rqlexpr.package)
                            )
    return perm_edges


class CheckLocalPermsCommand(Command):
    """Analyse local permissions configuration.

    It will load the given cube schema and hooks, analyze local permissions in
    read permission and propagation rules to print on the standart output
    warnings about detected problems.
    """

    name = "check-localperms"
    arguments = "<cube>"
    min_args = max_args = 1
    options = (
        (
            "graph",
            {
                "short": "g",
                "type": "string",
                "metavar": "<file>",
                "default": None,
                "help": "draw propagation graph in the given file. Require pygraphviz installed",
            },
        ),
    )

    def run(self, args):
        """run the command with its specific arguments"""
        cube = args[0]
        # instrumentalize cube's hooks S_RELS / O_RELS (has to be done before
        # vreg init)
        os.environ["LOCALPERMS_INSTRUMENTALIZE"] = "1"
        # get config, schema and vreg
        analyzer = PermissionPropagationAnalyzer()
        vreg, eschemas = analyzer.init(cube)
        if not eschemas:
            warn("nothing to analyze")
            return
        # get propagation rules
        from cubicweb_localperms.hooks import S_RELS, O_RELS  # local import necessary

        prop_edges = analyzer.prop_edges(S_RELS, O_RELS, eschemas)
        # get read perms check
        perm_edges = read_permission_edges(eschemas)
        # detect pbs
        problematic = analyzer.detect_problems(eschemas, prop_edges)
        for eschema in eschemas:
            # used by read perm (and not a security root) but not propagated
            if (
                not analyzer.is_root(eschema)
                and any(edge for edge in perm_edges if edge[1] == eschema)
                and not any(edge for edge in prop_edges if edge[1] == eschema)
            ):
                warn(
                    "%s is used in a read permission but isn't reached by "
                    "propagation",
                    eschema,
                )
                problematic.add(eschema)
        # build graph if asked
        if self.config.graph:
            graph = analyzer.init_graph(eschemas, prop_edges, problematic)
            for subj, obj, rtype, package in perm_edges:
                graph.add_edge(
                    str(subj),
                    str(obj),
                    label=rtype,
                    color=get_color(package),
                    arrowhead="normal",
                    style="dashed",
                )
            analyzer.add_colors_legend(graph)
            # auto layout and draw
            graph.layout(prog="dot")
            graph.draw(self.config.graph)
        # print graph.string()


if register_command:
    CWCTL.register(CheckLocalPermsCommand)
