import ast
import pathlib
import unittest


def read_setup_options():
    setup_path = pathlib.Path(__file__).resolve().parents[1] / "setup.py"
    tree = ast.parse(setup_path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "OPTIONS":
                    return ast.literal_eval(node.value)
    raise AssertionError("OPTIONS not found in setup.py")


class SetupOptionsTests(unittest.TestCase):
    def test_excludes_do_not_remove_py2app_runtime_dependencies(self):
        options = read_setup_options()
        excludes = set(options.get("excludes", []))
        self.assertNotIn("multiprocessing", excludes)
        self.assertNotIn("concurrent", excludes)
        self.assertNotIn("xml", excludes)


if __name__ == "__main__":
    unittest.main()
