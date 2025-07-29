import sys
import subprocess
import os
import tempfile
import time
import argparse
import shutil
from typing import Optional

from md2ltx.app.constants import logo_string, help_string, templates
from md2ltx.app.python_evaluation import evaluate_python_in_markdown_string


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
    open_file: bool = False
) -> None:
    """Compiles a Markdown file to a PDF using pdflatex, optionally saving or opening the file."""

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

        subprocess.run(
            pandoc_cmd,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return tex_path

    def run_pdflatex(tex_file: str, output_dir: str) -> str:
        pdflatex_command = [
            'pdflatex',
            '-interaction=nonstopmode',
            '-output-directory', output_dir,
            tex_file
        ]
        subprocess.run(pdflatex_command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(pdflatex_command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        base_name = os.path.splitext(os.path.basename(tex_file))[0]
        return os.path.join(output_dir, f"{base_name}.pdf")

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
        print("Error: The source file must be a Markdown (.md) file.")
        sys.exit(1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tex") as temp_tex_file:
        temp_tex_path: str = temp_tex_file.name

    temp_dir = None
    final_pdf_path = None

    try:
        convert_markdown_to_latex(preprocessed_source_file, temp_tex_path, template_content)
        time.sleep(1)

        temp_dir = tempfile.mkdtemp()
        generated_pdf = run_pdflatex(temp_tex_path, temp_dir)
        time.sleep(1)

        if not os.path.exists(generated_pdf):
            print("\nPDF was not generated as expected.")
            sys.exit(1)

        if output_pdf is None:
            pdf_basename = os.path.splitext(os.path.basename(source_file_name_without_extension))[0] + ".pdf"
            final_pdf_path = os.path.join(os.getcwd(), pdf_basename)
        else:
            final_pdf_path = output_pdf

        if os.path.exists(final_pdf_path):
            os.remove(final_pdf_path)
        os.rename(generated_pdf, final_pdf_path)

        if open_file:
            open_pdf(final_pdf_path)

        print(f"PDF generated at: {final_pdf_path}")

    except subprocess.CalledProcessError as e:
        print(f"\nError during compilation: {e}")
        sys.exit(1)

    finally:
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

    print("Attempting to install pandoc and a minimal TeX Live set of packages...")
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "-y", "install"] + packages, check=True)
        print("Installation of pandoc and a minimal TeX Live environment completed.")
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")


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
        help="Path to the output PDF file (optional). If omitted, a temp PDF is created in the current directory and removed afterward."
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
        install_pandoc_and_latex()
        print("\nDependencies installed. Re-run without --install_dependencies to compile documents.")
        sys.exit(0)

    if not args.source_file:
        print("A source markdown file is required. Try --help for usage.")
        sys.exit(1)

    if not os.path.exists(args.source_file):
        print(f"Error: No such file: {args.source_file}")
        sys.exit(1)

    # Extract template content if a template name is provided
    template_content = None
    if args.template:
        template_content = templates.get(args.template)
        if not template_content:
            print(f"Error: No such template '{args.template}' available.")
            sys.exit(1)

    # Preprocess the markdown file
    expanded_md_path = preprocess_markdown_file(args.source_file, args.test)

    # get the base name of the file (e.g., file.md)
    base_name = os.path.basename(args.source_file)
    # split the base name to remove the extension (e.g., ['file', 'md'])
    source_file_name_without_extension = os.path.splitext(base_name)[0]

    if not args.test:
        # Compile to PDF using the preprocessed file and resolved template content
        compile_markdown_to_pdf(
            source_file_name_without_extension=source_file_name_without_extension,
            preprocessed_source_file=expanded_md_path,
            output_pdf=args.output_pdf,
            template_content=template_content,
            open_file=args.open
        )


if __name__ == "__main__":
    main()
