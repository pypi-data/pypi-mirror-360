import sys
import subprocess
import os
import tempfile
import time
import argparse
import shutil
from typing import Optional, Union, Tuple
from .constants import logo_string, help_string, templates
from .python_evaluation import evaluate_python_in_markdown_string

def preprocess_markdown_file(source_file: str, test: bool = False) -> str:
    """Preprocess a Markdown file by evaluating embedded Python and saving it as a temporary file."""
    with open(source_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Evaluate Python code within the Markdown
    evaluated_content = evaluate_python_in_markdown_string(markdown_content)
    if test:
        print()
        print("#################################################################")
        print("################ EVALUATED PRE-PANDOC CONTENT ###################")
        print("=================================================================")
        print(evaluated_content)
        print("=================================================================")
        print("#################################################################")

    # Create a temporary Markdown file with the evaluated content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as temp_md_file:
        temp_md_file.write(evaluated_content)
        temp_md_path = temp_md_file.name

    return temp_md_path

def compile_markdown_to_pdf(
    source_file_name_without_extension: str,
    preprocessed_source_file: str,
    template_content: Optional[str] = None,
    output_pdf: Optional[str] = None,
    open_file: bool = False,
    return_binary: bool = False
) -> Union[str, Tuple[bytes, str]]:
    """Compiles a Markdown file to a PDF using pdflatex, optionally returning the PDF binary."""
    def convert_markdown_to_latex(md_path: str, tex_path: str, template_content: Optional[str] = None) -> str:
        pandoc_cmd = [
            'pandoc', md_path,
            '-s',
            '-o', tex_path,
            '--pdf-engine-opt=--quiet'
        ]

        if template_content:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tex") as tf:
                tf.write(template_content.encode('utf-8'))
                tf.flush()
                pandoc_cmd.append(f'--template={tf.name}')

        result = subprocess.run(
            pandoc_cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return tex_path, result.stderr

    def run_pdflatex(tex_file: str, output_dir: str) -> Tuple[str, str]:
        pdflatex_command = [
            'pdflatex',
            '-interaction=nonstopmode',
            '-output-directory', output_dir,
            tex_file
        ]
        result = subprocess.run(
            pdflatex_command,
            check=True,
            capture_output=True,
            text=True
        )
        # Run pdflatex twice to resolve references
        result = subprocess.run(
            pdflatex_command,
            check=True,
            capture_output=True,
            text=True
        )

        base_name = os.path.splitext(os.path.basename(tex_file))[0]
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        return pdf_path, result.stderr

    def open_pdf(pdf_path: str) -> None:
        try:
            if sys.platform.startswith('darwin'):
                subprocess.run(['open', pdf_path], check=False)
            elif os.name == 'nt':
                os.startfile(pdf_path)  # type: ignore
            elif os.name == 'posix':
                subprocess.run(['xdg-open', pdf_path], check=False)
        except Exception as e:
            print(f"Unable to open PDF automatically: {str(e)}")

    if not preprocessed_source_file.endswith('.md'):
        raise ValueError("The source file must be a Markdown (.md) file.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tex") as temp_tex_file:
        temp_tex_path = temp_tex_file.name

    temp_dir = None
    final_pdf_path = None
    pandoc_stderr = ""
    pdflatex_stderr = ""

    try:
        # Convert markdown to LaTeX
        temp_tex_path, pandoc_stderr = convert_markdown_to_latex(preprocessed_source_file, temp_tex_path, template_content)
        time.sleep(1)

        # Create temporary directory for pdflatex output
        temp_dir = tempfile.mkdtemp()
        pdf_path, pdflatex_stderr = run_pdflatex(temp_tex_path, temp_dir)
        time.sleep(1)

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF was not generated at: {pdf_path}")

        if return_binary:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            return pdf_data, f"PDF generated at: {pdf_path}\nPandoc stderr: {pandoc_stderr}\nPdflatex stderr: {pdflatex_stderr}"

        # Move PDF to final destination
        if output_pdf is None:
            pdf_basename = os.path.splitext(os.path.basename(source_file_name_without_extension))[0] + ".pdf"
            final_pdf_path = os.path.join(os.getcwd(), pdf_basename)
        else:
            final_pdf_path = output_pdf

        if os.path.exists(final_pdf_path):
            os.remove(final_pdf_path)
        os.rename(pdf_path, final_pdf_path)

        if open_file:
            open_pdf(final_pdf_path)

        return f"PDF generated at: {final_pdf_path}\nPandoc stderr: {pandoc_stderr}\nPdflatex stderr: {pdflatex_stderr}"

    finally:
        # Clean up temporary files
        if os.path.exists(temp_tex_path):
            os.remove(temp_tex_path)
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

def install_pandoc_and_latex():
    """Install pandoc and a minimal set of TeX Live packages."""
    packages = [
        "pandoc",
        "texlive-latex-base",
        "texlive-latex-recommended",
        "texlive-latex-extra",
        "texlive-fonts-recommended"
    ]

    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True, text=True)
        subprocess.run(["sudo", "apt-get", "-y", "install"] + packages, check=True, capture_output=True, text=True)
        return "Installation of pandoc and a minimal TeX Live environment completed."
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Installation failed: {e.stderr}")

def main():
    print(logo_string)

    parser = argparse.ArgumentParser(
        description="Compile a Markdown (.md) file to PDF using pandoc and pdflatex.",
        add_help=False
    )

    parser.add_argument(
        "--help",
        action="store_true",
        help="Show the help message and exit."
    )
    parser.add_argument(
        "--install_dependencies",
        action="store_true",
        help="Install pandoc and TeX Live (Ubuntu/Debian)."
    )
    parser.add_argument(
        "source_file",
        nargs="?",
        help="Path to the input Markdown file."
    )
    parser.add_argument(
        "output_pdf",
        nargs="?",
        default=None,
        help="Path to the output PDF file (optional)."
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the resulting PDF with the system's default viewer."
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Name of a built-in template to use (e.g. 'two-column')."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Evaluates the python code in the Markdown, and prints the string just before it is sent for Pandoc processing."
    )

    args = parser.parse_args()

    if args.help:
        print(help_string)
        sys.exit(0)

    if args.install_dependencies:
        print(install_pandoc_and_latex())
        print("\nDependencies installed. Re-run without --install_dependencies to compile documents.")
        sys.exit(0)

    if not args.source_file:
        print("A source markdown file is required. Try --help for usage.")
        sys.exit(1)

    if not os.path.exists(args.source_file):
        print(f"Error: No such file: {args.source_file}")
        sys.exit(1)

    # Preprocess the markdown file
    expanded_md_path = preprocess_markdown_file(args.source_file, args.test)

    # Get the base name of the file
    base_name = os.path.basename(args.source_file)
    source_file_name_without_extension = os.path.splitext(base_name)[0]

    if not args.test:
        # Compile to PDF
        result = compile_markdown_to_pdf(
            source_file_name_without_extension=source_file_name_without_extension,
            preprocessed_source_file=expanded_md_path,
            output_pdf=args.output_pdf,
            template_content=templates.get(args.template),
            open_file=args.open
        )
        print(result)

if __name__ == "__main__":
    main()
