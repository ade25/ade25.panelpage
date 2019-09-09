# -*- coding: utf-8 -*-
# Module providing version specific upgrade steps
import logging

default_profile = 'profile-ade25.panelpage:default'
logger = logging.getLogger(__name__)


def upgrade_1001(setup):
    setup.runImportStepFromProfile(default_profile, 'typeinfo')
