import brep_part_finder as bpf
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

my_reactor.export_brep('my_brep_file.brep')


my_brep_part_properties = bpf.get_brep_part_properties('my_brep_file.brep')

print(my_brep_part_properties)
