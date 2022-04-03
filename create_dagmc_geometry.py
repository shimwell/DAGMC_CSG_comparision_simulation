import paramak

# makes a mode of a reactor with a rotation angle of 360 and default parameters elsewhere
# Link to a full list of parameters https://paramak.readthedocs.io/en/main/examples.html#flfsystemcodereactor
my_reactor = paramak.FlfSystemCodeReactor(
    rotation_angle=360,
    inner_blanket_radius = 100.,
    blanket_thickness = 70.,
    blanket_height = 500.,
    lower_blanket_thickness = 50.,
    upper_blanket_thickness = 40.,
    blanket_vv_gap = 20.,
    upper_vv_thickness = 10.,
    vv_thickness = 10.,
    lower_vv_thickness = 10.,
)


# creates a dagmc h5m file of the geometry with material tags automatically assigned
my_reactor.export_dagmc_h5m(filename="dagmc.h5m", min_mesh_size=5, max_mesh_size=20)
