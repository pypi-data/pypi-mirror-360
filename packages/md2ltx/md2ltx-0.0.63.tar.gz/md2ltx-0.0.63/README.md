# md2ltx

A command-line tool for converting Markdown to LateX-formatted PDF via Pandoc. Requires a pip virtual environment in Ubuntu/ Debian based OS.

## 1. Quickstart

### 1.1. Installation

    pip install md2ltx; md2ltx --install_dependencies

### 1.2. Usage

    md2ltx [source.md] [output.pdf] [--open] [--help]

• `source_file`: Path to the input Markdown (.md) file.  

• `output_pdf` (optional): Path to the output PDF file. If omitted, a default name is derived from the source file, and the working directory is assumed to be the path.  

• `--open`: Open the resulting PDF in the system’s default viewer. 

• `--test`: Evaluates embedded python and prints the pre-pandoc processed string for the purposes of debugging. 

• `--template template_name`: Specify a built-in templates by name. Available templates: "one-column-article", "two-column-article", "report", "slides", "letter").

• `--help`: Access documentation.

--------------------------------------------------------------------------------

## 2. Templates

md2ltx can inject Markdown content into a LaTeX “template” that defines the overall look and structure of the PDF. You can choose from these built-in templates:

• "one-column-article"  
• "two-column-article"  
• "report"  
• "slides"  
• "letter"

When you run md2ltx (or Pandoc directly), you can specify the template with the “--template” flag. Pandoc then loads that template, replacing special variables like $title$, $author$, $date$, and $body$ with metadata and the converted Markdown content.

### 2.1. Common Fields in the YAML Metadata

• one-column-article/ two-column-article / report:  
  - title: Title of your document  
  - author: Author name(s)  
  - date: Date displayed below the author(s)

• slides (Beamer presentations):  
  - title: Presentation title  
  - subtitle: (Optional) subtitle for your presentation  
  - author: Presenter name(s)  
  - date: Date (often included on the title slide)

• letter:  
  - author: Sender’s name (also used in \signature)  
  - address: Sender’s address  
  - date: Date displayed in the letter  
  - recipient: Recipient name or address  
  - greeting: Opening phrase (e.g., “Dear John,”)  
  - closing: Closing phrase (e.g., “Regards,”)

-------------------------------------------------------------------------------
### 2.2. Using the Templates

Pandoc reads these fields from a YAML block at the top of your Markdown file. For example:

    ---
    title: "My Awesome Title"
    author: "John Doe"
    date: "October 4, 2023"
    ---

    # Sample Document

    This is a **Markdown** document to test `compile_markdown_to_pdf` from `main.py`.

    ## Advantages of Markdown

    - Easy to write
    - Human-readable
    - Widely supported

    ## Conclusion

    Markdown is fantastic!

When you run md2ltx:

    md2ltx my_document.md --template=two-column-article

Pandoc loads the chosen “two-column-article” template, substitutes $title$, $author$, $date$, and $body$, and then compiles a PDF. The same process applies to any of the provided templates.

---------------------------------------------------------------------------------

## 3. Embedded Python Code with `EMBED::function_name`

md2ltx supports executing Python code blocks alongside your Markdown, and replacing placeholders of the form `EMBED::function_name` with the string returned by calling `function_name()` in Python.

Each code block is enclosed between [START]######## and [END]######## (with at least three “#” characters). All code in those blocks is executed once in the same environment, meaning you can define multiple functions in a single block or spread them across multiple blocks. As soon as the code is executed, any functions you defined become available for embedding.

### 3.1. General Steps

3.1.1. In your Markdown text, put placeholders where you want to inject dynamic data:

    “Markdown is awesome! `EMBED::foo`.”

Each placeholder references a function name that you’ll define in a code block.

3.1.2. Define your code blocks somewhere in the same Markdown file, delimited by [START]…[END]:

    [START]#########################################################################
        def foo() -> str:
            return "Hello from foo()"

        def bar() -> str:
            return "Hello from bar()"
    [END]###########################################################################

You can define as many functions in a block as you want.

3.1.3. At build time, md2ltx collects all your code blocks, removes common indentation so Python sees them as valid top-level code, executes them, and records the function objects.

3.1.4. Every placeholder `EMBED::function_name` in your Markdown is then replaced by the return value of calling that function.

### 3.2. Requirements  

• Each function you plan to embed must take no parameters and return a string (or something convertible to string, or a pandas DataFrame).  
• If your function returns a pandas.DataFrame, md2ltx automatically converts it to a Markdown table (displaying only the first 5 and last 5 rows if there are more than 10).  
• md2ltx does NOT automatically provide additional libraries (e.g. math, pandas, numpy, datetime, rgwfuncs) in the environment. If your code depends on these libraries, you must explicitly import them within your “[START] … [END]” blocks.  
• Keep your code blocks consistently indented. By default, if each line is indented by four spaces, md2ltx will remove those four leading spaces and preserve deeper indentation so that nested code within your function remains valid Python.

### 3.3. Example  

Here’s a short Markdown snippet:

    Markdown is fantastic! `EMBED::sqrt_of_16`. Another result: `EMBED::compute_2`.

    [START]#########################################################################
        import math

        def sqrt_of_16() -> str:
            val = math.sqrt(16)
            return f"The square root of 16 is {val}"
    [END]###########################################################################

    [START]#########################################################################
        import math

        def compute_2() -> str:
            val = math.sqrt(25)
            return f"The square root of 25 is {val}"
    [END]###########################################################################

When processed:

• The code blocks are gathered and executed. Both `sqrt_of_16()` and `compute_2()` are defined.  
• `EMBED::sqrt_of_16` is replaced by “The square root of 16 is 4.0.”  
• `EMBED::compute_2` is replaced by “The square root of 25 is 5.0.”  

Resulting output might look like:

    Markdown is fantastic! The square root of 16 is 4.0. Another result: The square root of 25 is 5.0.

### 3.4. Example with DataFrames  

You can also return a DataFrame—maybe you fetch data from `rgwfuncs.load_data_from_query()`:

    Here’s a DataFrame preview: `EMBED::fetch_data`

    [START]#########################################################################
        import pandas as pd
        from rgwfuncs import load_data_from_query

        def fetch_data() -> pd.DataFrame:
            df = load_data_from_query("mydb", "SELECT * FROM mytable LIMIT 20")
            return df
    [END]###########################################################################

If `fetch_data()` returns a DataFrame (e.g. 20 rows × N columns), md2ltx converts it to a Markdown pipe table. The final output appears as a table, truncated if there are more than 10 rows.

### 3.5. Multiple Blocks, Many Functions  

It’s perfectly valid to define multiple functions in one code block, or spread them among several:

    [START]#########################################################################
        import math

        def foo() -> str:
            return "Hello from foo"

        def bar() -> str:
            return "Hello from bar"
    [END]###########################################################################

    [START]#########################################################################
        def baz() -> str:
            return "Hello from baz"
    [END]###########################################################################

All three functions (foo, bar, baz) become available, and you embed them by writing:

    `EMBED::foo`, `EMBED::bar`, or `EMBED::baz`.

### 3.6. Error Handling  

If your code has a Python syntax error or cannot be executed, md2ltx prints an “[Error executing combined code: …]” message in the logs and all the affected functions remain undefined. Any placeholders referencing them become “[Error: No function named 'xyz' has been defined in the code blocks]”.

--------------------------------------------------------------------------------

## 4. General Pandoc Tranformations

md2ltx uses Pandoc to transform Markdown files into LaTeX, which pdflatex then uses to generate a final PDF. This workflow supports most of Markdown’s core syntax plus many Pandoc extensions. Below is a high-level overview of how Pandoc typically converts various Markdown constructs into LaTeX. For full details, refer to Pandoc’s official documentation.

---

### 4.1. Headings

• <strong>Markdown</strong>  
  <pre><code># Heading 1  
## Heading 2  
### Heading 3</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\section{Heading 1}  
\subsection{Heading 2}  
\subsubsection{Heading 3}</code></pre>

Pandoc chooses <code>\section</code>, <code>\subsection</code>, etc. based on the heading level. It also supports underline-style Markdown headings with “===” or “---” for level-one and level-two headings.

---

### 4.2. Emphasis &amp; Strong Emphasis

• <strong>Markdown</strong>  
  <pre><code>*emphasis* or _emphasis_  
**strong emphasis** or __strong emphasis__</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\emph{emphasis}  
\textbf{strong emphasis}</code></pre>

---

### 4.3. Inline Code

• <strong>Markdown</strong>  
  <pre><code>`inline code`</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\texttt{inline code}</code></pre>

---

### 4.4. Code Blocks

• <strong>Markdown (fenced)</strong>  
  <pre><code>```  
a = 1  
b = 2  
```</code></pre>

• <strong>Pandoc → LaTeX (by default)</strong>  
  <pre><code>\begin{verbatim}  
a = 1  
b = 2  
\end{verbatim}</code></pre>

With certain options, Pandoc can use different LaTeX environments (e.g., listings).

---

### 4.5. Lists

• <strong>Unordered (Markdown)</strong>  
  <pre><code>- item 1  
- item 2  
- item 3</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\begin{itemize}  
\item item 1  
\item item 2  
\item item 3  
\end{itemize}</code></pre>

• <strong>Ordered (Markdown)</strong>  
  <pre><code>1. item 1  
2. item 2</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\begin{enumerate}  
\item item 1  
\item item 2  
\end{enumerate}</code></pre>

---

### 4.6. Links &amp; Images

• <strong>Link (Markdown)</strong>  
  <pre><code>[Pandoc](https://pandoc.org)</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\href{https://pandoc.org}{Pandoc}</code></pre>

• <strong>Image (Markdown)</strong>  
  <pre><code>![Alt text](image.png)</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\includegraphics{image.png}</code></pre>

By default, <code>\includegraphics</code> is placed without floats. You can add captions or figure environments using extended syntax or metadata.

---

### 4.7. Blockquotes

• <strong>Markdown</strong>  
  <pre><code>> This is a blockquote.</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\begin{quote}  
This is a blockquote.  
\end{quote}</code></pre>

---

### 4.8. Horizontal Rules

• <strong>Markdown</strong>  
  <pre><code>---  
***  
___</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\hrule</code></pre>

---

### 4.9. Footnotes (Pandoc Extension)

• <strong>Markdown</strong>  
  <pre><code>This is some text with a footnote.[^1]

[^1]: This is the footnote text.</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>This is some text with a footnote.\footnote{This is the footnote text.}</code></pre>

---

### 4.10. Tables

• <strong>Markdown (simple pipe table)</strong>  
  <pre><code>| Column1 | Column2 |  
|---------|---------|  
| Val1    | Val2    |  
| Val3    | Val4    |</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\begin{table}  
\centering  
\begin{tabular}{ll}  
\hline  
Column1 & Column2 \\  
\hline  
Val1    & Val2    \\  
Val3    & Val4    \\  
\hline  
\end{tabular}  
\end{table}</code></pre>

---

### 4.11. Math &amp; LaTeX Blocks

• <strong>Inline Math</strong>  
  <pre><code>$E = mc^2$</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\(E = mc^2\)</code></pre>

• <strong>Display Math</strong>  
  <pre><code>$$  
E = mc^2  
$$</code></pre>

• <strong>Pandoc → LaTeX</strong>  
  <pre><code>\[  
E = mc^2  
\]</code></pre>

---

### 4.12. Citations &amp; Bibliographies

Pandoc can handle citations if you provide a bibliography file. A reference like <code>[@smith2009]</code> can become <code>\cite{smith2009}</code> or <code>\autocite</code> depending on the style and Pandoc’s command-line options.

---

### 4.14. Raw LaTeX

Pandoc passes raw LaTeX through if you’re converting to LaTeX or PDF. For example:

```
\newpage
```

remains <code>\newpage</code> in the output.

---


