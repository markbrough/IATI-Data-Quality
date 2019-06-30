import csv
from os import listdir, makedirs
from os.path import exists, join, isdir
import shutil

from flask import current_app
from flask.cli import with_appcontext
import click
import iatikit

from ..core import models
from . import utils


@click.group('iati')
def iati_cli():
    """Automated test commands."""
    pass


@iati_cli.command('download')
@with_appcontext
def download_iati_data():
    """Download a snapshot of all IATI data."""
    click.echo('Fetching a snapshot of *all* data from the IATI registry ...')
    iatikit.download.data()


@iati_cli.command('import')
@with_appcontext
def import_iati_data():
    """Import the relevant data from the downloaded IATI snapshot."""

    if models.Organisation.query.count() == 0:
        click.secho('Error: No organisations to fetch data for.',
                    fg='red', err=True)
        click.echo('Perhaps you need to import some, using:', err=True)
        click.echo('\n    $ flask setup orgs\n', err=True)
        raise click.Abort()

    updated_on = iatikit.data().last_updated.date()
    input_path = iatikit.data().path
    output_path = join(current_app.config.get('IATI_DATA_PATH'), str(updated_on))

    click.echo('Copying files into place ...')
    click.echo(f'Output path: {output_path}')

    if exists(output_path):
        click.secho('Error: Output path exists.', fg='red', err=True)
        raise click.Abort()
    makedirs(output_path)

    shutil.copy(join(input_path, 'metadata.json'),
                join(output_path, 'metadata.json'))

    with click.progressbar(models.Organisation.all()) as all_organisations:
        for organisation in all_organisations:
            if not organisation.registry_slug:
                # if the org isn’t an IATI publisher, skip
                continue
            # Copy data files into place
            shutil.copytree(join(input_path, 'data', organisation.registry_slug),
                            join(output_path, 'data', organisation.id))
            # Copy metadata files into place
            shutil.copytree(join(input_path, 'metadata', organisation.registry_slug),
                            join(output_path, 'metadata', organisation.id))


@iati_cli.command('test')
@click.option('--date', default='latest',
              help='Date of the data to test, in YYYY-MM-DD. ' +
                   'Defaults to most recent.')
@click.option('--refresh/--no-refresh', default=True,
              help='Refresh schema and codelists.')
@with_appcontext
def run_iati_tests(date, refresh):
    """Test a set of imported IATI data."""

    iati_data_path = current_app.config.get('IATI_DATA_PATH')
    iati_result_path = current_app.config.get('IATI_RESULT_PATH')
    try:
        snapshot_dates = listdir(join(iati_data_path))
        if date == 'latest':
            snapshot_date = max(snapshot_dates)
        else:
            if not exists(join(iati_data_path, date)):
                raise ValueError
            snapshot_date = date
    except ValueError:
        if date:
            click.secho(f'Error: No IATI data found for given date ({date}).',
                        fg='red', err=True)
        else:
            click.secho('Error: No IATI data to test.', fg='red', err=True)
        click.echo('Perhaps you need to download some, using:', err=True)
        click.echo('\n    $ flask iati download\n', err=True)
        raise click.Abort()

    snapshot_xml_path = join(iati_data_path, snapshot_date)
    root_output_path = join(iati_result_path, snapshot_date)

    if exists(root_output_path):
        click.secho('Error: Output path exists.', fg='red', err=True)
        raise click.Abort()

    if refresh:
        click.echo('Downloading latest schemas and codelists ...')
        iatikit.download.standard()
    codelists = iatikit.codelists()

    click.echo('Loading tests ...')
    all_tests = utils.load_tests()
    all_tests.append(utils.load_current_data_test())

    click.echo(f'Testing IATI data snapshot ({snapshot_date}) ...')
    publishers = iatikit.data(path=snapshot_xml_path).publishers
    for publisher in publishers:
        org = models.Organisation.find(publisher.name)
        if not org:
            click.secho(f'Error: Publisher "{publisher.name}" not ' +
                        f'found in database. Database and XML ' +
                        f'may be out of sync.',
                        fg='red', err=True)
            raise click.Abort()
        click.echo(f'Testing organisation: {org.name} ({org.id}) ...')
        output_path = join(root_output_path, org.id)
        makedirs(output_path, exist_ok=True)
        for test in all_tests:
            output_filepath = join(output_path,
                                   utils.slugify(test.name) + '.csv')
            click.echo(f'  {test} ...')
            utils.run_test(test, publisher, output_filepath,
                           org.test_condition, codelists=codelists,
                           today=snapshot_date)


@iati_cli.command('summarize')
@click.option('--date', default='latest',
              help='Date of the data to summarize, in YYYY-MM-DD. ' +
                   'Defaults to most recent.')
@with_appcontext
def aggregate_results(date):
    """Summarize results of IATI data tests."""

    iati_result_path = current_app.config.get('IATI_RESULT_PATH')
    try:
        result_dates = listdir(join(iati_result_path))
        if date == 'latest':
            result_date = max(result_dates)
        else:
            if not exists(join(iati_result_path, date)):
                raise ValueError
            result_date = date
    except ValueError:
        if date:
            click.secho(f'Error: No IATI results found for given date ({date}).',
                        fg='red', err=True)
        else:
            click.secho('Error: No IATI results to summarize.', fg='red', err=True)
        click.echo('Perhaps you need to run tests, using:', err=True)
        if date:
            click.echo(f'\n    $ flask iati test --date {date}\n', err=True)
        else:
            click.echo('\n    $ flask iati test\n', err=True)
        raise click.Abort()

    click.echo('Loading tests ...')
    all_tests = utils.load_tests()
    current_data_test = utils.load_current_data_test()

    snapshot_result_path = join(iati_result_path, result_date)

    click.echo(f'Summarizing results from IATI data snapshot ({result_date}) ...')
    publishers = [x for x in listdir(snapshot_result_path)
                  if isdir(join(snapshot_result_path, x))]
    for publisher_name in publishers:
        org = models.Organisation.find(publisher_name)
        if not org:
            click.secho(f'Error: Publisher "{publisher_name}" not ' +
                        f'found in database. Database and XML ' +
                        f'may be out of sync.',
                        fg='red', err=True)
            raise click.Abort()
        click.echo(f'Summarizing results for organisation: ' +
                   f'{org.name} ({org.id}) ...')
        for test in all_tests:
            result_filepath = join(snapshot_result_path, org.id,
                                   utils.slugify(test.name) + '.csv')
            if not exists(result_filepath):
                continue
            with open(result_filepath) as handler:
                current_dataset = None
                for row in csv.DictReader(handler):
                    if not current_dataset:
                        dataset_test_results = {}
                        current_dataset = row['dataset']
                    elif current_dataset != row['dataset']:
                        for hierarchy, scores in dataset_test_results.items():
                            print('Aggregation: All data')
                            print(f'Dataset: {current_dataset}')
                            print(f'Test: {test.name}')
                            print(f'Publisher: {org.id}')
                            print(f'Hierarchy: {hierarchy}')
                            total = sum(scores.values())
                            score = 100. * scores['pass'] / total if total > 0 else 0
                            print(f'Score: {score}')
                            print(f'Total: {total}')
                        dataset_test_results = {}
                        current_dataset = row['dataset']
                    hierarchy = row['hierarchy']
                    if hierarchy not in dataset_test_results:
                        dataset_test_results[hierarchy] = {
                            'pass': 0,
                            'fail': 0,
                        }
                    result = row['result']
                    if result == 'not relevant':
                        continue
                    dataset_test_results[hierarchy][result] += 1
