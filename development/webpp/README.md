Offline Web Preprocessor
========================

This script provides a system for preprocessing source files used for web
pages into single source files.  The goal is to allow it to recursively
construct a single output file given a single "root" file that eventually
references each of the necessary external resources.

Use Cases
---------

### Static HTML Page

The preprocessor takes in a `.html` file and converts it to a new `.html` file
with all internal references resolved to in-page content.  Some of the initial
conversions will include:

- Convert style sheet `<link>` elements to `<style>` elements containing the
  style information defined in the external file.
- Convert `<script>` elements with `src` attributes to `<script>` elements
  containing the external file as an inline script.
- Within `<script>` elements, resolve inclusion of external JSON data by
  writing the contents of the file.  This may require some special support in
  the script to allow multiple ways of access the JSON data depending on if
  it is local to the script, or requires access over HTTP.

Future conversions may include:

- Convert references to external images to data URIs embedded in the HTML
  page.
- Recurse into .css files looking for @import rules.
- Look for common "JavaScript include" patterns in .js files.
- Look for structured dependency comments in .js and .css files.
- Be able to include an XML document as a native document object.
- Be able to inject data from CSV files as constant literals.
- Be able to inject data from an SQLite database as constant literals.

### PHP Source File

PHP presents some additional challenges.  The easy way to convert a complex
PHP presentation layer is to recursively resolve all the `include()` and
`require()` calls.  The more difficult task is to attempt to discover any
auto-loading classes.  This may need to be helped with structured dependency
comments in the source file.

The output should be a single `.php` file that contains all the server-side
and client-side resources necessary to replicate the application.
