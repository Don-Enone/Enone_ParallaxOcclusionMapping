import unreal
import json
import os

ROOT = os.path.join(unreal.Paths.project_saved_dir(), 'EnonePOM')
os.makedirs(ROOT, exist_ok=True)
fn = unreal.load_asset('/Game/TAcourse_III/Element/BaseElement/Enone_ParallaxOcclusionMapping')
assert fn
lib = unreal.MaterialEditingLibrary
assert lib.get_num_material_expressions_in_function(fn) == 124
for name in ['MaterialExpressionFunctionInput_0', 'MaterialExpressionFunctionInput_6',
             'MaterialExpressionStaticSwitch_1', 'MaterialExpressionStaticSwitch_3']:
    assert unreal.find_object(fn, name) is None, name

def get(name):
    result = unreal.find_object(fn, name)
    assert result, name
    return result

inspection_material = unreal.Material(name='EnonePOM_Inspection')
for target in ['MaterialExpressionComponentMask_8', 'MaterialExpressionComponentMask_9',
               'MaterialExpressionComponentMask_46', 'MaterialExpressionComponentMask_47',
               'MaterialExpressionFunctionOutput_0']:
    # UE4 requires a non-null Material, then reads expression inputs directly.
    inputs = lib.get_inputs_for_material_expression(inspection_material, get(target))
    assert len(inputs) == 1 and isinstance(inputs[0], unreal.MaterialExpressionCustom), target
    assert 'basisDet' in inputs[0].get_editor_property('code')

materials = []
for shadow in [False, True]:
    material = unreal.Material(name='EnonePOM_Compile_Shadow_' + str(shadow))
    material.set_editor_property('two_sided', True)
    call = lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall)
    assert call.set_material_function(fn)
    tex = lib.create_material_expression(material, unreal.MaterialExpressionTextureObject)
    tex.set_editor_property('texture', unreal.load_asset('/Engine/EngineResources/WhiteSquareTexture'))
    assert lib.connect_material_expressions(tex, '', call, 'Heightmap Texture')
    for pin, value in [('Height Ratio', 0.075), ('Min Steps', 8), ('Max Steps', 32)]:
        scalar = lib.create_material_expression(material, unreal.MaterialExpressionConstant)
        scalar.set_editor_property('r', value)
        assert lib.connect_material_expressions(scalar, '', call, pin)
    flag = lib.create_material_expression(material, unreal.MaterialExpressionStaticBool)
    flag.set_editor_property('value', shadow)
    assert lib.connect_material_expressions(flag, '', call, 'Render Shadows (Occlusion Mapping)')
    # Force all meaningful outputs into a compiled pixel shader.
    def red(result):
        mask = lib.create_material_expression(material, unreal.MaterialExpressionComponentMask)
        for channel in ['r', 'g', 'b', 'a']:
            mask.set_editor_property(channel, channel == 'r')
        assert lib.connect_material_expressions(call, result, mask, '')
        return mask
    acc = red('Parallax UVs')
    output = ''
    for result in ['Offset Only', 'Shadow', 'Material Complexity - Steps Debug', 'Tangent Light Vector', 'World Position', 'Pixel Depth Offset']:
        add = lib.create_material_expression(material, unreal.MaterialExpressionAdd)
        assert lib.connect_material_expressions(acc, output, add, 'A')
        assert lib.connect_material_expressions(red(result), '', add, 'B')
        acc, output = add, ''
    assert lib.connect_material_property(acc, output, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    lib.recompile_material(material)
    materials.append(material)
    unreal.log('ENONE_COMPILE_REQUESTED ' + material.get_path_name())

with open(ROOT + '/validation.json', 'w') as f:
    json.dump({'reload': True, 'legacy_modes_removed': True, 'direction_connections': 'pass',
               'compile_requested': [m.get_path_name() for m in materials]}, f, indent=2)
unreal.log('ENONE_VALIDATE_OK')
