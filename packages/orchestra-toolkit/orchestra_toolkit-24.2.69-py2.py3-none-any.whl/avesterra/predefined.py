""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import entity_of

# -- AvesTerra Registries/Entities (1..9)
avesterra_registry = entity_of("<0|0|1>")
taxonomy_registry = entity_of("<0|0|2>")
declaration_registry = entity_of("<0|0|3>")
network_registry = entity_of("<0|0|4>")
host_registry = entity_of("<0|0|5>")
trash_entity = entity_of("<0|0|6>")
agent_registry = entity_of("<0|0|7>")
tuple_registry = entity_of("<0|0|8>")
ontology_registry = entity_of("<0|0|9>")

# -- AvesTerra Adapter Outlets(10..19)
registry_outlet = entity_of("<0|0|10>")
object_outlet = entity_of("<0|0|11>")
folder_outlet = entity_of("<0|0|12>")
file_outlet = entity_of("<0|0|13>")
general_outlet = entity_of("<0|0|14>")
authentication_outlet = entity_of("<0|0|15>")
trash_outlet = entity_of("<0|0|16>")
agent_outlet = entity_of("<0|0|17>")
tuple_outlet = entity_of("<0|0|18>")
privacy_outlet = entity_of("<0|0|19>")

# -- AvesTerra  Resources (20..29)
executable_registry = entity_of("<0|0|20>")
source_registry = entity_of("<0|0|21>")
certificate_registry = entity_of("<0|0|22>")
documentation_registry = entity_of("<0|0|23>")
example_registry = entity_of("<0|0|24>")
test_registry = entity_of("<0|0|25>")
file_registry = entity_of("<0|0|26>")
entity_registry = entity_of("<0|0|27>")
spare_registry = entity_of("<0|0|28>")
build_registry = entity_of("<0|0|29>")

release_registry = entity_of("<1|1|29>")

# -- Template registries (30..39)
# Avial 4.11 Predefined registries updated
model_registry = entity_of("<0|0|30>")
import_registry = entity_of("<0|0|31>")
export_registry = entity_of("<0|0|32>")
configuration_registry = entity_of("<0|0|33>")
enrichment_registry = entity_of("<0|0|34>")
relationship_registry = entity_of("<0|0|35>")

# -- Special adapters/subscribers (40..99)
space_outlet = entity_of("<0|0|40>")
geo_space = entity_of("<0|0|41>")
hyper_space = entity_of("<0|0|42>")
cyber_space = entity_of("<0|0|43>")
meta_space = entity_of("<0|0|44>")  # Avial 4.11 Added meta_space

boost_outlet = entity_of("<0|0|50>")
thrust_outlet = entity_of("<0|0|51>")
tunnel_outlet = entity_of("<0|0|52>")  # Avial 4.7: Tunnel outlet

# -- AvesTerra System Registries/Outlets (100..999)
atra_registry = entity_of("<0|0|100>")
avert_registry = entity_of("<0|0|101>")
avian_registry = entity_of("<0|0|102>")
aware_registry = entity_of("<0|0|103>")

geospace_registry = entity_of("<0|0|111>")
community_registry = entity_of("<0|0|211>")
contact_registry = entity_of("<0|0|212>")
municipal_registry = entity_of("<0|0|311>")
health_registry = entity_of("<0|0|312>")
directory_registry = entity_of("<0|0|411>")
traffic_registry = entity_of("<0|0|511>")
repair_registry = entity_of("<0|0|611>")
relay_registry = entity_of("<0|0|711>")
utility_registry = entity_of("<0|0|811>")
emergency_registry = entity_of("<0|0|911>")

# -- Reserved Registries (1000..99999)
orchestra_registry = entity_of("<0|0|01000>")
sirius_registry = entity_of("<0|0|01001>")

american_registry = entity_of("<0|0|20016>")
georgetown_registry = entity_of("<0|0|20057>")
hanging_steel_registry = entity_of("<0|0|20165>")
agent_labs_registry = entity_of("<0|0|21029>")
darpa_registry = entity_of("<0|0|22203>")
ornl_registry = entity_of("<0|0|37831>")
ledr_registry = entity_of("<0|0|94111>")
llnl_registry = entity_of("<0|0|94550>")
pnnl_registry = entity_of("<0|0|99354>")
