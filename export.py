bl_info = {
    "name": "TalkingHead Pose Exporter",
    "author": "Andrea Santaniello",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Object",
    "description": "Exports pose templates for TalkingHead",
    "category": "Import-Export",
}

import bpy
import json
from bpy_extras.io_utils import ExportHelper
from bpy.props import BoolProperty, StringProperty

def get_pose_data(obj):
    pose_data = {}
    for bone in obj.pose.bones:
        bone_name = bone.name

        # Get the bone's matrix relative to the armature
        mat = obj.matrix_world @ bone.matrix
        loc, rot, scale = mat.decompose()
        euler = rot.to_euler('XYZ')

        # For the 'Hips' bone, include position
        if bone_name == 'Hips':
            pose_data[f'{bone_name}.position'] = {
                'x': round(loc.x, 3),
                'y': round(loc.y, 3),
                'z': round(loc.z, 3)
            }

        # Collect rotation data
        pose_data[f'{bone_name}.rotation'] = {
            'x': round(euler.x, 3),
            'y': round(euler.y, 3),
            'z': round(euler.z, 3)
        }
    return pose_data

def format_pose_template(pose_name, pose_data, attributes):
    # Format the attributes into the required string
    attrs_str = ', '.join([f'{key}: {str(value).lower()}' for key, value in attributes.items()])
    return f"""
    '{pose_name}': {{
      {attrs_str},
      props: {json.dumps(pose_data, indent=2)}
    }},
    """

class TalkingHeadPoseExporterOperator(bpy.types.Operator, ExportHelper):
    """Export Pose Templates for TalkingHead with Save As dialog"""
    bl_idname = "export.talkinghead_pose"
    bl_label = "Export TalkingHead Pose"

    filename_ext = ".js"

    # Operator properties for boolean attributes
    standing: BoolProperty(
        name="Standing",
        description="Is the pose standing?",
        default=False,
    )
    sitting: BoolProperty(
        name="Sitting",
        description="Is the pose sitting?",
        default=False,
    )
    bend: BoolProperty(
        name="Bend",
        description="Is the pose bending?",
        default=False,
    )
    kneeling: BoolProperty(
        name="Kneeling",
        description="Is the pose kneeling?",
        default=False,
    )
    lying: BoolProperty(
        name="Lying",
        description="Is the pose lying down?",
        default=False,
    )

    pose_name: StringProperty(
        name="Pose Name",
        description="Name of the pose",
        default="custom_pose",
    )

    def execute(self, context):
        obj = context.active_object

        if obj is None or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}

        # Collect attributes
        attributes = {
            'standing': self.standing,
            'sitting': self.sitting,
            'bend': self.bend,
            'kneeling': self.kneeling,
            'lying': self.lying
        }

        pose_data = get_pose_data(obj)
        pose_template = format_pose_template(self.pose_name, pose_data, attributes)

        # Save to the selected file
        with open(self.filepath, 'a') as f:
            f.write(pose_template)

        self.report({'INFO'}, f"Pose template '{self.pose_name}' exported to {self.filepath}")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        # Pose name
        layout.prop(self, "pose_name")

        # Boolean attributes
        layout.label(text="Pose Attributes:")
        row = layout.row()
        row.prop(self, "standing")
        row.prop(self, "sitting")
        row.prop(self, "bend")
        row.prop(self, "kneeling")
        row.prop(self, "lying")

def menu_func(self, context):
    self.layout.operator(TalkingHeadPoseExporterOperator.bl_idname, text="Export TalkingHead Pose")

def register():
    bpy.utils.register_class(TalkingHeadPoseExporterOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(TalkingHeadPoseExporterOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
