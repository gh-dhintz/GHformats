#' Convert to HTML document with bootstrap design 'material'
#'
#' \code{html_material} converts the R Markdown file into an HTML document output format
#' that has a navigation bar on the left and in which the different sections
#' (defined by setting header level 1 (#)) are displayed on individual pages.
#' The design is an adaptation from the Material design theme
#' for Bootstrap 3 project: \url{https://github.com/FezVrasta/bootstrap-material-design}.
#' The HTML, JavaScript, CSS, and R code were originally developed by Julien Barnier
#' in the \href{https://github.com/juba/rmdformats}{rmdformats} package and adapted
#' for Guardant Health branding. This template uses Roboto font (embedded web fonts).
#'
#' @param highlight Syntax highlighting style. Supported styles include
#'   "default", "tango", "pygments", "kate" (default), "monochrome", "espresso",
#'   "zenburn", "haddock", and "textmate". Pass \code{NULL} to prevent syntax
#'   highlighting.
#' @param code_folding Enable document readers to toggle the display of R code chunks.
#'   Specify "show" to show all R code chunks by default. Specify "none" to display all
#'   code chunks (assuming they were knit with echo = TRUE). Specify "hide" to hide
#'   all R code chunks by default (users can show hidden code chunks
#'   either individually or document-wide).
#' @param code_download Embed the Rmd source code within the document and provide a
#'   link that can be used by readers to download the code.
#' @param cards If \code{TRUE}, sections will be presented as distinct and animated
#'   cards or pages.  If \code{FALSE}, sections are all on a single page.
#' @param lightbox \code{TRUE} to add lightbox effect to content images.
#' @param gallery If \code{TRUE} and lightbox is \code{TRUE}, add a gallery navigation
#'   between images in lightbox display.
#' @param thumbnails \code{TRUE} to display content images as thumbnails.
#' @param fig_width Default width (in inches) for figures, set here to 6.
#' @param fig_height Default width (in inches) for figures, set here to 4.
#' @param fig_caption \code{TRUE} to render figures with captions.
#' @param use_bookdown If \code{TRUE} (default), uses \code{\link[bookdown]{html_document2}}
#'   instead of \code{\link[rmarkdown]{html_document}}, thus providing numbered sections
#'   and automatic numbering of tables and figures. The hyperlink in the cross-references,
#'   does not work here.
#' @param mathjax Set to NULL to disable Mathjax insertion.
#' @param pandoc_args Arguments passed to the pandoc_args argument of rmarkdown
#'   \code{\link[rmarkdown]{html_document}}.
#' @param md_extensions arguments passed to the md_extensions argument of rmarkdown
#'   \code{\link[rmarkdown]{html_document}}
#' @param ... Additional function arguments passed to rmarkdown.
#'   \code{\link[rmarkdown]{html_document}}
#'
#' @return R Markdown output format to pass to \code{\link[rmarkdown]{render}}
#' @import rmarkdown
#' @import bookdown
#' @importFrom htmltools htmlDependency
#' @export
#'
html_material <- function(
  highlight = "kate", code_folding = "show", code_download = FALSE,
  cards = TRUE, lightbox = TRUE, thumbnails = TRUE, gallery = TRUE,
  fig_width = 6, fig_height = 6, fig_caption = TRUE,
  use_bookdown = TRUE, md_extensions = NULL,
  mathjax = "GHformats", pandoc_args = NULL, ... ) {

  html_template(
    template_name = "html_material",
    template_path = "templates/html_material/html_material.html",
    template_dependencies = list(
      html_dependency_bootstrap_material(),
      html_dependency_material()
    ),
    pandoc_args = pandoc_args,
    highlight = highlight,
    code_folding = code_folding,
    code_download = code_download,
    cards = cards,
    toc = TRUE,
    toc_depth = 1,
    lightbox = lightbox,
    thumbnails = thumbnails,
    gallery = gallery,
    fig_width = fig_width,
    fig_height = fig_height,
    fig_caption = fig_caption,
    use_bookdown = use_bookdown,
    md_extensions = md_extensions,
    mathjax = mathjax,
    ...
  )

}


##### This was also adjusted to link to the GHformats file names:
# bootstrap material design js and css
# https://github.com/FezVrasta/bootstrap-material-design
html_dependency_bootstrap_material <- function() {
  htmltools::htmlDependency(name = "bootstrap_material",
    version = utils::packageVersion("GHformats"),
    src = system.file("templates/html_material/lib", package = "GHformats"),
    script = c("material.min.js", "ripples.min.js"),
    stylesheet = c("bootstrap-material-design.min.css", "ripples.min.css"))
}

# material js and css
html_dependency_material <- function() {
  htmltools::htmlDependency(name = "html_material",
    version = utils::packageVersion("GHformats"),
    src = system.file("templates/html_material", package = "GHformats"),
    script = "html_material.js",
    stylesheet = "html_material.css")
}
