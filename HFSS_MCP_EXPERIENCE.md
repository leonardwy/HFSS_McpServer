# HFSS MCP Usage Experience (2026-05-01)

## Scope
This note summarizes issues encountered while building and simulating a 10 GHz microstrip patch antenna through `hfss_server` MCP tools, plus practical fixes that worked.

## Environment
- AEDT: 2026.1 (gRPC session on port 56440)
- PyAEDT: 0.25.1
- Python: 3.12.10
- Project: `PatchAntenna_10GHz`
- Design: `Patch10GHz`

## Problems Encountered and Fixes

### 1) MCP tool definition placement caused syntax/runtime break
- Symptom: server failed or tool list was malformed.
- Root cause: one `Tool(...)` block was outside the `return [...]` list.
- Fix: move the tool definition back into `get_tool_definitions()` return list.

### 2) Face ID used as list index (port/radiation assignment failed)
- Symptom: `IndexError` when assigning wave port/radiation by face.
- Root cause: used `obj.faces[face_id]` where `face_id` is a geometry ID, not an array index.
- Fix: pass face IDs directly to API calls.

### 3) Radiation API name mismatch across PyAEDT versions
- Symptom: `'Hfss' object has no attribute 'assign_radiation_boundary_on_faces'`.
- Root cause: wrong method name for PyAEDT 0.25.1.
- Fix (implemented): use `assign_radiation_boundary_to_faces([face_id], name=...)`.

### 4) Sweep creation API mismatch
- Symptom: `unexpected keyword argument 'units'`.
- Root cause: wrong kwarg name for `create_linear_count_sweep`.
- Fix: use `unit=...` (not `units=...`).

### 5) Setup object method assumption was wrong
- Symptom: `'SetupHFSS' object has no attribute 'create_sweep'`.
- Root cause: method not available in this version.
- Fix: use `hfss.create_linear_count_sweep(...)` or setup-supported alternatives.

### 6) Some failing gRPC calls released Desktop session
- Symptom: later calls fail with `InvokeAedtObjMethod` / broken connection.
- Root cause: certain API failures in sequence caused Desktop release.
- Fix: reconnect session and rebind MCP session manager before continuing.

### 7) Far-field sphere creation instability
- Symptom: `InsertInfiniteSphereSetup` failed on gRPC route in this setup.
- Root cause: API/transport compatibility behavior in this environment.
- Practical handling:
  - Ensure radiation boundaries exist first.
  - Reconnect if Desktop was released.
  - Reuse existing valid far-field reports when available.

### 8) S-parameter helper API mismatch
- Symptom: `hfss.post.get_report_arrays` not found.
- Root cause: version-specific API differences.
- Fix: fallback to `hfss.post.create_report(...)`.

## Stable Workflow That Worked
1. Launch/connect HFSS and bind session in MCP manager.
2. Build geometry and materials.
3. Assign wave port using face ID directly.
4. Assign radiation boundaries on AirBox faces.
5. Create setup and sweep using PyAEDT-0.25.1-compatible args.
6. Validate design; fix reported issues.
7. Run analysis.
8. Create reports (VSWR and far-field when context is valid).
9. Save project after each critical stage.

## Version-Safe API Notes
- Radiation to faces:
  - `hfss.assign_radiation_boundary_to_faces([face_id], name="...")`
- Wave port:
  - `hfss.wave_port(assignment=face_id, name="P1")`
- Linear count sweep:
  - `hfss.create_linear_count_sweep(setup="Setup1", unit="GHz", start_frequency=8.0, stop_frequency=12.0, num_of_freq_points=401, ... )`

## Recovery Checklist
- If command fails with session errors:
  1. Reconnect to existing AEDT gRPC session.
  2. Rebind `_global_hfss` and `session_manager` current session.
  3. Save project.
  4. Re-run validation and analysis.

## Deliverables Verified in This Task
- 8-12 GHz sweep simulation completed.
- VSWR report created.
- Far-field report objects exist and can be exported (CSV).
- MCP radiation boundary API in server code corrected for current environment.
