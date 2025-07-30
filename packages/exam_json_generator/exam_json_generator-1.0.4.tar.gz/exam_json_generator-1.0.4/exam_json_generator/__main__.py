from .extractor import extractor_json
import argparse
import os
import sys
import webbrowser


def main():

    parser = argparse.ArgumentParser(
        description="Extracts questions from a .DOCX file and saves them in a .JSON format."
    )
    parser.add_argument("origin_dir", nargs='?',help="Path to the input .docx file")
    parser.add_argument("output_dir",nargs='?', help="Path to the output .json file")    
    parser.add_argument("--show-example", action="store_true", help="Display the path to the example .docx file")


    args = parser.parse_args()


    if args.show_example:
        example_path = os.path.abspath("ejemplo_formato_valido.docx")
        print(example_path)
        print(f"📄 Example .docx location: {example_path}")
        
        # Opcional: abrir el archivo si existe
        if os.path.exists(example_path):
            webbrowser.open(f"file://{example_path}")
            
        else:
            print("❌ The example file does not exist.")
        sys.exit(0)

    if not args.origin_dir or not os.path.isdir(args.origin_dir):
        print(f"❌ Invalid input directory: {args.origin_dir}")
        print("📌 Please provide a valid and existing directory containing .docx files.")
        sys.exit(1)

    # Check output path
    if not args.output_dir:
        print("❌ Output directory cannot be empty.")
        sys.exit(1)

    # If output path doesn't exist, offer to create it
    if not os.path.exists(args.output_dir):
        print(f"⚠️ Output directory does not exist: {args.output_dir}")
        try:
            os.makedirs(args.output_dir)
            print(f"📁 Created output directory: {args.output_dir}")
        except Exception as e:
            print(f"❌ Failed to create output directory: {e}")
            sys.exit(1)
    elif not os.path.isdir(args.output_dir):
        print(f"❌ Output path exists but is not a directory: {args.output_dir}")
        sys.exit(1)

    print(f"📥 Reading: {args.origin_dir}")
    print(f"📤 Saving to: {args.output_dir}")

    extractor_json(args.origin_dir, args.output_dir)
    
if __name__=='__main__':
    main()