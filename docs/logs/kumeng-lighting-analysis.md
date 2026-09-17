# KumengScreen lighting breakdown (reviewed 2026-09-17)

Read the public main-branch source before changing our lighting. Main is mutable;
links below identify the reviewed files, not a pinned release. No reference code
or artwork is copied into this repository.

## What the source actually implements

The [scene shader](https://github.com/buger404/KumengScreen/blob/main/lib/scene-shader.ts)
uses color + registered normal data across the whole image. Linear reflectance
is multiplied by separate sky fill and directional key. A subtle rim, hair
reflection and iris reflection are additional terms. Face normals are filtered
and the face's light direction is artistically softened. This is a single scene
lighting draw, not independent shadow render targets.

[Stylized lighting](https://github.com/buger404/KumengScreen/blob/main/lib/stylized-lighting.ts)
organizes surfaces into two soft painted tones from normal/light facing. Main
light response varies strongly between those tones while the sky fill survives;
the dark tone also has a restrained cooler pigment. This mechanism acts on the
whole scene, not just a bright spot. Hair sheen is a separate material-local term.
There is no explicit contact AO texture, depth test or cast-shadow solver here.

[Daylight](https://github.com/buger404/KumengScreen/blob/main/lib/daylight.ts) changes
key direction, intensity/color and sky fill/color together with solar elevation.
Night has weak blue key/fill, not a local interior desk lamp. Our lamp visibility
cannot be obtained by copying this outdoor scene's night equations.

[Post processing](https://github.com/buger404/KumengScreen/blob/main/lib/post-processing.ts)
renders into one scene target, then executes four downsample/blur levels and a
composite. [Post shaders](https://github.com/buger404/KumengScreen/blob/main/lib/post-shaders.ts)
encode linear HDR in RGBM RGBA8, extract highlights, tone-map with ACES and apply
display grading. These extra passes soften bright energy; they do not construct
the primary shadows or recover missing contact geometry.

## Transfer decision

The plausible reason for stronger volume is whole-scene normal-driven tone
separation and a smaller fill/key ratio, supported by its purpose-made assets.
This is a source-based inference, not a controlled perceptual comparison.

Transfer the organization: independent environment, key, local reflection,
emission and visibility, with a shared soft form response and time state.
Keep our registered contact data, aperture, actual lamp location and corrected
window/sill masks. Apply contact occlusion to incident light instead of dimming
an already-combined sum. A blocked window must not dim lamp emission.

Do not migrate its artwork-specific face/hair masks, animation, cropping,
outdoor night model, four-level bloom or full renderer. Our already-lit artwork
also cannot be treated as clean albedo. Implement logical lighting layers inside
the existing fragment pass, with explicit diagnostics and no added FBO/texture.
