# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright (C) 2019 Federacion Galega de Natación (FEGAN) http://www.fegan.org
# Author: Daniel Muñiz Fontoira (2017) <dani@damufo.com>


"""
xesde sql to update list
select "'" || club_id ||"': ('" || short_desc ||"', '" || long_desc || "'),"
from clubs where not club_id like "D%"order by club_id;
"""


import csv
clubs = {}
with open('clubs.csv', encoding="utf8", newline='') as f:
    reader = csv.reader(f, dialect='unix', delimiter=',')
    for row in reader:
        clubs[row[0]] = (row[1], row[2])
