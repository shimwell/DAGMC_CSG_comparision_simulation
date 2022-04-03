

import openmc
import openmc_data_downloader as odd


# Names of material tags can be found with the command line tool
# mbsize -ll dagmc.h5m | grep 'NAME = mat:'

rotation_angle=360
inner_blanket_radius = 100.
blanket_thickness = 70.
blanket_height = 500.
lower_blanket_thickness = 50.
upper_blanket_thickness = 40.
blanket_vv_gap = 20.
upper_vv_thickness = 10.
vv_thickness = 10.
lower_vv_thickness = 10.
fractional_height_of_source = 0.5

mat_vacuum_vessel = openmc.Material(name="vacuum_vessel")
mat_vacuum_vessel.add_element("Fe", 1, "ao")
mat_vacuum_vessel.set_density("g/cm3", 7.7)

mat_upper_blanket = openmc.Material(name="upper_blanket")
mat_upper_blanket.add_element("Li", 1, "ao")
mat_upper_blanket.set_density("g/cm3", 0.5)

mat_lower_blanket = openmc.Material(name="lower_blanket")
mat_lower_blanket.add_element("Li", 1, "ao")
mat_lower_blanket.set_density("g/cm3", 0.5)

mat_lower_vacuum_vessel = openmc.Material(name="lower_vacuum_vessel")
mat_lower_vacuum_vessel.add_element("Fe", 1, "ao")
mat_lower_vacuum_vessel.set_density("g/cm3", 7.7)

mat_upper_vacuum_vessel = openmc.Material(name="upper_vacuum_vessel")
mat_upper_vacuum_vessel.add_element("Fe", 1, "ao")
mat_upper_vacuum_vessel.set_density("g/cm3", 7.7)

mat_blanket = openmc.Material(name="blanket")
mat_blanket.add_element("Li", 1, "ao")
mat_blanket.set_density("g/cm3", 0.5)

materials = openmc.Materials(
    [
        mat_vacuum_vessel,
        mat_upper_blanket,
        mat_lower_blanket,
        mat_lower_vacuum_vessel,
        mat_upper_vacuum_vessel,
        mat_blanket,
    ]
)

#downloads the nuclear data and sets the openmc_cross_sections environmental variable
odd.just_in_time_library_generator(
    libraries='ENDFB-7.1-NNDC',
    materials=materials
)

# makes use of the dagmc geometry
dag_univ = openmc.DAGMCUniverse("dagmc.h5m")

# creates an edge of universe boundary
vac_surf = openmc.Sphere(r=10000, surface_id=9999, boundary_type="vacuum")

# specifies the region as below the universe boundary
region = -vac_surf

# creates a cell from the region and fills the cell with the dagmc geometry
containing_cell = openmc.Cell(cell_id=9999, region=region, fill=dag_univ)

geometry = openmc.Geometry(root=[containing_cell])

max_source_height = blanket_height + lower_vv_thickness + lower_blanket_thickness
min_source_height = lower_vv_thickness + lower_blanket_thickness
range_of_source_heights = max_source_height - min_source_height
absolute_height_of_source = (fractional_height_of_source * range_of_source_heights) + min_source_height


# creates a simple isotropic neutron source in the center with 14MeV neutrons
my_source = openmc.Source()
my_source.space = openmc.stats.Point((0, 0, absolute_height_of_source))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])

# specifies the simulation computational intensity
settings = openmc.Settings()
settings.batches = 10
settings.particles = 10000
settings.inactive = 0
settings.run_mode = "fixed source"
settings.source = my_source


tallies = openmc.Tallies()
for material in [
    mat_vacuum_vessel,
    mat_upper_blanket,
    mat_lower_blanket,
    mat_lower_vacuum_vessel,
    mat_upper_vacuum_vessel,
    mat_blanket]:

    flux_tally = openmc.Tally(name=f"flux_{material.name}")
    material_filter = openmc.MaterialFilter([material])
    flux_tally.filters = [material_filter]
    flux_tally.scores = ["flux"]
    tallies.append(flux_tally)



# groups the two tallies

# builds the openmc model
my_model = openmc.Model(
    materials=materials, geometry=geometry, settings=settings, tallies=tallies
)

# starts the simulation
my_model.run()


# open the results file
sp = openmc.StatePoint("statepoint.10.h5")

# access the tally using pandas dataframes

for material in [
    mat_vacuum_vessel,
    mat_upper_blanket,
    mat_lower_blanket,
    mat_lower_vacuum_vessel,
    mat_upper_vacuum_vessel,
    mat_blanket]:

    flux_tally = sp.get_tally(name=f"flux_{material.name}")
    

    # print cell tally results
    print(f"{material.name} = {flux_tally.mean.sum()}")
    # print(f"{flux_tally.std_dev}")



