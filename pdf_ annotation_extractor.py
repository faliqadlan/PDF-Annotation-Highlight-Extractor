# ==============================================================================
# 1. INSTALL LIBRARIES
# ==============================================================================
# This cell installs the necessary Python libraries if they aren't already installed.
# PyMuPDF is used for PDF processing, and pandas is for data display.
# ==============================================================================
!pip install PyMuPDF pandas

# ==============================================================================
# 2. SET THE PDF FILE PATH
# ==============================================================================
# Instead of uploading, you now specify the path to your PDF file directly.
#
# HOW TO GET THE PATH:
# 1. Upload your PDF to the Colab session (using the file browser on the left).
# 2. Right-click the file in the browser and select "Copy path".
# 3. Paste the path between the quotes below.
# ==============================================================================
import os

# --- IMPORTANT: PASTE YOUR PDF FILE PATH HERE ---
# Example: pdf_path = "/content/my_research_paper.pdf"
pdf_path = "/content/sample_annotated_document.pdf" # Replace with your file's path

# The script will check if the file exists at the specified path.
if not os.path.exists(pdf_path):
    print(f"Error: The file '{pdf_path}' was not found.")
    print("Please make sure you have uploaded the file and copied the correct path.")
    pdf_path = None # Set to None to prevent errors in later cells


# ==============================================================================
# 3. IMPORT LIBRARIES AND DEFINE CORE FUNCTIONS
# ==============================================================================
# This cell contains all the logic for extracting headings and annotations.
# It remains unchanged from the previous version.
# ==============================================================================
import fitz  # PyMuPDF
import pandas as pd
import operator
import re

def get_headings(doc):
    """
    Identifies document headings using two methods:
    1. Primary: Extracts the Table of Contents (ToC) if it exists.
    2. Fallback: Uses a style-based heuristic (font size and boldness) if no ToC is found.

    Args:
        doc: The PyMuPDF document object.

    Returns:
        A sorted list of heading dictionaries, each containing 'level', 'text', 
        'page', and 'y' position. Returns an empty list if none are found.
    """
    
    # --- Primary Method: Use the Table of Contents ---
    toc = doc.get_toc()
    if toc:
        print("Found a Table of Contents. Using it to identify headings.")
        headings = []
        for level, title, page in toc:
            clean_title = title.strip()
            # We search for the title on its page to get its location.
            search_results = doc[page - 1].search_for(clean_title, hit_max=1)
            y_pos = search_results[0].y0 if search_results else 0
            
            headings.append({
                "level": level,
                "text": clean_title,
                "page": page - 1,  # 0-indexed
                "y": y_pos
            })
        headings.sort(key=operator.itemgetter('page', 'y'))
        return headings

    # --- Fallback Method: Font Style Heuristic ---
    print("No Table of Contents found. Using font style heuristic to identify headings.")
    
    headings = []
    styles = {}
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    for s in l["spans"]:
                        style_key = (int(round(s['size'])), s['flags'] & 1)
                        styles[style_key] = styles.get(style_key, 0) + 1

    if not styles:
        print("Warning: No text styles found. Cannot identify headings.")
        return []
    
    body_style = max(styles, key=styles.get)
    body_size, body_is_bold = body_style
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    for s in l["spans"]:
                        span_size = int(round(s['size']))
                        span_is_bold = s['flags'] & 1
                        
                        if (span_size > body_size or (span_is_bold and not body_is_bold)):
                            text = s["text"].strip()
                            if text and not text.lower().startswith("figure"):
                                headings.append({
                                    "level": span_size,
                                    "text": text,
                                    "page": page_num,
                                    "y": s["bbox"][1]
                                })

    headings.sort(key=operator.itemgetter('page', 'y'))
    if not headings:
        return []

    unique_headings = [headings[0]]
    for i in range(1, len(headings)):
        prev = headings[i-1]
        curr = headings[i]
        if not (curr["text"] == prev["text"] and curr["page"] == prev["page"] and abs(curr["y"] - prev["y"]) < 10):
            unique_headings.append(curr)
            
    return unique_headings


def extract_annotations_with_headings(pdf_path):
    """
    Extracts text annotations and highlighted text from a PDF, mapping each 
    to its nearest preceding heading.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A list of dictionaries, each containing the annotation details.
    """
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' was not found or is invalid.")
        return []
        
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening or processing PDF file: {e}")
        return []

    print("\nStep 1: Identifying headings...")
    headings = get_headings(doc)
    
    if not headings:
        print("Could not identify any headings. Annotations will be listed without a heading.")
    else:
        print(f"Found {len(headings)} potential headings.")

    print("\nStep 2: Extracting annotations and mapping to headings...")
    results = []
    
    for page_num, page in enumerate(doc):
        page_headings = [h for h in headings if h['page'] == page_num]
        
        annots = page.annots()
        if not annots:
            continue
            
        sorted_annots = sorted(list(annots), key=lambda a: a.rect.y0)
      
        for annot in sorted_annots:
            annot_y = annot.rect.y0
            comment = annot.info.get("content", "").strip()
            author = annot.info.get("title", "N/A").strip()
            created_at = annot.info.get("creationDate", "N/A")
            highlighted_text = ""
            
            annot_types = {8: "Comment", 9: "Highlight", 10: "Underline", 11: "Squiggly", 12: "StrikeOut"}
            annot_type = annot_types.get(annot.type[0], "Other")

            # CORRECTED THIS LINE: Changed PDF_ANNOT_STRIKEOUT to PDF_ANNOT_STRIKE_OUT
            if annot.type[0] in [fitz.PDF_ANNOT_HIGHLIGHT, fitz.PDF_ANNOT_UNDERLINE, fitz.PDF_ANNOT_SQUIGGLY, fitz.PDF_ANNOT_STRIKE_OUT]:
                highlighted_text = page.get_text("text", clip=annot.rect).strip()

            if not comment and not highlighted_text:
                continue

            current_heading_text = "No Associated Heading"
            current_heading_level = 0
            
            for h in page_headings:
                if h['y'] < annot_y:
                    current_heading_text = h['text']
                    current_heading_level = h['level']
                else:
                    break
            
            if current_heading_text == "No Associated Heading":
                prev_page_headings = [h for h in headings if h['page'] < page_num]
                if prev_page_headings:
                    last_heading = prev_page_headings[-1]
                    current_heading_text = last_heading['text']
                    current_heading_level = last_heading['level']

            results.append({
                "Heading": current_heading_text,
                "Page": page_num + 1,
                "Annotation Type": annot_type,
                "Highlighted Text": highlighted_text,
                "Comment": comment,
                "Author": author,
                "Created At": created_at,
            })

    doc.close()
    print("\nStep 3: Extraction complete.")
    return results

# ==============================================================================
# 4. EXECUTE EXTRACTION AND DISPLAY RESULTS
# ==============================================================================
# This cell runs the main extraction function and displays the results in a table.
# ==============================================================================
if pdf_path:
    # To demonstrate, we'll create a dummy annotated PDF if the specified one doesn't exist
    if not os.path.exists(pdf_path):
        print(f"'{pdf_path}' not found. Creating a sample annotated PDF for demonstration.")
        doc = fitz.open()
        page = doc.new_page()
        # Add a heading and a highlight with a comment
        page.insert_text((50, 100), "1. Introduction", fontsize=18, fontname="helv-bold")
        page.insert_text((50, 120), "This is the first sentence of the introduction.", fontsize=11)
        highlight = page.add_highlight_annot((50, 118, 350, 132))
        highlight.set_info(content="This needs a citation.", title="Reviewer A")
        highlight.update()
        # Add another heading and a comment
        page.insert_text((50, 200), "2. Methodology", fontsize=18, fontname="helv-bold")
        page.add_text_annot((50, 220), "The methodology section is unclear.", "Note")
        doc.save(pdf_path)
        doc.close()
        print(f"Sample file created at '{pdf_path}'. Rerunning extraction...")


    # Run the main extraction function
    extracted_data = extract_annotations_with_headings(pdf_path)

    if extracted_data:
        print(f"\n--- Found {len(extracted_data)} Annotations ---")
        
        # Use pandas to create a clean, readable DataFrame
        df = pd.DataFrame(extracted_data)
        
        # Reorder columns for better presentation
        df = df[["Heading", "Page", "Annotation Type", "Highlighted Text", "Comment", "Author"]]
        
        # Display the DataFrame in the Colab output
        display(df)
        
        # Save the results to a CSV file
        csv_filename = os.path.splitext(pdf_path)[0] + "_annotations.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\nResults have also been saved to '{csv_filename}'. You can download it from the file browser on the left.")

    else:
        print(f"\nNo text annotations or highlights were found in '{pdf_path}'.")

else:
    print("\nCannot run extraction because no valid PDF file path was provided in Step 2.")

