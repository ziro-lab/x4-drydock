#!/usr/bin/env python3
"""Build a simple modular ship blockout from a JSON spec.

The validator runs in normal CPython with no Blender dependency:

    python tools/build_modular_blockout.py ships/dx500_pilot/blockout_spec.json --validate-only

To create a .blend scene, run the same file through Blender:

    blender --background --python tools/build_modular_blockout.py -- \
      ships/dx500_pilot/blockout_spec.json \
      --output build/dx500_pilot_blockout.blend

The generated scene is intentionally a blockout. X4 Connections, final equipment
geometry, materials, UVs, collision, LODs, and runtime bindings are later gates.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Bounds:
    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]

    @property
    def size(self) -> tuple[float, float, float]:
        return tuple(self.maximum[i] - self.minimum[i] for i in range(3))


def _cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    return sys.argv[1:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate/build a modular ship blockout")
    parser.add_argument("spec", type=Path, help="Path to blockout JSON spec")
    parser.add_argument("--validate-only", action="store_true", help="Do not require Blender")
    parser.add_argument("--output", type=Path, help="Output .blend path")
    return parser.parse_args(_cli_argv())


def load_spec(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _vec3(value: Any, label: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{label} must be a 3-element list")
    result = tuple(float(v) for v in value)
    if not all(math.isfinite(v) for v in result):
        raise ValueError(f"{label} contains a non-finite value")
    return result


def item_bounds(center: Iterable[float], size: Iterable[float]) -> Bounds:
    c = tuple(float(v) for v in center)
    s = tuple(float(v) for v in size)
    return Bounds(
        tuple(c[i] - s[i] / 2.0 for i in range(3)),
        tuple(c[i] + s[i] / 2.0 for i in range(3)),
    )


def union_bounds(bounds: list[Bounds]) -> Bounds:
    if not bounds:
        raise ValueError("cannot union an empty bounds list")
    return Bounds(
        tuple(min(b.minimum[i] for b in bounds) for i in range(3)),
        tuple(max(b.maximum[i] for b in bounds) for i in range(3)),
    )


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if spec.get("units") != "m":
        errors.append("units must be 'm'")

    modules = spec.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("modules must be a non-empty list")
        modules = []

    seen: set[str] = set()
    module_bounds: list[Bounds] = []
    previous_max_x: float | None = None

    for i, module in enumerate(modules):
        name = str(module.get("name", ""))
        if not name:
            errors.append(f"modules[{i}] has no name")
            continue
        if name in seen:
            errors.append(f"duplicate name: {name}")
        seen.add(name)
        try:
            center = _vec3(module.get("center"), f"{name}.center")
            size = _vec3(module.get("size"), f"{name}.size")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if any(v <= 0.0 for v in size):
            errors.append(f"{name}.size must be positive")
            continue
        b = item_bounds(center, size)
        module_bounds.append(b)
        if previous_max_x is not None and b.minimum[0] < previous_max_x:
            warnings.append(f"module X ranges overlap before {name}; intentional overlap should be reviewed")
        previous_max_x = b.maximum[0]

    engines = spec.get("engines", [])
    if not isinstance(engines, list):
        errors.append("engines must be a list")
        engines = []
    for i, engine in enumerate(engines):
        name = str(engine.get("name", ""))
        if not name:
            errors.append(f"engines[{i}] has no name")
            continue
        if name in seen:
            errors.append(f"duplicate name: {name}")
        seen.add(name)
        try:
            _vec3(engine.get("center"), f"{name}.center")
            length = float(engine.get("length"))
            diameter = float(engine.get("diameter"))
        except (TypeError, ValueError) as exc:
            errors.append(f"invalid engine {name}: {exc}")
            continue
        if length <= 0.0 or diameter <= 0.0:
            errors.append(f"{name} length/diameter must be positive")

    docks = spec.get("dock_placeholders", [])
    if not isinstance(docks, list):
        errors.append("dock_placeholders must be a list")
        docks = []
    for i, dock in enumerate(docks):
        name = str(dock.get("name", ""))
        if not name:
            errors.append(f"dock_placeholders[{i}] has no name")
            continue
        if name in seen:
            errors.append(f"duplicate name: {name}")
        seen.add(name)
        try:
            _vec3(dock.get("center"), f"{name}.center")
            size = _vec3(dock.get("size"), f"{name}.size")
            _vec3(dock.get("approach_reserve_center"), f"{name}.approach_reserve_center")
            reserve_size = _vec3(dock.get("approach_reserve_size"), f"{name}.approach_reserve_size")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if any(v <= 0.0 for v in (*size, *reserve_size)):
            errors.append(f"{name} sizes must be positive")

    intent = spec.get("intent", {})
    try:
        target = _vec3(intent.get("target_hull_envelope_m"), "intent.target_hull_envelope_m")
    except ValueError as exc:
        errors.append(str(exc))
        target = (0.0, 0.0, 0.0)

    actual = (0.0, 0.0, 0.0)
    hull_bounds: Bounds | None = None
    if module_bounds:
        hull_bounds = union_bounds(module_bounds)
        actual = hull_bounds.size
        for axis, label in enumerate(("X/length", "Y/width", "Z/height")):
            if actual[axis] > target[axis] + 1e-6:
                errors.append(
                    f"module hull exceeds target envelope on {label}: {actual[axis]:.2f} > {target[axis]:.2f}"
                )
            elif target[axis] - actual[axis] > 30.0:
                warnings.append(
                    f"module hull under-fills target envelope on {label}: {actual[axis]:.2f} vs {target[axis]:.2f}"
                )

    if engines:
        yz = {(round(float(e["center"][1]), 6), round(float(e["center"][2]), 6)) for e in engines}
        mirror_missing = []
        for y, z in yz:
            if (-y, z) not in yz or (y, -z) not in yz:
                mirror_missing.append((y, z))
        if mirror_missing:
            warnings.append(f"engine cluster is not fully mirrored in Y/Z: {mirror_missing}")

    return {
        "ship_id": spec.get("ship_id"),
        "module_count": len(modules),
        "engine_count": len(engines),
        "dock_placeholder_count": len(docks),
        "target_hull_envelope_m": list(target),
        "actual_module_hull_envelope_m": [round(v, 3) for v in actual],
        "actual_module_hull_min_m": list(hull_bounds.minimum) if hull_bounds else None,
        "actual_module_hull_max_m": list(hull_bounds.maximum) if hull_bounds else None,
        "errors": errors,
        "warnings": warnings,
    }


def _ensure_collection(bpy: Any, name: str, parent: Any | None = None) -> Any:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    parent_collection = parent or bpy.context.scene.collection
    if collection.name not in {c.name for c in parent_collection.children}:
        parent_collection.children.link(collection)
    return collection


def _move_to_collection(obj: Any, collection: Any) -> None:
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def _add_box(bpy: Any, collection: Any, name: str, center: list[float], size: list[float], bevel: float = 0.0) -> Any:
    bpy.ops.mesh.primitive_cube_add(location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(float(v) / 2.0 for v in size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0.0:
        modifier = obj.modifiers.new(name="BlockoutBevel", type="BEVEL")
        modifier.width = min(bevel, min(float(v) for v in size) * 0.2)
        modifier.segments = 2
    _move_to_collection(obj, collection)
    return obj


def _add_cylinder_x(bpy: Any, collection: Any, name: str, center: list[float], length: float, diameter: float) -> Any:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24,
        radius=float(diameter) / 2.0,
        depth=float(length),
        location=center,
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    _move_to_collection(obj, collection)
    return obj


def _add_marker(bpy: Any, collection: Any, name: str, location: list[float]) -> Any:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "AXES"
    obj.empty_display_size = 12.0
    obj.location = location
    collection.objects.link(obj)
    return obj


def _look_at(obj: Any, target: tuple[float, float, float]) -> None:
    from mathutils import Vector

    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _add_camera(bpy: Any, collection: Any, name: str, location: tuple[float, float, float], ortho_scale: float | None) -> Any:
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    collection.objects.link(camera)
    camera.location = location
    _look_at(camera, (0.0, 0.0, 0.0))
    if ortho_scale is not None:
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = ortho_scale
    return camera


def build_blender_scene(spec: dict[str, Any], output: Path) -> None:
    try:
        import bpy
    except ImportError as exc:
        raise RuntimeError("Blender Python (bpy) is required unless --validate-only is used") from exc

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != bpy.context.scene.collection.name:
            bpy.data.collections.remove(collection)

    root = _ensure_collection(bpy, "DX500_PILOT")
    hull = _ensure_collection(bpy, "HULL_BLOCKOUT", root)
    structure = _ensure_collection(bpy, "STRUCTURE", root)
    equipment = _ensure_collection(bpy, "EQUIPMENT_PLACEHOLDER", root)
    reserved = _ensure_collection(bpy, "RESERVED_DEBUG", root)
    cameras = _ensure_collection(bpy, "DIAGNOSTIC_CAMERAS", root)

    modules = spec["modules"]
    for module in modules:
        obj = _add_box(
            bpy,
            hull,
            module["name"],
            module["center"],
            module["size"],
            float(module.get("bevel", 0.0)),
        )
        obj["purpose"] = module.get("purpose", "")
        obj["blockout_role"] = "module"

    connector = spec.get("connector_pattern", {})
    beam_y, beam_z = [float(v) for v in connector.get("beam_cross_section_m", [8.0, 8.0])]
    overlap = float(connector.get("overlap_into_module_m", 0.0))
    offsets = connector.get("beam_offsets_yz_m", [[0.0, 0.0]])

    for left, right in zip(modules, modules[1:]):
        left_max = float(left["center"][0]) + float(left["size"][0]) / 2.0
        right_min = float(right["center"][0]) - float(right["size"][0]) / 2.0
        span_min = left_max - overlap
        span_max = right_min + overlap
        span = span_max - span_min
        if span <= 0.0:
            continue
        center_x = (span_min + span_max) / 2.0
        for beam_index, (y, z) in enumerate(offsets, start=1):
            _add_box(
                bpy,
                structure,
                f"TRUSS_{left['name']}_{right['name']}_{beam_index:02d}",
                [center_x, float(y), float(z)],
                [span, beam_y, beam_z],
                0.5,
            )

    for engine in spec.get("engines", []):
        obj = _add_cylinder_x(
            bpy,
            equipment,
            engine["name"],
            engine["center"],
            float(engine["length"]),
            float(engine["diameter"]),
        )
        obj["blockout_role"] = "engine_placeholder"

        reserve_obj = _add_cylinder_x(
            bpy,
            reserved,
            f"RESERVE_{engine['name']}",
            engine["center"],
            float(engine["clearance_snapshot"][0]),
            float(engine["clearance_snapshot"][1]),
        )
        reserve_obj.display_type = "WIRE"
        reserve_obj.hide_render = True
        reserve_obj["authority_note"] = "snapshot only; re-read current Blender_Properties.xml before Layout Freeze"

    for dock in spec.get("dock_placeholders", []):
        dock_obj = _add_box(bpy, equipment, dock["name"], dock["center"], dock["size"], 1.0)
        dock_obj["blockout_role"] = "dock_placeholder"
        dock_obj["note"] = dock.get("note", "")
        reserve_obj = _add_box(
            bpy,
            reserved,
            f"RESERVE_{dock['name']}_APPROACH",
            dock["approach_reserve_center"],
            dock["approach_reserve_size"],
            0.0,
        )
        reserve_obj.display_type = "WIRE"
        reserve_obj.hide_render = True
        reserve_obj["authority_note"] = "conceptual design reserve, not an Egosoft visualization value"

    for marker in spec.get("markers", []):
        _add_marker(bpy, reserved, marker["name"], marker["location"])

    _add_camera(bpy, cameras, "CAM_TOP", (0.0, 0.0, 700.0), 650.0)
    _add_camera(bpy, cameras, "CAM_SIDE", (0.0, -700.0, 0.0), 650.0)
    _add_camera(bpy, cameras, "CAM_FRONT", (-700.0, 0.0, 0.0), 430.0)
    _add_camera(bpy, cameras, "CAM_PERSPECTIVE", (-620.0, -520.0, 360.0), None)

    bpy.context.scene["ship_id"] = spec.get("ship_id", "")
    bpy.context.scene["blockout_schema_version"] = int(spec.get("schema_version", 1))
    bpy.context.scene["x4_layout_state"] = "BLOCKOUT_BASELINE_CANDIDATE"

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    print(f"Saved blockout: {output}")


def main() -> int:
    args = parse_args()
    spec = load_spec(args.spec)
    summary = validate_spec(spec)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if summary["errors"]:
        return 2
    if args.validate_only:
        return 0

    output = args.output or args.spec.with_name(f"{spec.get('ship_id', 'ship')}_blockout.blend")
    build_blender_scene(spec, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
