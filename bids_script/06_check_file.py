import pandas as pd
from pathlib import Path


def gather_dataset_info(root_folder):
    """Loops through the BIDS dataset and extracts raw counts and directory presence."""
    root_path = Path(root_folder)
    dataset_summary = []

    for sub_dir in sorted(root_path.glob('sub-*')):
        print(sub_dir)
        if not sub_dir.is_dir(): continue
        subject_id = sub_dir.name

        for ses_dir in sorted(sub_dir.glob('ses-*')):
            if not ses_dir.is_dir(): continue
            session_id = ses_dir.name

            # Count Anat
            anat_dir = ses_dir / 'anat'
            anat_count = len(list(anat_dir.glob('*.nii.gz'))) if anat_dir.exists() else 0

            # Count DWI
            dwi_dir = ses_dir / 'dwi'
            dwi_count = len(list(dwi_dir.glob('*_dwi.nii.gz'))) if dwi_dir.exists() else 0

            # Check Func
            func_dir = ses_dir / 'func'
            func_present = False
            if func_dir.exists() and len(list(func_dir.glob('*_bold.nii.gz'))) > 0:
                func_present = True

            # Check Segmentation (longiseg)
            seg_dir = ses_dir / 'longiseg'
            # Check if directory exists and contains at least one file/folder
            seg_present = seg_dir.exists() and any(seg_dir.iterdir())

            # Check Surfaces (surf-slam)
            surf_dir = ses_dir / 'surf-slam'
            surf_present = surf_dir.exists() and any(surf_dir.iterdir())

            dataset_summary.append({
                'Subject': subject_id,
                'Session': session_id,
                'Anat': anat_count,
                'DWI': dwi_count,
                'Func': func_present,
                'Seg': seg_present,
                'Surf': surf_present
            })

    return pd.DataFrame(dataset_summary)


def format_cell(row):
    """Formats a single cell with HTML and text labels."""
    # Handle entirely missing sessions for a subject (NaN)
    if pd.isna(row['Anat']):
        return "<span style='color: #ccc;'>-</span>"

    # Define text labels instead of icons
    anat_label = "Anat:"
    dwi_label = "DWI:"

    func_line = "<div>Func: Yes</div>" if row['Func'] else ""
    seg_line = "<div>Seg: Yes</div>" if row.get('Seg', False) else ""
    surf_line = "<div>Surf: Yes</div>" if row.get('Surf', False) else ""

    # Format as a clean vertical cell
    cell_html = (
        f"<div style='line-height: 1.4;'>"
        f"<div>{anat_label} {int(row['Anat'])}</div>"
        f"<div>{dwi_label} {int(row['DWI'])}</div>"
        f"{func_line}"
        f"{seg_line}"
        f"{surf_line}"
        f"</div>"
    )
    return cell_html


def create_publication_table(df, output_html="dataset_table.html"):
    """Pivots the dataframe and applies CSS styling for a paper-ready look."""

    if df.empty:
        print("Dataset is empty. Cannot create table.")
        return

    # Apply the cell formatting
    df['Cell_Content'] = df.apply(format_cell, axis=1)

    # Pivot: Rows = Subject, Columns = Session, Values = Cell_Content
    pivot_df = df.pivot(index='Subject', columns='Session', values='Cell_Content')

    # Fill any subjects that missed a specific session completely
    pivot_df = pivot_df.fillna("<span style='color: #ccc;'>-</span>")

    # Remove the name of the columns axis for a cleaner look
    pivot_df.columns.name = None
    pivot_df.index.name = None

    # CSS Styling for a classic scientific paper format (APA / Nature style)
    styles = [
        dict(selector="table", props=[("border-collapse", "collapse"),
                                      ("font-family", "Arial, sans-serif"),
                                      ("font-size", "10pt"),
                                      ("margin", "20px 0")]),
        dict(selector="th", props=[("border-top", "2px solid black"),
                                   ("border-bottom", "1px solid black"),
                                   ("padding", "12px 15px"),
                                   ("text-align", "center"),
                                   ("background-color", "#fcfcfc")]),
        dict(selector="th.row_heading", props=[("text-align", "left"),
                                               ("font-weight", "bold")]),
        dict(selector="td", props=[("padding", "10px 15px"),
                                   ("text-align", "center"),
                                   ("border-bottom", "1px solid #eeeeee")]),
        dict(selector="tr:last-child td, tr:last-child th", props=[("border-bottom", "2px solid black")]),
    ]

    # Generate Styled HTML
    html_out = (
        pivot_df.style
        .set_table_styles(styles)
        .to_html()
    )

    # Add a legend at the bottom explaining the text labels
    legend = """
    <div style='font-family: Arial, sans-serif; font-size: 9pt; color: #555; margin-top: 10px;'>
        <em>Note:</em> Anat = Anatomical (T2w) runs; DWI = Diffusion runs; Func = Functional (rs-fMRI) presence; Seg = Segmentation (longiseg) presence; Surf = Surfaces (surf-slam) presence.
    </div>
    """

    # Save to file
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_out + legend)

    print(f"Publication table successfully generated: {output_html}")
    print("Open this file in your web browser (Chrome/Firefox/Safari).")
    print("You can select the table on the webpage, copy it (Ctrl+C), and paste it directly into MS Word (Ctrl+V).")


if __name__ == "__main__":
    # ---> CHANGE THIS PATH to your data folder <---
    DATASET_ROOT = "/envau/work/meca/data/BaboFet_BIDS/derivatives/"

    # 1. Extract data
    df_raw = gather_dataset_info(DATASET_ROOT)

    # 2. Generate styled table
    create_publication_table(df_raw, "publication_table.html")