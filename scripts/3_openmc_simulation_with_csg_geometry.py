
import neutronics_material_maker as nmm
import openmc
import openmc_data_downloader as odd



inner_blanket_radius = 100.
blanket_thickness = 70.
blanket_height = 500.
lower_blanket_thickness = 50.
upper_blanket_thickness = 40.
blanket_vv_gap = 20.
upper_vv_thickness = 10.
vv_thickness = 10.
lower_vv_thickness = 10.

simulation_batches = 10
simulation_particles_per_batch = 1000
fractional_height_of_source = 0.5


mat_vessel = openmc.Material(name="vacuum_vessel")
mat_vessel.add_element("Fe", 89, "ao")
mat_vessel.add_element("Cr", 9.1, "ao")
mat_vessel.add_element("Mo", 1, "ao")
mat_vessel.add_element("Mn", 0.5, "ao")
mat_vessel.add_element("Si", 0.4, "ao")
mat_vessel.set_density("g/cm3", 7.96)

mat_blanket = openmc.Material(name="upper_blanket")
mat_blanket.add_element("Li", 1, "ao")
mat_blanket.set_density("g/cm3", 0.46721185)

materials = openmc.Materials([mat_blanket, mat_vessel])

odd.just_in_time_library_generator(
    libraries=["ENDFB-7.1-NNDC", "TENDL-2019"],
    materials=materials,
    overwrite=False
)

# surfaces
inner_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius)
outer_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius + blanket_thickness)

inner_vessel_cylinder = openmc.ZCylinder(r=inner_blanket_radius + blanket_thickness + blanket_vv_gap)
outer_vessel_cylinder = openmc.ZCylinder(
    r=inner_blanket_radius + blanket_thickness + blanket_vv_gap + vv_thickness,
    boundary_type="vacuum",
)

upper_vessel_bottom = openmc.ZPlane(z0=blanket_height + lower_vv_thickness + lower_blanket_thickness)
upper_vessel_top = openmc.ZPlane(z0=blanket_height + lower_vv_thickness + lower_blanket_thickness + upper_vv_thickness)

lower_blanket_top = openmc.ZPlane(z0=lower_vv_thickness + lower_blanket_thickness)
lower_blanket_bottom = openmc.ZPlane(z0=lower_vv_thickness)

upper_blanket_bottom = upper_vessel_top
upper_blanket_top = openmc.ZPlane(
    z0=blanket_height + lower_vv_thickness + lower_blanket_thickness + upper_vv_thickness + upper_blanket_thickness,
    boundary_type="vacuum",
)

lower_vessel_top = lower_blanket_bottom
lower_vessel_bottom = openmc.ZPlane(z0=0, boundary_type="vacuum")

# regions
inner_void_region = -upper_vessel_bottom & +lower_blanket_top & -inner_blanket_cylinder
blanket_region = -upper_vessel_bottom & +lower_blanket_top & +inner_blanket_cylinder & -outer_blanket_cylinder

blanket_upper_region = -inner_vessel_cylinder & -upper_blanket_top & +upper_blanket_bottom
blanket_lower_region = -inner_vessel_cylinder & -lower_blanket_top & +lower_blanket_bottom

outer_void_region = -upper_vessel_bottom & +lower_blanket_top & -inner_vessel_cylinder & +outer_blanket_cylinder

vessel_region = -upper_blanket_top & +lower_vessel_bottom & -outer_vessel_cylinder & +inner_vessel_cylinder
vessel_upper_region = -upper_vessel_top & +upper_vessel_bottom & -inner_vessel_cylinder
vessel_lower_region = -lower_vessel_top & +lower_vessel_bottom & -inner_vessel_cylinder

# cells
vessel_cell_lower = openmc.Cell(region=vessel_lower_region, name='vessel_cell_lower')
vessel_cell_upper = openmc.Cell(region=vessel_upper_region, name='vessel_cell_upper')
vessel_cell_cylinder = openmc.Cell(region=vessel_region, name='vessel_cell_cylinder')
vessel_cell_lower.fill = mat_vessel
vessel_cell_upper.fill = mat_vessel
vessel_cell_cylinder.fill = mat_vessel

blanket_cell_cylinder = openmc.Cell(region=blanket_region, name='blanket_cell_cylinder')
blanket_cell_upper = openmc.Cell(region=blanket_upper_region, name='blanket_cell_upper')
blanket_cell_lower = openmc.Cell(region=blanket_lower_region, name='blanket_cell_lower')
blanket_cell_cylinder.fill = mat_blanket
blanket_cell_upper.fill = mat_blanket
blanket_cell_lower.fill = mat_blanket

void_cell1 = openmc.Cell(region=inner_void_region)
void_cell2 = openmc.Cell(region=outer_void_region)

universe = openmc.Universe(
    cells=[
        void_cell1,
        void_cell2,
        vessel_cell_lower,
        vessel_cell_upper,
        vessel_cell_cylinder,
        blanket_cell_cylinder,
        blanket_cell_upper,
        blanket_cell_lower,
    ]
)

geom = openmc.Geometry(universe)

max_source_height = blanket_height + lower_vv_thickness + lower_blanket_thickness
min_source_height = lower_vv_thickness + lower_blanket_thickness
range_of_source_heights = max_source_height - min_source_height
absolute_height_of_source = (fractional_height_of_source * range_of_source_heights) + min_source_height

# initialises a new source object
my_source = openmc.Source()

# sets the location of the source to x=0 y=0 z=0
my_source.space = openmc.stats.Point((0, 0, absolute_height_of_source))

# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()

# sets the energy distribution to 100% 14MeV neutrons
my_source.energy = openmc.stats.Discrete([14e6], [1])

settings = openmc.Settings()
settings.inactive = 0
settings.run_mode = "fixed source"
settings.batches = simulation_batches
settings.particles = simulation_particles_per_batch
settings.source = my_source
settings.photon_transport = True
# settings.seed = 1

tallies = openmc.Tallies()

for cell in [
    vessel_cell_lower,
    vessel_cell_upper,
    vessel_cell_cylinder,
    blanket_cell_cylinder,
    blanket_cell_upper,
    blanket_cell_lower]:

    flux_tally = openmc.Tally(name=f"flux_{cell.name}")
    cell_filter = openmc.CellFilter([cell])
    flux_tally.filters = [cell_filter]
    flux_tally.scores = ["flux"]
    tallies.append(flux_tally)

model = openmc.model.Model(geom, materials, settings, tallies)

sp_filename = model.run()

sp = openmc.StatePoint(sp_filename)


for cell in [
    vessel_cell_lower,
    vessel_cell_upper,
    vessel_cell_cylinder,
    blanket_cell_cylinder,
    blanket_cell_upper,
    blanket_cell_lower]:
    
    tally_from_sp = sp.get_tally(name=f"flux_{cell.name}")
    df = tally_from_sp.get_pandas_dataframe()

    tally_result = df['mean'].sum()
    tally_std_dev = df['std. dev.'].sum()
    
    print(cell.name , tally_result)
