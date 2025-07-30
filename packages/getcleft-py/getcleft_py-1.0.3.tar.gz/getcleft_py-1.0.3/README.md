# GetCleft as a Python Package

A Python package designed to prepare arguments and run `GetCleft`.

---

## Example usage:

```
from getcleftpy import run_getcleft

run_getcleft("/path/to/myprotein.pdb")
```

---

## Arguments

| Argument                    | Type    | Description                                                                                                                                                                                                                                                                             | Default                        |
|-----------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| `pdb_file`                  | `str`   | PDB filename (e.g., `myprotein.pdb`).                                                                                                                                                                                                                                                   | **Required**                   |
| `min_sphere_radius`         | `float` | Minimum sphere radius. `Get_Cleft` default is `1.50`.                                                                                                                                                                                                                                   | `None`                         |
| `max_sphere_radius`         | `float` | Maximum sphere radius. `Get_Cleft` default is `4.00`.                                                                                                                                                                                                                                   | `None`                         |
| `output_het_atoms`          | `bool`  | Output hetero group atoms in the cleft. Corresponds to the `-h` flag in `Get_Cleft`.                                                                                                                                                                                                    | `False`                        |
| `output_all_het_atoms`      | `bool`  | Output all atoms of hetero groups found in the cleft.                                                                                                                                                                                                                                   | `False`                        |
| `chain_ids`                 | `list`  | A list of chain IDs to be considered (e.g., `['A', 'B']`). If `None`, all chains are included.                                                                                                                                                                                          | `None`                         |
| `num_clefts`                | `int`   | The maximum number of clefts to be generated. `Get_Cleft` default is `0` (all clefts).                                                                                                                                                                                                  | `5`                            |
| `anchor_residue_specifier`  | `str`   | Specifies an anchor residue or hetero molecule as residue, number, chain, alternate location identifier. The placeholder `-` is used to indicate a blank character for the alternate location identifier (should be present if unsure) or the chain ID (e.g., `LIG123A-` or `LYS128-`). | `None`                         |
| `anchor_mode`               | `str`   | Mode for the anchor residue. Can be `all`, `interacting`, or `both`.                                                                                                                                                                                                                    | `None`                         |
| `include_calpha`            | `bool`  | Include C-alpha atoms of residues in certain outputs.                                                                                                                                                                                                                                   | `False`                        |
| `include_cbeta`             | `bool`  | Include C-beta atoms of residues in certain outputs.                                                                                                                                                                                                                                    | `False`                        |
| `include_all_residue_atoms` | `bool`  | Include all atoms of the residue in certain outputs.                                                                                                                                                                                                                                    | `False`                        |
| `output_spheres`            | `bool`  | Output the cleft spheres, including their center coordinates and radii.                                                                                                                                                                                                                 | `True`                         |
| `contact_threshold`         | `float` | The threshold distance for defining contacts. `Get_Cleft` default is `5.0`.                                                                                                                                                                                                             | `None`                         |
| `output_base`               | `str`   | The full path and filename for the output, without the extension (e.g., `/path/to/output/filename`).                                                                                                                                                                                    | Folder of the input `pdb_file` |
| `verbose`                   | `bool`  | If `True`, the standard output and standard error from `Get_Cleft` will be printed.                                                                                                                                                                                                     | `False`                        |

---

## Returns

| Type                          | Description                                                                                                                    |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `subprocess.CompletedProcess` | The result of the `Get_Cleft` execution. This object includes attributes such as `args`, `returncode`, `stdout`, and `stderr`. |

---

## Raises

| Error                           | Condition                                                                                                           |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------|
| `FileNotFoundError`             | Raised if the `Get_Cleft` executable or the specified input file cannot be found.                                   |
| `ValueError`                    | Raised if `anchor_mode` is provided without an `anchor_residue_specifier`, or if an invalid `anchor_mode` is given. |
| `subprocess.CalledProcessError` | Raised if the `Get_Cleft` executable returns a non-zero exit code, indicating an error during its execution.        |