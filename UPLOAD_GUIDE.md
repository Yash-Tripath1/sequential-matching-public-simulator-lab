# Applying this ZIP to the existing GitHub repository

This archive is a repository-content update, not a Git repository and not a push. It intentionally excludes `.git/`, credentials, virtual environments, and Python caches. It does not overwrite your existing Git history.

## Safe update on your Ubuntu VM

1. Back up your current clone or create a new branch.
2. Extract the ZIP into a temporary directory and inspect it before copying over your checkout.
3. Copy the archive's `sequential-matching-public-simulator-lab/` contents into the root of your existing repository clone. Do **not** copy the archive's `.git` folder (there is none) and do not delete your existing `.git` directory.
4. From the existing clone, review changes and run non-simulation checks:

```bash
git status --short
git diff --check
python -m unittest discover -s tests
python make_scaled_factorial_heatmap.py
python make_research_figures.py
```

5. Review the final README, note draft, source/license notices, and all AI/resource declarations. Do not submit placeholders or statements that your team has not verified.
6. Stage the reviewed files, commit, and push using your authenticated GitHub remote. Record the resulting immutable commit SHA and use that commit link in the Google Form if desired.

The figure commands regenerate plots from saved result aggregates and do not run simulator episodes. The unittest suite includes one small public-simulator smoke episode; it does not rerun the 360-row factorial. The larger experiment runners are included for reproducibility but should not be run merely to update the GitHub repository.

## Before sharing the repository

- Confirm the note’s author line and declaration.
- If available, add the raw user-VM output JSON for the three-seed soft-question screen and seven-seed holdout under `results/`, update the manifest/README, and regenerate the aggregate plot from the verified data. They were not in the shared workspace when this bundle was made.
- If uploading the note to the form as a PDF, convert the included DOCX using your existing office tools and check the page count and 10 MB limit. The DOCX is provided as an editable document; its explicit page breaks are a draft layout, so verify rendering in the office software used for conversion.
