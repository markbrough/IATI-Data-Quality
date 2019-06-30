from csv import DictWriter
from glob import glob
from os.path import dirname, join

from flask import current_app
from bdd_tester import BDDTester


def load_tests():
    """Load the index tests."""
    base_path = join(dirname(current_app.root_path),
                     'index_indicator_definitions', 'test_definitions')
    step_definitions = join(base_path, 'step_definitions.py')
    feature_filepaths = glob(join(base_path, '*', '*.feature'))
    tester = BDDTester(step_definitions)
    all_tests = [t for feature_filepath in feature_filepaths
                 for t in tester.load_feature(feature_filepath).tests]

    # Remove the current data condition from tests.
    for test in all_tests:
        test.steps = [x for x in test.steps
                      if not (x.step_type == 'given' and
                              x.text == 'the activity is current')]

    return all_tests


def load_current_data_test():
    """Load the current data test."""
    base_path = join(dirname(current_app.root_path),
                     'index_indicator_definitions', 'test_definitions')
    step_definitions = join(base_path, 'step_definitions.py')
    tester = BDDTester(step_definitions)
    return tester.load_feature(
        join(base_path, 'current_data.feature')).tests[0]


def slugify(some_text):
    """Return a slugified version of an input string."""
    def safe_char(char):
        return char.lower() if char.isalnum() else '_'
    return ''.join(safe_char(char) for char in some_text).strip('_')


def run_test(test, publisher, output_path, test_condition, **kwargs):
    """Run test for a given publisher, and output results to a CSV."""
    fieldnames = ['dataset', 'identifier', 'index', 'result',
                  'hierarchy', 'explanation']
    tags = test.tags + test.feature.tags
    if 'iati-activity' not in tags and 'iati-organisation' not in tags:
        # Skipping test (it’s not tagged as activity or organisation level)
        return None

    with open(output_path, 'w') as handler:
        writer = DictWriter(handler, fieldnames=fieldnames)
        writer.writeheader()
        if 'iati-activity' in tags:
            if test_condition:
                items = publisher.activities.where(xpath=test_condition)
            else:
                items = publisher.activities
        elif 'iati-organisation' in tags:
            items = publisher.organisations
        for item in items:
            result, explanation = test(item.etree, bdd_verbose=True, **kwargs)
            hierarchy = item.etree.get('hierarchy')
            if not hierarchy:
                hierarchy = '1'
            writer.writerow({
                'dataset': item.dataset.name,
                'identifier': item.id,
                'index': item.etree.getparent().index(item.etree) + 1,
                'result': str(result),
                'hierarchy': hierarchy,
                'explanation': str(explanation) if not result else '',
            })
