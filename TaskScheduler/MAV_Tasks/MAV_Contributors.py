# -*- coding: utf-8 -*-

'''
Created on Friday 02.03.2018
Copyright Henricus N. Basien
Author: Henricus N. Basien
Email: Henricus@Basien.de
'''

#****************************************************************************************
# Imports
#****************************************************************************************

from Workforce import Workforce,Team

#****************************************************************************************
# Contributors
#****************************************************************************************

Salery = 0

TeamMembers = []
TeamMembers.append("Henricus")
TeamMembers.append("Casper")
TeamMembers.append("Salomon")
TeamMembers.append("Luuk")
TeamMembers.append("Jari")
TeamMembers.append("Sukrit")

team = []
for TeamMember in TeamMembers:
    team.append(Workforce(Name=TeamMember,HourlyRate=Salery,Workweek_Avg=8))

#========================================================================================
# Team
#========================================================================================

MAV_FullTeam = Team("MAV Developers",team)
