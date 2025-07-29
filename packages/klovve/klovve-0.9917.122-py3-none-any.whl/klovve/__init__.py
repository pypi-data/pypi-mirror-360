#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Klovve.

Everything needed for a simple Klovve application is in on of the submodules that are directly available after
:code:`import klovve`.

There are more things in other submodules, but you will rarely, if ever, need them.
"""
import klovve.app
import klovve.effect
import klovve.event
import klovve.model
import klovve.timer
import klovve.ui.dialog
import klovve.views


# TODO  toast notifications
# TODO  gtk: some nice (static?!) animations
# TODO  label mnemonic accelerators (optionally via some 'mnemonic' flag; then like in gtk or similar)
# TODO  combobox / accordion / breadcrumb / buttonbar
# TODO  annize studio like (boxes inside boxes, with stuff inside)
# TODO  console view (like annize do, or krrez runner view)
