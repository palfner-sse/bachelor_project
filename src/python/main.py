import argparse
import importlib
import json

from ai_generator.ai_generator import run_ai_generator
from besser_java_generator.java_generator import JavaGenerator
from model_analyzer import analyze_model


"""
Dynamically loads and executes a B-UML model Python file and returns its domain_model variable.

Args:
    path : str  - Absolute or relative path to the model.py file

Return:
    DomainModel - The domain_model object defined in the loaded file
"""
def load_domain_model(path: str):
    spec = importlib.util.spec_from_file_location("model", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.domain_model


"""
Entry point for the toolchain.

Provides a CLI to either generate Java source files from a B-UML model
or run the AI-powered multi-agent system to migrate an existing codebase
in response to a model change.

Usage:
    Java generator:
        python main.py -b <model.py> -c <output_dir> -j

    AI generator:
        python main.py -b <before_model.py> -a <after_model.py> -c <codebase_dir>

Arguments:
    -b / --before   : Path to the B-UML model file. Used as the sole input for the Java
                      generator, or as the before-state model for the AI generator.
    -a / --after    : Path to the B-UML model file after the change. Required for the AI generator.
    -c / --codebase : Path to the codebase directory. Output directory for the Java generator,
                      or the directory the AI generator reads and modifies.
    -j / --java     : Flag to use the Java generator. Omit to use the AI generator instead.
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--before", required=True, help="path to the B-UML model file; used as the input model for the Java generator or as the before model for the AI generator")
    parser.add_argument("-a", "--after", required=False, help="path to the B-UML model file after the change; only required when using the AI generator")
    parser.add_argument("-c", "--codebase", required=False, help="path to the codebase directory; used by the AI generator as the directory to read and modify, or by the Java generator as the output directory for generated .java files")
    parser.add_argument("-j", "--java", action="store_true", required=False, help="use the Java generator instead of the AI generator")
    parser.add_argument("--count", action="store_true", required=False, help="count changeable elements in the model instead of running a generator")

    args = parser.parse_args()

    if args.count:
        model = load_domain_model(args.before)
        result = analyze_model(model)
        print(json.dumps(result, indent=2))
    elif args.java:
        if not args.codebase:
            parser.error("-c/--codebase is required when using the Java generator")
        JavaGenerator(model=load_domain_model(args.before), output_dir=args.codebase).generate()
    else:
        if not args.after:
            parser.error("-a/--after is required when using the AI generator")
        if not args.codebase:
            parser.error("-c/--codebase is required when using the AI generator")
        run_ai_generator(args.before, args.after, args.codebase)
