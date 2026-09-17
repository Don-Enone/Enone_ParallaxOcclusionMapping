"""Run using UE 4.26 PythonScript commandlet; creates only the new function."""
import json
import os
import unreal

ROOT = os.path.join(unreal.Paths.project_saved_dir(), 'EnonePOM')
os.makedirs(ROOT, exist_ok=True)
SOURCE = '/Engine/Functions/Engine_MaterialFunctions01/Texturing/ParallaxOcclusionMapping'
DEST = '/Game/TAcourse_III/Element/BaseElement/Enone_ParallaxOcclusionMapping'
lib = unreal.MaterialEditingLibrary
assert not unreal.EditorAssetLibrary.does_asset_exist(DEST), 'Refusing to overwrite existing asset'
source = unreal.load_asset(SOURCE)
assert source
fn = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(
    'Enone_ParallaxOcclusionMapping', '/Game/TAcourse_III/Element/BaseElement', source)
assert fn

def node(name):
    result = unreal.find_object(fn, name)
    assert result, name
    return result

def connect(a, b, pin, output=''):
    assert lib.connect_material_expressions(a, output, b, pin), (a.get_name(), b.get_name(), pin)

def make(cls, x, y):
    return lib.create_material_expression_in_function(fn, cls, x, y)

# The original World->Tangent path is valid for unmodified mesh UV0. Its
# normal-only world-coordinate basis cannot recover roll around that normal,
# and neither legacy path follows arbitrary rotated/mirrored input UVs.
# Reconstruct the axes of the ACTUAL input UV field from screen derivatives.
# Degenerate UVs produce zero lateral offset. Derivatives are evaluated
# before ray marching, and never depend on the displaced UV output.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frame_optimized.hlsl'), encoding='utf-8') as shader_file:
    FRAME_CODE = shader_file.read()

uv = node('MaterialExpressionFunctionInput_10')
pos = node('MaterialExpressionWorldPosition_4')
normal = node('MaterialExpressionVertexNormalWS_0')
uvdx = make(unreal.MaterialExpressionDDX, -2400, -1500)
uvdy = make(unreal.MaterialExpressionDDY, -2400, -1350)
pdx = make(unreal.MaterialExpressionDDX, -2400, -1200)
pdy = make(unreal.MaterialExpressionDDY, -2400, -1050)
for src, dst in [(uv, uvdx), (uv, uvdy), (pos, pdx), (pos, pdy)]:
    connect(src, dst, 'Value')

def frame(vector, y, label, camera=False):
    custom = make(unreal.MaterialExpressionCustom, -2000, y)
    custom.set_editor_property('description', label)
    custom.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    ending = 'return result;'
    if camera:
        ending = 'result.z = (result.z < 0 ? -1 : 1) * max(abs(result.z), 1e-4); return result;'
    custom.set_editor_property('code', FRAME_CODE.replace('RETURN_RESULT', ending))
    sources = [('VectorWS', vector), ('NormalWS', normal), ('Pdx', pdx),
               ('Pdy', pdy), ('UVdx', uvdx), ('UVdy', uvdy)]
    inputs = []
    for name, _ in sources:
        inp = unreal.CustomInput()
        inp.set_editor_property('input_name', name)
        inputs.append(inp)
    custom.set_editor_property('inputs', inputs)
    for name, src in sources:
        connect(src, custom, name)
    return custom

camera = frame(node('MaterialExpressionCameraVectorWS_9'), -1600,
               'Enone: camera in actual UV frame', camera=True)
connect(camera, node('MaterialExpressionComponentMask_8'), '')
connect(camera, node('MaterialExpressionComponentMask_9'), '')
light = frame(node('MaterialExpressionMultiply_56'), -1100,
              'Enone: light in same UV frame')
connect(light, node('MaterialExpressionComponentMask_46'), '')
connect(light, node('MaterialExpressionComponentMask_47'), '')
connect(light, node('MaterialExpressionFunctionOutput_0'), '')

fn.set_editor_property('description',
    'Enone POM: optimized automatic UV frame for object rotation, rotated/mirrored and sheared UVs. '
    'Automatic UV frame only; no legacy coordinate mode. Degenerate UVs suppress lateral parallax. '
    'Based on UE4.26 ParallaxOcclusionMapping; original height ratio, ray marching, PDO and quality fallbacks retained.')
obsolete = ['MaterialExpressionFunctionInput_0', 'MaterialExpressionFunctionInput_6',
            'MaterialExpressionStaticSwitch_1', 'MaterialExpressionStaticSwitch_3',
            'MaterialExpressionMaterialFunctionCall_0', 'MaterialExpressionStaticBool_1',
            'MaterialExpressionStaticBool_2', 'MaterialExpressionTransform_4',
            'MaterialExpressionTransform_18']
for name in obsolete:
    lib.delete_material_expression_in_function(fn, node(name))
for name in ['MaterialExpressionCustom_20', 'MaterialExpressionCustom_21']:
    custom = node(name)
    custom.set_editor_property('code', custom.get_editor_property('code').replace(
        'float yintersect;', 'float yintersect=0;'))
lib.update_material_function(fn)
assert lib.get_num_material_expressions_in_function(fn) == lib.get_num_material_expressions_in_function(source) + 6 - len(obsolete)
assert unreal.EditorAssetLibrary.save_loaded_asset(fn, only_if_is_dirty=False)
with open(os.path.join(ROOT, 'creation.json'), 'w') as f:
    json.dump({'asset': fn.get_path_name(), 'source': source.get_path_name(),
               'expressions': lib.get_num_material_expressions_in_function(fn),
               'added_nodes': 6, 'removed_nodes': obsolete, 'status': 'saved'}, f, indent=2)
unreal.log('ENONE_CREATE_OK ' + fn.get_path_name())
