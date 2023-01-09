import bpy
import os
import random
import sys

from functools import partial
from typing import Optional, Tuple

sys.path.append(os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-2]))
from configs.config import SeasyConfig


def create_displaced_candy(dimensions: Tuple[float] = (1, 1, 1), dimension_variability: float = 0.05,
                           strength: float = 0.2, strength_variability: float = 0.25, name: Optional[str] = None) -> None:
    """
    Exports a random bumpy sphere with specified dimensions
    :param dimensions: dimensions for the sphere
    :param dimension_variability: percentage of variation for dimensions
    :param strength: strength of the displacement modifier
    :param strength_variability: percentage of variation for strength
    :param name: name to save
    :return: None
    """

    dimensions = tuple([random.uniform(i*(1-dimension_variability), i*(1+dimension_variability)) for i in dimensions])

    # Create sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=1,
        location=(random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)),
        scale=dimensions
    )
    bpy.ops.object.shade_smooth()
    bpy.context.object.data.use_auto_smooth = True
    bpy.context.object.name = name.split(os.sep)[-1] if name else 'candy'

    # Random bumpiness with displacement modifier
    bpy.ops.object.modifier_add(type='DISPLACE')
    bpy.context.object.modifiers["Displace"].texture_coords = 'GLOBAL'
    bpy.context.object.modifiers["Displace"].strength = random.uniform(strength*(1-strength_variability), strength*(1+strength_variability))
    bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["rock_displacement"]

    # Center and export
    scale = dimensions[0]/bpy.context.object.dimensions[0]
    bpy.ops.wm.obj_export(filepath=name, check_existing=False, global_scale=scale, export_uv=False, export_materials=False)
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.wm.obj_import(filepath=name)
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
    bpy.context.object.location[0] = 0
    bpy.context.object.location[1] = 0
    bpy.context.object.location[2] = 0
    bpy.ops.wm.obj_export(filepath=name, check_existing=False, export_uv=False, export_materials=False)
    bpy.ops.object.delete(use_global=False, confirm=False)


def generate_obj_data(config: SeasyConfig) -> None:
    """
    Generate a dataset of obj files corresponding to 4 types of candies
    :param config: config to use for dataset creation
    :return: None
    """
    bpy.ops.mesh.add_mesh_rock()
    _ = [o.select_set(True) for o in bpy.data.objects]
    bpy.ops.object.delete(use_global=False, confirm=False)
    candies = {c: partial(create_displaced_candy, **config.classes[c]) for c in config.classes}
    for class_to_generate in ["mms", "mms_nut", "skittle", "bean"]:
        os.makedirs(os.path.join(config.obj_folder, class_to_generate), exist_ok=True)
        for sample in range(config.number_of_obj_per_class):
            file = os.path.join(config.obj_folder, class_to_generate,
                                class_to_generate + "_" + str(sample).zfill(len(str(config.number_of_obj_per_class-1))) + ".obj")
            arguments = {"name": file}
            if class_to_generate == "mms_nut":
                arguments["dimensions"] = (random.uniform(*config.mms_nut_dimension["x"]),
                                           config.mms_nut_dimension["y"], config.mms_nut_dimension["z"])
            candies[class_to_generate](**arguments)


if __name__ == "__main__":
    configuration = SeasyConfig.load_config()
    print(configuration.obj_creation.details())

    generate_obj_data(configuration.obj_creation)
