# PDF Annotation and Highlight Extractor

This tool extracts annotations (like comments and highlights) from a PDF file and intelligently organizes them under the document's existing headings. This makes it easy to get a structured summary of your notes.

## ✨ Features

  * **Automatic Heading Detection**: Finds headings by looking for a Table of Contents or by analyzing font styles (size and boldness).
  * **Comprehensive Annotation Extraction**: Pulls out highlights, underlines, comments, and other common annotation types.
  * **Contextual Organization**: Maps every annotation to the correct heading, so you know which part of the document your notes refer to.
  * **CSV Export**: Saves all the extracted data into a clean, easy-to-use CSV file.

-----

## 📝 How to Use (for Beginners)

The easiest way to use this tool is with Google Colab, which lets you run the code directly in your browser without any setup.

### Step 1: Open the Notebook in Colab

1.  Go to `https://colab.research.google.com/`.
2.  In the popup window, click on the **GitHub** tab.
3.  Paste this repository's URL into the search bar: `https://github.com/faliqadlan/pdf-annotation-highlight-extractor`
4.  Press Enter, and then click on `PDF_Annotation_Extractor_(File_Path_Input).ipynb` to open it.

### Step 2: Upload Your PDF 📂

1.  Look for the **folder icon** on the left-hand side of the Colab screen and click it. This opens the file browser.
2.  Click the **"Upload to session storage"** icon (it looks like a page with an arrow pointing up).
3.  Select the annotated PDF file from your computer.

### Step 3: Get the PDF's File Path 🔗

1.  After the upload is complete, you will see your PDF file in the file browser.
2.  **Right-click** on your PDF file.
3.  From the menu, choose **"Copy path"**.

### Step 4: Run the Extractor 🚀

1.  Scroll to the second code cell in the notebook. You'll see this line of code:
    ```python
    pdf_path = "/content/sample_annotated_document.pdf" # Replace with your file's path
    ```
2.  **Replace** the path inside the quotes (`"/content/..."`) by pasting the path you just copied.
3.  From the menu at the top, click **Runtime** -\> **Run all**. This will execute all the steps in the notebook.

### Step 5: View and Download Your Results 📊

  * Once the script finishes, scroll to the bottom of the notebook to see a **table** with all your extracted annotations.
  * A CSV file containing your results (e.g., `your_file_annotations.csv`) will also appear in the file browser on the left, located in the **session storage**. You can **right-click** this file and select **Download** to save it.
