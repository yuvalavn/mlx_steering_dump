# Copyright (c) 2020 Mellanox Technologies, Inc.  All rights reserved.
#
# This software is available to you under a choice of one of two
# licenses.  You may choose to be licensed under the terms of the GNU
# General Public License (GPL) Version 2, available from the file
# COPYING in the main directory of this source tree, or the
# OpenIB.org BSD license below:
#
#     Redistribution and use in source and binary forms, with or
#     without modification, are permitted provided that the following
#     conditions are met:
#
#      - Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      - Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials
#        provided with the distribution.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from src.parsers import dr_hw_ste_parser
from dr_utilities import _srd
from dr_utilities import dec_indent
from dr_utilities import dict_join_str
from dr_utilities import dr_dump_rec_type
from dr_utilities import dr_obj
from dr_utilities import get_indent_str
from dr_utilities import inc_indent
from dr_utilities import print_dr


class dr_dump_rule(dr_obj):
    def __init__(self, data):
        keys = ["dr_dump_rec_type", "id", "matcher_id"]
        self.data = dict(zip(keys, data))
        self.rule_entry_list = []
        self.rule_action_list = []

    def dump_str(self):
        return "rule %s\n" % (_srd(self.data, "id"))

    def dump_match_str(self, verbose, raw):
        MATCH = "match: "
        match_str = MATCH

        for i in range(0, len(self.rule_entry_list)):
            rule_mem = self.rule_entry_list[i]
            match_str += rule_mem.dump_str(verbose, raw) + " "
            if verbose and i != (len(self.rule_entry_list) - 1):
                match_str += "\n" + get_indent_str() + len(MATCH) * " "

        return match_str + "\n"

    def dump_actions_str(self):
        ACTION = "action: "
        action_str = ACTION

        for i in range(0, len(self.rule_action_list)):
            action = self.rule_action_list[i]
            action_str += action.dump_str()
            if i != (len(self.rule_action_list) - 1):
                action_str += " & "

        return action_str + "\n"

    def print_tree_view(self, dump_ctx, verbose, raw):
        print_dr(self.dump_str())
        inc_indent()
        print_dr(self.dump_match_str(verbose, raw))
        print_dr(self.dump_actions_str())
        dec_indent()

    def print_rule_view(self, dump_ctx, verbose, raw):
        dmn_str = "domain %s, " % (_srd(dump_ctx.domain.data, "id"))
        tbl_str = "table %s, " % (_srd(dump_ctx.table.data, "id"))
        matcher_str = "matcher %s, " % (_srd(dump_ctx.matcher.data, "id"))

        print_dr(dmn_str + tbl_str + matcher_str + self.dump_str())
        inc_indent()
        print_dr(self.dump_match_str(verbose, raw))
        print_dr(self.dump_actions_str())
        dec_indent()

    def add_rule_entry(self, rule_mem):
        self.rule_entry_list.append(rule_mem)

    def add_action(self, action):
        self.rule_action_list.append(action)


class dr_dump_rule_entry_rx_tx(dr_obj):
    def __init__(self, data):
        keys = ["dr_dump_rec_type", "ste_icm_addr", "rule_id", "ste_data"]
        self.data = dict(zip(keys, data))

    def dump_str(self, verbose, raw):
        parsed_ste = dr_hw_ste_parser.mlx5_hw_ste_parser(self.data['ste_data'], raw)
        if "tag" not in parsed_ste.keys():
            return ""

        if verbose == 0:
            return "%s" % dict_join_str(parsed_ste["tag"])
        else:
            if self.data['dr_dump_rec_type'] == dr_dump_rec_type.DR_DUMP_REC_TYPE_RULE_RX_ENTRY.value[0]:
                rx_tx = "RX"
            else:
                rx_tx = "TX"

            if verbose == 1:
                return "(%s STE, icm_idx %s): %s" % (
                       rx_tx, _srd(self.data, "ste_icm_addr"),
                       dict_join_str(parsed_ste["tag"]))
            elif verbose >= 2:
                return "(%s STE, icm_idx %s): %s (%s)" % (
                    rx_tx, _srd(self.data, "ste_icm_addr"),
                    _srd(self.data, "ste_data"),
                    dict_join_str(parsed_ste["tag"]))