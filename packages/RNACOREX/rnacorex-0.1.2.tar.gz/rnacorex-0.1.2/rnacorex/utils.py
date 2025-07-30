import os

def check_engines():

    """
    
    Check if all required engine files are present in the 'engines/' directory.

    Returns:
        bool: True if all required files are present, False otherwise.
        
    """

    base_dir = os.path.dirname(__file__)
    engines_dir = os.path.join(base_dir, "engines")

    required_files = ["DIANA_targets.txt", "Targetscan_targets.txt", "MTB_targets_25.csv", "TarBase_v9.tsv", "gencode.v47.basic.annotation.gtf"] 
    missing_files = []

    for filename in required_files:
        if not os.path.isfile(os.path.join(engines_dir, filename)):
            missing_files.append(filename)

    if missing_files:
        print("⚠️ The following engine files are missing from the 'engines/' directory:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    else:
        print("✅ All required engines are present.")
        return True