# Automated example generation script for GHformats
# This script renders all R Markdown and Quarto templates to create fresh examples

library(GHformats)
library(rmarkdown)

# Setup
workdir <- "/tmp/ghformats_examples"
# Clean up any existing temp directory
if (dir.exists(workdir)) {
  unlink(workdir, recursive = TRUE)
}
dir.create(workdir, recursive = TRUE, showWarnings = FALSE)
output_dir <- "resources/examples"

cat("\n==============================================\n")
cat("  GHformats Example Regeneration Script\n")
cat("==============================================\n\n")

# R Markdown templates
rmd_templates <- c("html_simple", "html_material", "word_doc",
                   "pdf_simple", "pdf_report", "pdf_cheatsheet",
                   "rmd_to_jupyter")

cat("Phase 1: Rendering R Markdown templates\n")
cat("----------------------------------------\n")

for (template in rmd_templates) {
  cat("\n=== Rendering", template, "===\n")

  tryCatch({
    # Special handling for rmd_to_jupyter
    if (template == "rmd_to_jupyter") {
      # Use skeleton file directly from inst directory
      skeleton_rmd <- "inst/rmarkdown/templates/rmd_to_jupyter/skeleton/skeleton.Rmd"
      skeleton_images <- "inst/rmarkdown/templates/rmd_to_jupyter/skeleton/images"

      # Create temp directory for output
      template_dir <- file.path(workdir, "rmd_to_jupyter")
      dir.create(template_dir, recursive = TRUE, showWarnings = FALSE)

      # Copy skeleton and images to temp directory
      temp_rmd <- file.path(template_dir, "skeleton.Rmd")
      file.copy(skeleton_rmd, temp_rmd, overwrite = TRUE)

      # Copy images directory
      temp_images <- file.path(template_dir, "images")
      if (dir.exists(skeleton_images)) {
        dir.create(temp_images, recursive = TRUE, showWarnings = FALSE)
        file.copy(
          list.files(skeleton_images, full.names = TRUE),
          temp_images,
          overwrite = TRUE,
          recursive = TRUE
        )
      }

      # Convert Rmd to Jupyter notebook
      GHformats::rmd_to_jupyter(temp_rmd)

      # Find the generated .ipynb file
      ipynb_file <- file.path(template_dir, "skeleton.ipynb")

      if (file.exists(ipynb_file)) {
        # Copy and rename .ipynb to examples directory
        output_name <- "demo_rmd_to_jupyter.ipynb"
        file.copy(ipynb_file, file.path(output_dir, output_name), overwrite = TRUE)
        cat("✓ Successfully generated:", output_name, "\n")

        # Create zip file containing the .ipynb and images
        current_dir <- getwd()
        zip_file <- file.path(current_dir, output_dir, "demo_rmd_to_jupyter.zip")
        temp_zip <- file.path(template_dir, "demo_rmd_to_jupyter.zip")

        setwd(template_dir)

        # Zip the notebook file and images directory
        zip(zipfile = "demo_rmd_to_jupyter.zip",
            files = c("skeleton.ipynb", "images"))

        setwd(current_dir)

        # Copy zip to output directory (remove old one first)
        if (file.exists(zip_file)) {
          file.remove(zip_file)
        }
        file.copy(temp_zip, zip_file, overwrite = TRUE)
        cat("✓ Successfully generated: demo_rmd_to_jupyter.zip\n")
      } else {
        cat("✗ Error: .ipynb file not found after conversion\n")
      }
    } else {
      # Normal rendering for other templates
      template_dir <- file.path(workdir, paste0("rmd_", template))

      # Create template directory
      GHformats::create_rmd_doc(dirname = template_dir, template = template)

      # Find the Rmd file
      rmd_file <- list.files(template_dir, pattern = "\\.Rmd$", full.names = TRUE)[1]

      # Render
      output_file <- rmarkdown::render(rmd_file)

      # Determine output extension
      output_ext <- tools::file_ext(output_file)

      # Copy to examples directory with standard naming
      output_name <- paste0("demo_rmd_", template, ".", output_ext)
      file.copy(output_file, file.path(output_dir, output_name), overwrite = TRUE)

      cat("✓ Successfully generated:", output_name, "\n")
    }

  }, error = function(e) {
    cat("✗ Error rendering", template, ":", conditionMessage(e), "\n")
  })
}

# Quarto templates
quarto_templates <- c("html", "word", "pdf_simple", "pdf_report")

cat("\n\nPhase 2: Rendering Quarto templates\n")
cat("------------------------------------\n")

for (template in quarto_templates) {
  cat("\n=== Rendering quarto", template, "===\n")
  template_dir <- file.path(workdir, paste0("quarto_", template))

  tryCatch({
    # Create template directory
    GHformats::create_quarto_doc(dirname = template_dir, template = template)

    # Find the qmd file
    qmd_file <- list.files(template_dir, pattern = "\\.qmd$", full.names = TRUE)[1]

    # Render using quarto
    quarto::quarto_render(qmd_file)

    # Determine output extension
    if (template == "html") {
      output_ext <- "html"
    } else if (grepl("pdf", template)) {
      output_ext <- "pdf"
    } else {
      output_ext <- "docx"
    }

    # Find the output file
    output_file <- sub("\\.qmd$", paste0(".", output_ext), qmd_file)

    # Copy to examples directory with standard naming
    output_name <- paste0("demo_quarto_", template, ".", output_ext)
    file.copy(output_file, file.path(output_dir, output_name), overwrite = TRUE)

    cat("✓ Successfully generated:", output_name, "\n")

  }, error = function(e) {
    cat("✗ Error rendering", template, ":", conditionMessage(e), "\n")
  })
}

cat("\n\n==============================================\n")
cat("  Generation Complete!\n")
cat("==============================================\n\n")

# List generated files
cat("Generated files:\n")
files <- list.files(output_dir, pattern = "^demo_", full.names = FALSE)
for (f in files) {
  cat("  -", f, "\n")
}

cat("\nAll examples generated successfully!\n")

# Phase 3: Generate preview montages
cat("\n\nPhase 3: Generating preview montages\n")
cat("-------------------------------------\n")

python_script <- "scripts/generate_preview_montages.py"
result <- system2("python3", args = python_script, stdout = TRUE, stderr = TRUE)

if (!is.null(attr(result, "status")) && attr(result, "status") != 0) {
  cat("WARNING: Preview montage generation had errors\n")
  cat(paste(result, collapse = "\n"))
} else {
  cat(paste(result, collapse = "\n"))
}
