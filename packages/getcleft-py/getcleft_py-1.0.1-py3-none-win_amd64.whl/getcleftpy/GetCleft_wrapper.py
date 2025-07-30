import subprocess
import os
import platform


def run_getcleft(
    pdb_file: str,
    min_sphere_radius: float = None,
    max_sphere_radius: float = None,
    output_het_atoms: bool = False,
    output_all_het_atoms: bool = False,
    chain_ids: list = None, # List of strings e.g. ['A', 'B']
    num_clefts: int = 5,
    anchor_residue_specifier: str = None, # e.g., "LIG123A-"
    anchor_mode: str = None, # 'all', 'interacting', or 'both'
    include_calpha: bool = False,
    include_cbeta: bool = False,
    include_all_residue_atoms: bool = False,
    output_spheres: bool = True,
    contact_threshold: float = None,
    output_base: str = None,
    verbose: bool = False
):
    """
    Python function to prepare arguments and run the Get_Cleft executable.

    This function can be imported and used in other Python scripts or packages.

    Args:
        pdb_file (str): PDB filename (e.g., myprotein.pdb).
        min_sphere_radius (float, optional): Min sphere radius. (Get_Cleft default: 1.50).
        max_sphere_radius (float, optional): Max sphere radius. (Get_Cleft default: 4.00).
        output_het_atoms (bool, optional): Output hetero group atoms in cleft.
                                         (Corresponds to Get_Cleft's -h flag). Defaults to False.
        output_all_het_atoms (bool, optional): Output all atoms of hetero groups in cleft.
                                             Defaults to False.
        chain_ids (list, optional): List of chain IDs to be considered (e.g., ['A', 'B']).
                                    If None, Get_Cleft considers all. Defaults to None.
        num_clefts (int, optional): Maximum number of clefts to be generated. Defaults to 5.
                                    (Get_Cleft default: 0, meaning all). Defaults to None.
        anchor_residue_specifier (str, optional): Anchor residue/hetero molecule
                                                  (Format: RESNUMCA, e.g., LIG123A- or ---123--).
                                                  Defaults to None.
        anchor_mode (str, optional): Mode for anchor residue. Can be 'all' (outputs all atoms
                                     in selected cleft; Default), 'interacting' (outputs all atoms in contact),
                                     or 'both' (produces two output files).
                                     Corresponds to -a, -i, -b flags of Get_Cleft. Defaults to None.
        include_calpha (bool, optional): Include C-alpha of residues in certain outputs. Defaults to False.
        include_cbeta (bool, optional): Include C-beta of residues in certain outputs. Defaults to False.
        include_all_residue_atoms (bool, optional): Include all atoms of the residue in certain outputs.
                                                 Defaults to False.
        output_spheres (bool, optional): Output cleft spheres (centre coordinates and radii).
                                       Defaults to True.
        contact_threshold (float, optional): Threshold distance for contact definition.
                                           (Get_Cleft Default: 5.0). Defaults to None.
        output_base (str, optional): Output full path and filename without extension (e.g. /foo/bar/filename).
                                     Defaults to the folder where the pdb file is located.
        verbose (bool, optional): Output stdout and stderr (program errors).

    Returns:
        subprocess.CompletedProcess: The result of the Get_Cleft execution. Contains attributes
                                     like 'args', 'returncode', 'stdout', 'stderr'.

    Raises:
        FileNotFoundError: If the Get_Cleft executable or the input file is not found.
        ValueError: If anchor_mode is provided without anchor_residue_specifier,
                    or if an invalid anchor_mode is given.
        subprocess.CalledProcessError: If Get_Cleft returns a non-zero exit code.
    """

    # --- Validate executable path ---
    executable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'GetCleft')
    if platform.system() == 'Windows':
        executable_path += '.exe'
    if not os.path.isfile(executable_path) or not os.access(executable_path, os.X_OK):
        print(f"Error: Executable '{executable_path}' not found or not executable.")
        return
    cmd = [executable_path]

    # Obligatory arguments
    pdb_file = os.path.abspath(pdb_file)
    if not os.path.isfile(pdb_file):
        raise FileNotFoundError(f"Error: File '{pdb_file}' not found.")
    else:
        cmd.extend(["-p", pdb_file])

    # Optional arguments
    if min_sphere_radius is not None:
        cmd.extend(["-l", str(min_sphere_radius)])
    if max_sphere_radius is not None:
        cmd.extend(["-u", str(max_sphere_radius)])

    if output_het_atoms:
        cmd.append("-h")
    if output_all_het_atoms:
        cmd.append("-H")

    if chain_ids:
        for chain_id_val in chain_ids:
            cmd.extend(["-c", str(chain_id_val)])
    if num_clefts is not None:
        cmd.extend(["-t", str(num_clefts)])

    if anchor_residue_specifier:
        if anchor_mode == "all":
            cmd.extend(["-a", anchor_residue_specifier])
        elif anchor_mode == "interacting":
            cmd.extend(["-i", anchor_residue_specifier])
        elif anchor_mode == "both":
            cmd.extend(["-b", anchor_residue_specifier])
        elif anchor_mode is None:
            cmd.extend(["-a", anchor_residue_specifier])
        else:
            raise ValueError(f"Invalid anchor_mode '{anchor_mode}'. Must be 'all', 'interacting', or 'both'.")
    elif anchor_mode:
        raise ValueError("anchor_mode specified without anchor_residue_specifier.")

    if include_calpha:
        cmd.append("-ca")
    if include_cbeta:
        cmd.append("-cb")
    if include_all_residue_atoms:
        cmd.append("-r")
    if output_spheres:
        cmd.append("-s")
    if contact_threshold is not None:
        cmd.extend(["-k", str(contact_threshold)])
    if output_base is not None:
        cmd.extend(["-o", output_base])
    else:
        output_base = os.path.splitext(pdb_file)[0]
        cmd.extend(["-o", output_base])
    print(f'Files will be written to {os.path.dirname(output_base)}')

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                   universal_newlines=True)
        if verbose:
            print("\n--- Program Output (stdout) ---")
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    print(line, end='')
                process.stdout.close()

            print("\n--- Program Errors (stderr) ---")
            if process.stderr:
                stderr_output = []
                for line in iter(process.stderr.readline, ''):
                    print(line, end='')  # Print errors
                    stderr_output.append(line)
                process.stderr.close()

        return_code = process.wait()

        if return_code == 0:
            print("\nGet_Cleft executed successfully!")
        else:
            print(f"\nGet_Cleft exited with error code: {return_code}")

    except FileNotFoundError:
        print(f"Error: The executable '{executable_path}' was not found. Double-check the path.")
    except PermissionError:
        print(f"Error: Permission denied to execute '{executable_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
