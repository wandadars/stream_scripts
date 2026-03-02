from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _import_gmsh():
    try:
        import gmsh  # type: ignore

        return gmsh
    except ModuleNotFoundError:
        pass

    script_dir = Path(__file__).resolve().parent
    local_lib = script_dir / "gmsh_env" / "lib"
    for site_packages in sorted(local_lib.glob("python*/site-packages")):
        sys.path.insert(0, str(site_packages))
        try:
            import gmsh  # type: ignore

            return gmsh
        except ModuleNotFoundError:
            sys.path.pop(0)

    raise ModuleNotFoundError(
        "Could not import 'gmsh'. Install the Gmsh Python module, or run with the "
        "Gmsh-provided Python, or provide a local 'gmsh_env' next to this script."
    )


gmsh = _import_gmsh()

def sync_any():
    # Works whether you used the built-in GEO kernel or OpenCASCADE
    geo_err = occ_err = None
    try:
        gmsh.model.geo.synchronize()
        geo_err = None
    except Exception as exc:
        geo_err = exc
    try:
        gmsh.model.occ.synchronize()
        occ_err = None
    except Exception as exc:
        occ_err = exc

    if geo_err is not None and occ_err is not None:
        raise RuntimeError("Failed to synchronize both GEO and OpenCASCADE kernels") from geo_err


def _extrude_surfaces_z(dimtags_2d: list[tuple[int, int]], dz: float) -> list[tuple[int, int]]:
    def _try_extrude_once() -> list[tuple[int, int]]:
        # Try GEO first, then OCC. This keeps the script kernel-agnostic.
        geo_err = occ_err = None
        try:
            out = gmsh.model.geo.extrude(dimtags_2d, 0.0, 0.0, dz)
            gmsh.model.geo.synchronize()
            return out
        except Exception as exc:
            geo_err = exc

        try:
            out = gmsh.model.occ.extrude(dimtags_2d, 0.0, 0.0, dz)
            gmsh.model.occ.synchronize()
            return out
        except Exception as exc:
            occ_err = exc

        raise RuntimeError(
            "Could not extrude with either GEO or OpenCASCADE kernels."
        ) from (geo_err if geo_err is not None else occ_err)

    try:
        return _try_extrude_once()
    except RuntimeError as first_err:
        # Common with pure mesh inputs (.msh): no CAD representation exists yet.
        try:
            gmsh.model.mesh.createGeometry()
            sync_any()
        except Exception:
            raise first_err
        return _try_extrude_once()


def _remove_surface_groups_by_name(names: set[str]) -> None:
    to_remove: list[tuple[int, int]] = []
    for _d, ptag in gmsh.model.getPhysicalGroups(dim=2):
        nm = gmsh.model.getPhysicalName(2, ptag)
        if nm in names:
            to_remove.append((2, ptag))
    if to_remove:
        gmsh.model.removePhysicalGroups(to_remove)


def _next_free_surface_tag(reserved: set[int]) -> int:
    used = {ptag for _d, ptag in gmsh.model.getPhysicalGroups(dim=2)}
    candidate = 1
    while candidate in used or candidate in reserved:
        candidate += 1
    return candidate


def _add_named_surface_group(
    surface_tags: list[int],
    name: str,
    reserved_tags: set[int],
) -> int | None:
    unique = sorted(set(surface_tags))
    if not unique:
        return None
    ptag = _next_free_surface_tag(reserved_tags)
    gmsh.model.addPhysicalGroup(2, unique, tag=ptag)
    gmsh.model.setPhysicalName(2, ptag, name)
    print(f"Physical Surface '{name}' (tag {ptag}): {len(unique)} surface(s)")
    return ptag


def _polygon_area_xy(conn: tuple[int, ...], xyz: dict[int, tuple[float, float, float]]) -> float:
    area2 = 0.0
    n = len(conn)
    for i in range(n):
        x1, y1, _ = xyz[conn[i]]
        x2, y2, _ = xyz[conn[(i + 1) % n]]
        area2 += x1 * y2 - x2 * y1
    return 0.5 * area2


def _normalize_ccw(conn: tuple[int, ...], xyz: dict[int, tuple[float, float, float]]) -> tuple[int, ...]:
    if _polygon_area_xy(conn, xyz) < 0.0:
        return tuple(reversed(conn))
    return conn


def _collect_nodes_xyz() -> dict[int, tuple[float, float, float]]:
    node_tags, coords, _param = gmsh.model.mesh.getNodes()
    if not node_tags:
        return {}
    xyz: dict[int, tuple[float, float, float]] = {}
    for i, ntag in enumerate(node_tags):
        xyz[int(ntag)] = (coords[3 * i], coords[3 * i + 1], coords[3 * i + 2])
    return xyz


def _collect_surface_elements() -> dict[int, list[tuple[int, tuple[int, ...]]]]:
    # surfaceTag -> [(etype, conn), ...], supports linear tri/quad only
    out: dict[int, list[tuple[int, tuple[int, ...]]]] = {}
    for _d, stag in gmsh.model.getEntities(dim=2):
        types, _elem_tags_vec, node_tags_vec = gmsh.model.mesh.getElements(2, stag)
        elems: list[tuple[int, tuple[int, ...]]] = []
        for etype, conn_vec in zip(types, node_tags_vec):
            if etype not in (2, 3):
                raise ValueError(
                    f"Unsupported 2D element type {etype} on surface {stag}. "
                    "Only linear triangles (2) and quads (3) are supported for .msh extrusion."
                )
            nper = 3 if etype == 2 else 4
            for i in range(0, len(conn_vec), nper):
                conn = tuple(int(v) for v in conn_vec[i : i + nper])
                elems.append((int(etype), conn))
        if elems:
            out[int(stag)] = elems
    return out


def _collect_curve_line_elements(curve_tags: set[int]) -> dict[int, list[tuple[int, int]]]:
    # curveTag -> [(n1, n2), ...], supports linear line elements only
    out: dict[int, list[tuple[int, int]]] = {}
    for ctag in sorted(curve_tags):
        types, _elem_tags_vec, node_tags_vec = gmsh.model.mesh.getElements(1, ctag)
        line_pairs: list[tuple[int, int]] = []
        for etype, conn_vec in zip(types, node_tags_vec):
            if etype != 1:
                raise ValueError(
                    f"Unsupported 1D element type {etype} on curve {ctag}. "
                    "Only linear line elements (1) are supported for .msh extrusion."
                )
            for i in range(0, len(conn_vec), 2):
                line_pairs.append((int(conn_vec[i]), int(conn_vec[i + 1])))
        if line_pairs:
            out[int(ctag)] = line_pairs
    return out


def _extrude_2d_msh_direct(
    out_msh: str,
    *,
    dz: float,
    back_surface_name: str,
    front_surface_name: str,
) -> int:
    phys_curves = gmsh.model.getPhysicalGroups(dim=1)
    if not phys_curves:
        print("No Physical Curve groups (dim=1) found in input .msh.")
        return 2

    ptag_to_name: dict[int, str] = {}
    ptag_to_curves: dict[int, list[int]] = {}
    for _d, ptag in phys_curves:
        ptag_to_name[ptag] = gmsh.model.getPhysicalName(1, ptag) or f"curve_group_{ptag}"
        ptag_to_curves[ptag] = list(gmsh.model.getEntitiesForPhysicalGroup(1, ptag))

    curve_tags_in_phys = {ctag for curves in ptag_to_curves.values() for ctag in curves}
    xyz = _collect_nodes_xyz()
    if not xyz:
        print("Input mesh has no nodes.")
        return 3

    surf_elems = _collect_surface_elements()
    if not surf_elems:
        print("No 2D elements found to extrude.")
        return 3

    curve_line_elems = _collect_curve_line_elements(curve_tags_in_phys)
    if not curve_line_elems:
        print("No boundary line elements found on Physical Curves.")
        return 3

    base_node_tags = sorted(xyz)
    max_node_tag = max(base_node_tags)
    top_node_of = {ntag: ntag + max_node_tag for ntag in base_node_tags}

    all_node_tags: list[int] = []
    all_coords: list[float] = []
    for ntag in base_node_tags:
        x, y, z = xyz[ntag]
        all_node_tags.append(ntag)
        all_coords.extend([x, y, z])
    for ntag in base_node_tags:
        x, y, z = xyz[ntag]
        all_node_tags.append(top_node_of[ntag])
        all_coords.extend([x, y, z + dz])

    gmsh.clear()
    gmsh.model.add("extruded")

    next_surf_tag = 1
    back_surf_of: dict[int, int] = {}
    front_surf_of: dict[int, int] = {}
    side_surf_of: dict[int, int] = {}

    for stag in sorted(surf_elems):
        back_surf_of[stag] = next_surf_tag
        gmsh.model.addDiscreteEntity(2, next_surf_tag)
        next_surf_tag += 1

    for stag in sorted(surf_elems):
        front_surf_of[stag] = next_surf_tag
        gmsh.model.addDiscreteEntity(2, next_surf_tag)
        next_surf_tag += 1

    for ctag in sorted(curve_line_elems):
        side_surf_of[ctag] = next_surf_tag
        gmsh.model.addDiscreteEntity(2, next_surf_tag)
        next_surf_tag += 1

    volume_tag = 1
    all_surface_tags = sorted(
        set(back_surf_of.values()).union(front_surf_of.values()).union(side_surf_of.values())
    )
    gmsh.model.addDiscreteEntity(3, volume_tag, all_surface_tags)

    gmsh.model.mesh.addNodes(3, volume_tag, all_node_tags, all_coords)

    # Add back/front caps and build volume cells.
    vol_prism_nodes: list[int] = []
    vol_hex_nodes: list[int] = []
    for orig_stag, elems in surf_elems.items():
        back_tri_nodes: list[int] = []
        back_quad_nodes: list[int] = []
        front_tri_nodes: list[int] = []
        front_quad_nodes: list[int] = []

        for etype, raw_conn in elems:
            conn = _normalize_ccw(raw_conn, xyz)
            top_conn = tuple(top_node_of[n] for n in conn)

            if etype == 2:
                front_tri_nodes.extend(top_conn)
                back_tri_nodes.extend(tuple(reversed(conn)))
                vol_prism_nodes.extend((*conn, *top_conn))
            elif etype == 3:
                front_quad_nodes.extend(top_conn)
                back_quad_nodes.extend(tuple(reversed(conn)))
                vol_hex_nodes.extend((*conn, *top_conn))

        back_tag = back_surf_of[orig_stag]
        front_tag = front_surf_of[orig_stag]
        if back_tri_nodes:
            gmsh.model.mesh.addElementsByType(back_tag, 2, [], back_tri_nodes)
        if back_quad_nodes:
            gmsh.model.mesh.addElementsByType(back_tag, 3, [], back_quad_nodes)
        if front_tri_nodes:
            gmsh.model.mesh.addElementsByType(front_tag, 2, [], front_tri_nodes)
        if front_quad_nodes:
            gmsh.model.mesh.addElementsByType(front_tag, 3, [], front_quad_nodes)

    # Add side quads from boundary line extrusion.
    for ctag, line_pairs in curve_line_elems.items():
        side_quad_nodes: list[int] = []
        for n1, n2 in line_pairs:
            side_quad_nodes.extend([n1, n2, top_node_of[n2], top_node_of[n1]])
        if side_quad_nodes:
            gmsh.model.mesh.addElementsByType(side_surf_of[ctag], 3, [], side_quad_nodes)

    if vol_prism_nodes:
        gmsh.model.mesh.addElementsByType(volume_tag, 6, [], vol_prism_nodes)
    if vol_hex_nodes:
        gmsh.model.mesh.addElementsByType(volume_tag, 5, [], vol_hex_nodes)

    # Surface physicals from original Physical Curves keep same tags and names.
    for ptag in sorted(ptag_to_name):
        side_surfs = sorted(
            {
                side_surf_of[ctag]
                for ctag in ptag_to_curves[ptag]
                if ctag in side_surf_of
            }
        )
        if not side_surfs:
            print(f"Physical Curve '{ptag_to_name[ptag]}' (tag {ptag}): no side surfaces found")
            continue
        gmsh.model.addPhysicalGroup(2, side_surfs, tag=ptag)
        gmsh.model.setPhysicalName(2, ptag, ptag_to_name[ptag])
        print(f"Physical Surface '{ptag_to_name[ptag]}' (tag {ptag}): {len(side_surfs)} surface(s)")

    reserved = set(ptag_to_name)
    back_surfs = sorted(back_surf_of.values())
    front_surfs = sorted(front_surf_of.values())
    if back_surface_name == front_surface_name:
        ptag = _add_named_surface_group(back_surfs + front_surfs, back_surface_name, reserved)
        if ptag is not None:
            reserved.add(ptag)
    else:
        back_ptag = _add_named_surface_group(back_surfs, back_surface_name, reserved)
        if back_ptag is not None:
            reserved.add(back_ptag)
        front_ptag = _add_named_surface_group(front_surfs, front_surface_name, reserved)
        if front_ptag is not None:
            reserved.add(front_ptag)

    gmsh.write(out_msh)
    return 0


def main(
    geo_path: str,
    out_msh: str,
    *,
    dz: float = 1.0,
    mesh_dim: int = 3,
    back_surface_name: str = "back",
    front_surface_name: str = "front",
    overwrite_surface_groups: bool = True,
) -> int:
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.SaveAll", 1)

        gmsh.open(geo_path)
        sync_any()

        if Path(geo_path).suffix.lower() == ".msh":
            return _extrude_2d_msh_direct(
                out_msh,
                dz=dz,
                back_surface_name=back_surface_name,
                front_surface_name=front_surface_name,
            )

        # Gather all existing Physical Curve groups (dim=1)
        phys_curves = gmsh.model.getPhysicalGroups(dim=1)
        if not phys_curves:
            print("No Physical Curve groups (dim=1) found. Define Physical Curve(...) in the .geo first.")
            return 2

        # We'll build: (curve-phys-tag) -> set(surfaceTags)
        # and also remember the curve group's name.
        ptag_to_name: dict[int, str] = {}
        ptag_to_surfs: dict[int, set[int]] = {}

        for d, ptag in phys_curves:
            nm = gmsh.model.getPhysicalName(1, ptag) or f"curve_group_{ptag}"
            ptag_to_name[ptag] = nm
            ptag_to_surfs[ptag] = set()

        base_curve_set = {tag for _d, tag in gmsh.model.getEntities(dim=1)}
        base_surfs = sorted(tag for _d, tag in gmsh.model.getEntities(dim=2))
        if not base_surfs:
            print("No dim=2 entities found to extrude.")
            return 3
        base_surf_set = set(base_surfs)

        # Extrude the 2D model in +z to create a 3D model.
        extruded = _extrude_surfaces_z([(2, s) for s in base_surfs], dz)
        sync_any()

        extruded_surfs = sorted({tag for dim, tag in extruded if dim == 2 and tag not in base_surf_set})
        front_surfs: set[int] = set()
        for stag in extruded_surfs:
            _upward_vols, downward_curves = gmsh.model.getAdjacencies(2, stag)
            if not any(ctag in base_curve_set for ctag in downward_curves):
                front_surfs.add(stag)

        back_surfs = sorted(base_surf_set)
        front_surfs_sorted = sorted(front_surfs)

        # Remove any existing Physical Surface groups we are about to (re)create so reruns are idempotent.
        if overwrite_surface_groups:
            to_remove = [(2, ptag) for (_d, ptag) in gmsh.model.getPhysicalGroups(dim=2) if ptag in ptag_to_name]
            if to_remove:
                gmsh.model.removePhysicalGroups(to_remove)
            _remove_surface_groups_by_name({back_surface_name, front_surface_name})

        # For each Physical Curve group, find the adjacent *lateral* surfaces and assign them.
        for ptag in ptag_to_name:
            curves = gmsh.model.getEntitiesForPhysicalGroup(1, ptag)
            for ctag in curves:
                upward_surfs, _downward_pts = gmsh.model.getAdjacencies(1, ctag)
                for stag in upward_surfs:
                    if stag not in base_surf_set:
                        ptag_to_surfs[ptag].add(stag)

        reserved = set(ptag_to_name)
        if back_surface_name == front_surface_name:
            ptag = _add_named_surface_group(back_surfs + front_surfs_sorted, back_surface_name, reserved)
            if ptag is not None:
                reserved.add(ptag)
        else:
            back_ptag = _add_named_surface_group(back_surfs, back_surface_name, reserved)
            if back_ptag is not None:
                reserved.add(back_ptag)
            front_ptag = _add_named_surface_group(front_surfs_sorted, front_surface_name, reserved)
            if front_ptag is not None:
                reserved.add(front_ptag)

        # Create Physical Surfaces (dim=2) with SAME TAGS and SAME NAMES as the Physical Curves
        for ptag, surfs in sorted(ptag_to_surfs.items()):
            if not surfs:
                print(f"Physical Curve '{ptag_to_name[ptag]}' (tag {ptag}): no lateral surfaces found")
                continue
            gmsh.model.addPhysicalGroup(2, sorted(surfs), tag=ptag)
            gmsh.model.setPhysicalName(2, ptag, ptag_to_name[ptag])
            print(f"Physical Surface '{ptag_to_name[ptag]}' (tag {ptag}): {len(surfs)} surface(s)")

        sync_any()

        gmsh.model.mesh.generate(mesh_dim)
        gmsh.write(out_msh)
        return 0
    finally:
        gmsh.finalize()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrude 2D Gmsh model in +z and map Physical Curves -> side Physical Surfaces.")
    parser.add_argument("geo", nargs="?", default="case.geo", help="Input .geo file (default: case.geo)")
    parser.add_argument("out", nargs="?", default=None, help="Output .msh file (default: <input>_extruded.msh)")
    parser.add_argument("--dz", type=float, default=1.0, help="Extrusion distance in +z (default: 1.0)")
    parser.add_argument("--back-surface-name", default="back", help="Name for back cap surface group")
    parser.add_argument("--front-surface-name", default="front", help="Name for front cap surface group")
    parser.add_argument("--cap-surface-name", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--mesh-dim", type=int, default=3, choices=[1, 2, 3], help="Mesh dimension to generate")
    parser.add_argument(
        "--no-overwrite-surface-groups",
        action="store_true",
        help="Do not remove existing Physical Surface groups with matching tags (will error if they already exist)",
    )
    args = parser.parse_args()
    in_path = Path(args.geo)
    out_path = Path(args.out) if args.out is not None else in_path.with_name(f"{in_path.stem}_extruded.msh")
    back_name = args.back_surface_name
    front_name = args.front_surface_name
    if args.cap_surface_name is not None:
        back_name = args.cap_surface_name
        front_name = args.cap_surface_name
    raise SystemExit(
        main(
            args.geo,
            str(out_path),
            dz=args.dz,
            mesh_dim=args.mesh_dim,
            back_surface_name=back_name,
            front_surface_name=front_name,
            overwrite_surface_groups=not args.no_overwrite_surface_groups,
        )
    )
