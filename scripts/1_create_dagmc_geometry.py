import paramak

# makes a mode of a reactor with a rotation angle of 360 and default parameters elsewhere
# Link to a full list of parameters https://paramak.readthedocs.io/en/main/examples.html#flfsystemcodereactor
my_reactor = paramak.FlfSystemCodeReactor(
    rotation_angle=360,
    inner_blanket_radius=100.0,
    blanket_thickness=70.0,
    blanket_height=500.0,
    lower_blanket_thickness=50.0,
    upper_blanket_thickness=40.0,
    blanket_vv_gap=20.0,
    upper_vv_thickness=10.0,
    vv_thickness=10.0,
    lower_vv_thickness=10.0,
)


# creates a dagmc h5m file of the geometry with material tags automatically assigned
# exports the mesh in several sizes.
for mesh_size in [100, 10]:

    # makes a DAGMC with tags suitable for OpenMC and no graveyard
    my_reactor.export_dagmc_h5m(
        filename=f"dagmc_{mesh_size}_openmc.h5m",
        min_mesh_size=mesh_size,
        max_mesh_size=mesh_size,
    )

    # makes the DAGMC geometry with tags suitable for Shift and with a graveyard
    my_reactor.export_dagmc_h5m(
        filename=f"dagmc_{mesh_size}_shift.h5m",
        tags=[
            "1",  # blanket
            "2",  # vessel
            "3",  # upper_blanket
            "4",  # lower_blanket
            "5",  # lower_vessel
            "6",  # upper_vessel
            "graveyard",
        ],
        include_graveyard={
            "offset": 10
        },  # manually sets the graveyard offset from the largest component
        min_mesh_size=mesh_size,
        max_mesh_size=mesh_size,
    )
