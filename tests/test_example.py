import os
from runpy import run_path


def test_example(tmp_path_factory):
    cwd = os.getcwd()
    example_script_path = os.path.abspath('example.py')

    tmp_path = tmp_path_factory.mktemp('example')
    os.chdir(tmp_path)
    run_path(example_script_path, run_name='__main__')
    os.chdir(cwd)

    assert_same_content(tmp_path / 'example.html', 'example.html')
    assert_same_content(tmp_path / 'example.docx', 'example.docx')
    assert_same_content(tmp_path / 'example.pdf', 'example.pdf')


def assert_same_content(path_a, path_b):
    print('Comparing', path_a, path_b)
    with open(path_a, 'rb') as fp_a, open(path_b, 'rb') as fp_b:
        assert fp_a.read() == fp_b.read()
