
import neutronics_material_maker as nmm
import openmc
import openmc_data_downloader as odd
import math



def run_neutronics_model(

):
    ind = input_neutronics_data
    imd = input_material_data
    igd = input_geometry_data

    # TODO consider adding units
    inner_blanket_radius = igd.inner_blanket_radius
    blanket_thickness = igd.blanket_thickness
    blanket_height = igd.blanket_height
    lower_blanket_thickness = igd.lower_blanket_thickness
    upper_blanket_thickness = igd.upper_blanket_thickness
    blanket_vv_gap = igd.blanket_vv_gap
    upper_vv_thickness = igd.upper_vv_thickness
    vv_thickness = igd.vv_thickness
    lower_vv_thickness = igd.lower_vv_thickness

    simulation_batches = ind.simulation_batches
    simulation_particles_per_batch = ind.simulation_particles_per_batch
    fractional_height_of_source = ind.fractional_height_of_source

    mat_blanket = nmm.Material.from_library(
        name=imd.blanket_material,
        enrichment=imd.lithium_enrichment,
        temperature=400,  # TODO expose temperatue to user args
        temperature_to_neutronics_code=False,
    ).openmc_material

    mat_vessel = nmm.Material.from_library(name=imd.vessel_material, temperature_to_neutronics_code=False).openmc_material

    materials = openmc.Materials([mat_blanket, mat_vessel])

    odd.just_in_time_library_generator(libraries=["ENDFB-7.1-NNDC", "TENDL-2019"], materials=materials, overwrite=False)

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
    vessel_cell_lower = openmc.Cell(region=vessel_lower_region)
    vessel_cell_upper = openmc.Cell(region=vessel_upper_region)
    vessel_cell_cylinder = openmc.Cell(region=vessel_region)
    vessel_cell_lower.fill = mat_vessel
    vessel_cell_upper.fill = mat_vessel
    vessel_cell_cylinder.fill = mat_vessel

    blanket_cell_cylinder = openmc.Cell(region=blanket_region)
    blanket_cell_upper = openmc.Cell(region=blanket_upper_region)
    blanket_cell_lower = openmc.Cell(region=blanket_lower_region)
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
    my_source.space = openmc.stats.Point((0, 0, 0))

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
    settings.seed = ind.seed

    tallies = openmc.Tallies()

    blanket_cell_filter = openmc.CellFilter([blanket_cell_cylinder, blanket_cell_lower, blanket_cell_upper])

    for cell in [
        vessel_cell_lower,
        vessel_cell_upper,
        vessel_cell_cylinder,
        blanket_cell_cylinder,
        blanket_cell_upper,
        blanket_cell_lower]:

        flux_tally = openmc.Tally(name=f"flux_{cell}")
        flux_tally.filters = [cell]
        flux_tally.scores = ["flux"]
        tallies.append(flux_tally)

    model = openmc.model.Model(geom, materials, settings, tallies)

    sp_filename = model.run()

    sp = openmc.StatePoint(sp_filename)

    for tally in sp.tallies:
        print(tally)
    # df = tbr_tally.get_pandas_dataframe()
    # tbr_tally_result = df["mean"].sum()

    # heating_tally = sp.get_tally(name="heating")
    # if ind.simulation_batches > 1:
    #     heating_tally_mev_pp, heating_tally_std_dev_mev_pp = otuc.process_tally(tally=heating_tally, required_units="megaelectron_volt")
    #     total_heating_tally_mev_pp = heating_tally_mev_pp.sum().magnitude
    # else:
    #     heating_tally_mev_pp = otuc.process_tally(tally=heating_tally, required_units="megaelectron_volt")
    #     total_heating_tally_mev_pp = heating_tally_mev_pp.sum().magnitude


    # return output_data


def volume_of_hollow_cylinder(
    outer_radius: float,
    height: float,
    inner_radius: float = 0,
):
    # = π (R2 - r2) h
    vol = math.pi * (math.pow(outer_radius, 2) - math.pow(inner_radius, 2)) * height
    return vol
