import openmc

import openmc_data_downloader as odd

# MATERIALS

breeder_material = openmc.Material(1, "PbLi")  # Pb84.2Li15.8
breeder_material.add_element('Pb', 84.2, percent_type='ao')
breeder_material.add_element('Li', 15.8, percent_type='ao', enrichment=50.0, enrichment_target='Li6', enrichment_type='ao')  # 50% enriched
breeder_material.set_density('atom/b-cm', 3.2720171e-2)  # around 11 g/cm3


steel = openmc.Material(name='steel')
steel.set_density('g/cm3', 7.75)
steel.add_element('Fe', 0.95, percent_type='wo')
steel.add_element('C', 0.05, percent_type='wo')

mats = openmc.Materials([breeder_material, steel])


# GEOMETRY

# surfaces
vessel_inner = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610, boundary_type='vacuum')


# cells
inner_vessel_region = -vessel_inner
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)

first_wall_region = -first_wall_outer_surface & +vessel_inner
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = steel

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[inner_vessel_cell, first_wall_cell, breeder_blanket_cell])
geom = openmc.Geometry(universe)


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
sett.batches = 10
sett.inactive = 0
sett.particles = 500
sett.run_mode = 'fixed source'

# Create a DT point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source


tallies = openmc.Tallies()

# added a cell tally for tritium production
cell_filter = openmc.CellFilter(breeder_blanket_cell)
tbr_tally = openmc.Tally(name='TBR')
tbr_tally.filters = [cell_filter]
tbr_tally.scores = ['(n,Xt)']  # Where X is a wildcard character, this catches any tritium production
tallies.append(tbr_tally)


odd.just_in_time_library_generator(
    libraries=['ENDFB-7.1-NNDC', 'TENDL-2019'],
    materials=mats
)


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)

sp_filename = model.run()

# open the results file
sp = openmc.StatePoint(sp_filename)

# access the tally using pandas dataframes
tbr_tally = sp.get_tally(name='TBR')
df = tbr_tally.get_pandas_dataframe()

tbr_tally_result = df['mean'].sum()
tbr_tally_std_dev = df['std. dev.'].sum()

# print results
print('The tritium breeding ratio was found, TBR = ', tbr_tally_result)
print('Standard deviation on the tbr tally is ', tbr_tally_std_dev)
