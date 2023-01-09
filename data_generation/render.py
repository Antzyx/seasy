import blenderproc as bproc
from blenderproc.python.types.MaterialUtility import Material

import os
from random import sample, randint
import sys

import bpy
import numpy as np
from typing import List, Union, Dict, Optional

sys.path.append(os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-2]))
from configs.config import SeasyConfig


def get_all_candies(obj_folder: str) -> List[str]:
    """
    Get the paths to all the candies generated with the candy_generator_script.
    :param obj_folder: path to the folder where the candies were generated
    :return: list of paths to the candies
    """
    candies = []
    for folder in [i for i in os.listdir(obj_folder) if "." not in i]:
        candies += [os.path.join(obj_folder, folder, i)
                    for i in os.listdir(os.path.join(obj_folder, folder))
                    if i.endswith(".obj")]
    return candies


def make_light(config: SeasyConfig) -> None:
    """
    Create as many sources of light as there were energies defined in the config file.
    :param config: sub-config used to define light sources (see config.image_rendering.light)
    """
    for energy in config.energy:
        light = bproc.types.Light()
        light.set_type(config.type)
        light.set_location(bproc.sampler.shell(
            center=config.shell_center,
            radius_min=config.shell_radius[0],
            radius_max=config.shell_radius[1],
            elevation_min=config.shell_elevation[0],
            elevation_max=config.shell_elevation[1]
        ))
        light.set_energy(energy)


def new_bsdf(name: str = '', image: Optional[str] = None, colour: Optional[List[float]] = None, specularity: float = 0.5,
             metalness: float = 0) -> Material:
    """
    Creates a new blender material with given parameters and texture, and return the corresponding blenderproc material.
    :param name: name for the blender material
    :param image: if an image would be used as texture, path to that image
    :param colour: if a colour would be used as texture, [R, G, B] for that colour (values between 0 and 1)
    :param specularity: specular component of the BSDF, between 0 and 1
    :param metalness: metallic component of the BSDF, between 0 and 1
    :return: returns the created Material
    """
    if image is None and colour is None:
        colour = [1, 1, 1, 1]
    new_material = bpy.data.materials.new(name=name)
    new_material.use_nodes = True
    if image is None:
        hsv = new_material.node_tree.nodes.new("ShaderNodeHueSaturation")
        new_material.node_tree.links.new(new_material.node_tree.nodes["Principled BSDF"].inputs['Base Color'],
                                         hsv.outputs['Color'])
        print(list(new_material.node_tree.nodes))
        new_material.node_tree.nodes["Hue Saturation Value"].inputs[4].default_value = (0, 1, 0, 1)
        new_material.node_tree.nodes["Hue Saturation Value"].inputs[0].default_value = colour[0]
        new_material.node_tree.nodes["Hue Saturation Value"].inputs[1].default_value = colour[1]
        new_material.node_tree.nodes["Hue Saturation Value"].inputs[2].default_value = colour[2]
    else:
        texture_image = new_material.node_tree.nodes.new('ShaderNodeTexImage')
        texture_image.image = bpy.data.images.load(image)
        new_material.node_tree.links.new(new_material.node_tree.nodes["Principled BSDF"].inputs['Base Color'],
                                         texture_image.outputs['Color'])
    new_material.node_tree.nodes["Principled BSDF"].inputs[6].default_value = metalness
    new_material.node_tree.nodes["Principled BSDF"].inputs[7].default_value = specularity
    return Material(new_material)


def make_materials(config: SeasyConfig, image_path: str, number_of_candies: int) -> Dict:
    """
    Creates the materials required for the scene to render
    :param config: config for the candies' material (see config.image_rendering.candies)
    :param image_path: image for the tabletop texture
    :param number_of_candies: number of candies to create
    :return: dictionary of the created materials
    """
    return {
        "candies": [new_bsdf(name=f"candy_{i}",
                             colour=[np.random.uniform(*config.hue),
                                     np.random.uniform(*config.saturation),
                                     np.random.uniform(*config.value)],
                             specularity=np.random.uniform(*config.specularity),
                             metalness=np.random.uniform(*config.metalness)) for i in range(number_of_candies)],
        "ground": new_bsdf(name="ground", image=image_path,
                           specularity=np.random.uniform(*config.specularity), metalness=np.random.uniform(*config.metalness)),
    }


def make_scene(config: SeasyConfig, candies: List[str], materials: Dict[str, Union[List[Material], Material]]
               ) -> None:
    """
    Creates a scene using specified candies with given materials. In particular, loads and places the objects in the scene.
    :param config: config to use to generate the scene
    :param candies: candies to place in the scene
    :param materials: materials to use for the candies
    """
    scene_objects = {
        "candies": [],
        "ground": bproc.loader.load_obj(os.path.join(config.obj_creation.obj_folder, "ground.obj"))[0],
    }
    for candy in candies:
        scene_objects["candies"].append(bproc.loader.load_obj(candy)[0])
        scene_objects["candies"][-1].set_cp("category_id", 1 + list(config.obj_creation.classes.keys()).index(candy.split(os.path.sep)[-2]))
    for index, obj in enumerate(scene_objects["candies"]):
        obj.set_location(np.random.uniform(*config.image_rendering.candies.location))
        # obj.set_location(bproc.sampler.upper_region(objects_to_sample_on=scene_objects["ground"]))
        obj.set_rotation_euler(bproc.sampler.uniformSO3())
        obj.enable_rigidbody(active=True)
        obj.set_shading_mode("auto", 45)
        obj.add_material(materials["candies"][index])
    scene_objects["ground"].enable_rigidbody(active=False, collision_shape="MESH")
    scene_objects["ground"].set_cp("category_id", 0)
    scene_objects["ground"].add_material(materials["ground"])
    bproc.object.simulate_physics_and_fix_final_poses(min_simulation_time=1, max_simulation_time=3, check_object_interval=1)


def render_all(config: SeasyConfig) -> None:
    """
    Render all images specified in the config
    :param config: config used to render
    """
    candies = get_all_candies(config.obj_creation.obj_folder)
    backgrounds = [len(os.listdir(os.path.join(config.image_rendering.pass_path, i))) for i in os.listdir(config.image_rendering.pass_path)]
    for _ in range(config.image_rendering.number_of_images):
        render_one(config, candies, backgrounds)


def render_one(config: SeasyConfig, all_candies: List[str], backgrounds: List[int]) -> None:
    """
    Renders one image using given config.
    :param config: config to use for rendering
    :param all_candies: all candies created by the candy_generator_script
    :param backgrounds: list of number of backgrounds in each sub-folder of the PASS dataset
    """
    bproc.clean_up(clean_up_camera=True)
    candies_to_use = sample(all_candies, randint(*config.image_rendering.number_of_candies_per_scene))
    image_index_to_use = randint(0, sum(backgrounds))
    image_to_use = None
    for i in range(len(backgrounds)):
        if sum(backgrounds[:i+1]) > image_index_to_use:
            index = image_index_to_use - (0 if not i else sum(backgrounds[:i]))
            folder = os.listdir(config.image_rendering.pass_path)[i]
            image_to_use = os.path.join(config.image_rendering.pass_path, folder,
                                        os.listdir(os.path.join(config.image_rendering.pass_path, folder))[index])
            break
    materials = make_materials(config.image_rendering.candies, image_to_use, len(candies_to_use))
    make_scene(config, candies_to_use, materials)
    make_light(config.image_rendering.light)
    set_camera(config.image_rendering.camera)
    bproc.renderer.enable_segmentation_output(map_by=["category_id", "name", "instance"])
    data = bproc.renderer.render()
    bproc.writer.write_coco_annotations(os.path.join(config.image_rendering.render_path, 'coco_data'),
                                        supercategory="coco_annotations",
                                        instance_segmaps=data["instance_segmaps"],
                                        instance_attribute_maps=data["instance_attribute_maps"],
                                        colors=data["colors"],
                                        color_file_format="JPEG",
                                        append_to_existing_output=True)


def set_camera(config: SeasyConfig) -> None:
    """
    Camera setup for rendering.
    :param config: sub-config to use to setup the camera (see config.image_rendering.camera)
    """
    location = np.random.uniform(*config.location)
    point_of_interest = [0, 0, -1]
    rotation_matrix = bproc.camera.rotation_from_forward_vec(point_of_interest - location, inplane_rot=np.random.uniform(-0.7854, 0.7854))
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)


if __name__ == "__main__":
    configuration = SeasyConfig.load_config()
    bproc.init()
    render_all(configuration)
