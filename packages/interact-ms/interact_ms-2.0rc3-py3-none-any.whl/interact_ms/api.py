""" Main api routes for interact-ms
"""
from argparse import ArgumentParser
import os
import shutil
import socket
import time

import flask
from flask import request, Response, render_template, send_file, send_from_directory
from flask.json import jsonify
from flask_cors import cross_origin
from jinja2.exceptions import TemplateNotFound
import pandas as pd
import yaml

from interact_ms.clean_up import (
    clear_queue,
    cancel_job_helper,
)
from interact_ms.constants import (
    ALL_CONFIG_KEYS,
    CPUS_KEY,
    EXTRA_PROT_KEY,
    FRAGGER_MEMORY_KEY,
    FRAGGER_PATH_KEY,
    KEY_FILES,
    MHCPAN_KEY,
    INTERACT_HOME_KEY,
    INTERACT_SLURM_SCRIPT,
    QUEUE_PATH,
    RESCORE_COMMAND_KEY,
    SERVER_ADDRESS_KEY,
    SKYLINE_RUNNER_KEY,
    ZIP_PATHS,
)
from interact_ms.handle_results import (
    create_queue_fig,
    deal_with_failure,
    deal_with_queue,
    deal_with_success,
    deal_with_waiting,
    fetch_queue_and_task,
    safe_fetch,
)
from interact_ms.execute import execute_invitro_job, execute_job
from interact_ms.execute_pisces import execute_pisces, prepare_pisces
from interact_ms.utils import (
    check_pids,
    format_header_and_footer,
    generate_raw_file_table,
    generate_subset_table,
    get_task_list,
    read_meta,
)

app = flask.Flask(__name__, template_folder='templates')


@app.route('/favicon.ico')
@cross_origin()
def favicon():
    """ Endpoint sending the favicon.
    """
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )


@app.route('/static/<path:path>')
@cross_origin()
def send_static(path):
    """ Function to send static files from the static folder.
    """
    return send_from_directory('static', path)


@app.route('/interact/user/<user>', methods=['GET'])
@cross_origin()
def get_user(user):
    """ Function to check for existing user or create a new user folder.
    """
    if os.path.isdir(f'{app.config[INTERACT_HOME_KEY]}/projects/{user}'):
        projects = sorted(os.listdir(f'projects/{user}'))
        projects = [project for project in projects if not project.endswith('.zip')]
    else:
        os.mkdir(f'projects/{user}')
        projects = []
    response =  jsonify(message=projects)
    return response


@app.route('/interact-page/<page>', methods=['GET'])
@cross_origin()
def fetch_page_no_arguments(page):
    """ Endpoint serving the spi_serverive Home Page.
    """
    additional_args = format_header_and_footer(app.config[SERVER_ADDRESS_KEY])
    try:
        if page == 'view-queue':
            create_queue_fig(
                app.config[INTERACT_HOME_KEY],
                f'{app.config[INTERACT_HOME_KEY]}/locks/'
            )
            additional_args['queue_svg'] = safe_fetch(
                f'{app.config[INTERACT_HOME_KEY]}/locks/queue.svg'
            )
        return render_template(
            f'{page}.html',
            server_address=app.config[SERVER_ADDRESS_KEY],
            **additional_args
        )
    except TemplateNotFound:
        return render_template(
            '404.html',
            **additional_args,
        ), 404


@app.route('/interact-page/<page>/<user>/<project>', methods=['GET'])
@cross_origin()
def fetch_page(page, user, project):
    """ Endpoint serving the spi_serverive Home Page.
    """
    header_and_footer = format_header_and_footer(app.config[SERVER_ADDRESS_KEY])
    project_home = f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}'
    if not os.path.exists(f'{project_home}/core_metadata.yml'):
        try:
            return render_template(
                f'{page}.html',
                server_address=app.config[SERVER_ADDRESS_KEY],
                user=user,
                project=project,
                **header_and_footer,
            )
        except TemplateNotFound:
            return render_template('404.html', **header_and_footer), 404

    try:
        core_config = read_meta(project_home, 'core')
        variant = core_config['variant']
    except:
        time.sleep(3)
        core_config = read_meta(project_home, 'core')
        variant = core_config['variant']

    if page == 'proteome':
        if variant in ('standard', 'pisces'):
            page += '-standard'
        else:
            page += f'-{variant}'
    elif page == 'parameters' and variant == 'invitro':
        page += f'-{variant}'
    elif page == 'search':
        if variant == 'pisces':
            page += '-pisces'

    try:
        if page == 'subset':
            html_table = generate_subset_table(user, project, app, variant)
            return render_template(
                f'{page}.html',
                server_address=app.config[SERVER_ADDRESS_KEY],
                user=user,
                project=project,
                variant=variant,
                html_table=html_table,
                **header_and_footer,
            )
        if page == 'parameters':
            html_table = generate_raw_file_table(user, project, app, variant)
            return render_template(
                f'{page}.html',
                server_address=app.config[SERVER_ADDRESS_KEY],
                user=user,
                project=project,
                variant=variant,
                html_table=html_table,
                **header_and_footer,
            )

        return render_template(
            f'{page}.html',
            server_address=app.config[SERVER_ADDRESS_KEY],
            user=user,
            project=project,
            variant=variant,
            **header_and_footer,
        )
    except TemplateNotFound:
        return render_template('404.html', **header_and_footer), 404


@app.route('/interact/project/<user>/<project>', methods=['GET'])
@cross_origin()
def create_project(user, project):
    """ Function to create a new user project.
    """
    if not os.path.isdir(f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}'):
        os.mkdir(f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}')
    return jsonify(message='Ok')

@app.route('/interact/tasks_included/<user>/<project>', methods=['GET'])
@cross_origin()
def get_tasks(user, project):
    """ Function to check which tasks are included in the workflow.
    """
    project_home = f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}'
    variant = read_meta(project_home, 'core')['variant']
    tasks = get_task_list(user, project, app, variant)
    return jsonify(message={'tasks': tasks})

@app.route('/interact/upload/<user>/<project>/<file_type>', methods=['POST'])
@cross_origin()
def upload_file(user, project, file_type):
    """ Function to create a new user project.
    """
    home_key= app.config[INTERACT_HOME_KEY]
    pisces_flag = False
    if file_type in ['search-pisces-db', 'search-pisces-dn']:
        pisces_flag = True
        pisces_type = file_type.split('-')[-1]
        file_type = 'search'

    upload_home = f'{home_key}/projects/{user}/{project}/{file_type}'

    if not os.path.isdir(f'{home_key}/projects/{user}/{project}/{file_type}'):
        os.mkdir(f'projects/{user}/{project}/{file_type}')

    uploaded_files = request.files.getlist("files")

    if file_type == 'proteome-invitro':
        uploaded_files[0].save(
            f'{upload_home}/protSeq.fasta'
        )

        uploaded_files[1].save(
            f'{upload_home}/contams.fasta'
        )
    elif file_type == 'proteome':
        uploaded_files[0].save(
            f'{upload_home}/proteome_{uploaded_files[0].filename}'
        )
        
    elif file_type == 'proteome-select':
        uploaded_files[0].save(
            f'{upload_home}/host_{uploaded_files[0].filename}'
        )
        uploaded_files[1].save(
            f'{upload_home}/pathogen_{uploaded_files[1].filename}'
        )
        with open(
            f'{upload_home}/proteome_combined.fasta', mode='w', encoding='UTF-8',
        ) as total_file:
            for prot_file in (
                f'{upload_home}/host_{uploaded_files[0].filename}',
                f'{upload_home}/pathogen_{uploaded_files[1].filename}',
            ):
                with open(
                    prot_file, mode='r', encoding='UTF-8'
                ) as source_file:
                    for line in source_file:
                        total_file.write(line)
    elif file_type == 'search':
        if pisces_flag:
            n_files = len(uploaded_files)
            if pisces_type == 'db':
                for idx in range(n_files):
                    uploaded_files[idx].save(
                        f'{upload_home}/dbSearch_{idx}.csv'
                    )
            else:
                for idx in range(n_files):
                    if uploaded_files[idx].filename.endswith('.csv'):
                        uploaded_files[idx].save(
                            f'{upload_home}/deNovo_{idx}.csv'
                        )
                    else:
                        uploaded_files[idx].save(
                            f'{upload_home}/{uploaded_files[idx].filename}'
                        )
        else:
            # For search if there are multiple msms.txt, etc, we avoid overwriting
            for idx, u_file in enumerate(uploaded_files):
                renamed_file = f'{str(idx+1)}_' + u_file.filename.replace(" ", "_")
                u_file.save(
                    f'{upload_home}/{renamed_file}'
                )
    elif file_type == 'fragger-params':
        upload_home = f'{home_key}/projects/{user}/{project}/search'
        uploaded_files[0].save(
            f'{upload_home}/fragger_params.template'
        )
    else:
        # For raw files we preserve name
        for u_file in uploaded_files:
            u_file.save(
                f'{upload_home}/{u_file.filename}'
            )

    return jsonify(message='Ok')

@app.route('/interact/metadata', methods=['POST'])
@cross_origin()
def upload_metadata():
    """ Function for checking which files match a particular file pattern provided.
    """
    config_data = request.json
    user = config_data.pop('user')
    project = config_data.pop('project')
    metadata_type = config_data.pop('metadata_type')
    with open(
        f'projects/{user}/{project}/{metadata_type}_metadata.yml',
        'w',
        encoding='UTF-8'
    ) as yaml_out:
        yaml.dump(config_data, yaml_out)
    return jsonify(message='Ok')


@app.route('/interact/metadata/<user>/<project>/<metadata_type>', methods=['GET'])
@cross_origin()
def get_metadata(user, project, metadata_type):
    """ Function for checking which files match a particular file pattern provided.
    """
    if metadata_type == 'pisces-cryptic':
        extra_prot_folders = app.config.get(EXTRA_PROT_KEY)
        if extra_prot_folders is None:
            extra_prot_folders = {}
        return jsonify(
            message=extra_prot_folders
        )
    project_home = f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}'
    meta_dict = read_meta(project_home, metadata_type)
    return jsonify(message=meta_dict)


@app.route('/interact/checkPattern/<file_type>', methods=['POST'])
@cross_origin()
def check_file_pattern(file_type):
    """ Function for checking which files match a particular file pattern provided.
    """
    config_data = request.json
    user = config_data['user']
    project = config_data['project']
    project_home = f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}'
    if file_type in ['search-pisces', 'search-pisces-db', 'search-pisces-dn']:
        file_type = 'search'

    if not os.path.exists(f'{project_home}/{file_type}'):
        os.mkdir(f'{project_home}/{file_type}')
        return jsonify(message=[])

    all_files = os.listdir(f'{project_home}/{file_type}')

    return jsonify(message=all_files)


@app.route('/interact/clearPattern/<file_type>', methods=['POST'])
@cross_origin()
def clear_file_pattern(file_type):
    """ Function for checking which files match a particular file pattern provided.
    """
    config_data = request.json
    user = config_data['user']
    project = config_data['project']
    if file_type == 'search-pisces':
        file_type = 'search'

    shutil.rmtree(
        f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}/{file_type}'
    )
    os.mkdir(
        f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}/{file_type}'
    )
    return jsonify(message=os.listdir(f'projects/{user}/{project}/{file_type}'))


@app.route('/interact', methods=['GET'])
@cross_origin()
def interact_landing_page():
    """ Endpoint serving the starting page.
    """
    header_and_footer = format_header_and_footer(app.config[SERVER_ADDRESS_KEY])
    usernames = sorted(os.listdir(f'{app.config[INTERACT_HOME_KEY]}/projects'))
    option_list = [
        f'<option value="{username}">{username}</option>' for username in usernames
    ]
    options_html = ' '.join(option_list)
    return render_template(
        'index.html',
        server_address=app.config[SERVER_ADDRESS_KEY],
        user_list=options_html,
        **header_and_footer,
    )


@app.route('/interact/delete', methods=['POST'])
@cross_origin()
def delete_project():
    """ Function allow deletion of all project data.
    """
    config_dict = request.json
    user = config_dict['user']
    project = config_dict['project']
    home_key= app.config[INTERACT_HOME_KEY]
    project_home = f'{home_key}/projects/{user}/{project}'
    if os.path.exists(project_home):
        shutil.rmtree(project_home)
    return jsonify(
        message=(
            'Project deleted.'
        )
    )


@app.route('/interact/download/<user>/<project>', methods=['GET'])
@cross_origin()
def download_project(user, project):
    """ Function allow download of all project data.
    """
    home_key= app.config[INTERACT_HOME_KEY]
    project_home = f'{home_key}/projects/{user}/{project}'
    if os.path.exists(f'{project_home}/config.yml'):
        shutil.copyfile(f'{project_home}/config.yml', f'{project_home}/outputFolder/config.yml')
    if not os.path.exists(f'{project_home}/outputFolder'):
        os.mkdir((f'{project_home}/outputFolder'))
    shutil.make_archive(f'{project_home}/outputFolder', 'zip', f'{project_home}/outputFolder')
    return send_file(f'{project_home}/outputFolder.zip', mimetype='zip', as_attachment=True)


@app.route('/interact/cancel', methods=['POST'])
@cross_origin()
def cancel_job():
    """ Function to cancel an job execution.
    """
    config_dict = request.json

    user = config_dict.get('user')
    project = config_dict.get('project')
    job_id = config_dict.get('jobID')
    if job_id is not None:
        job_id = int(job_id)

    cancel_message = cancel_job_helper(app.config[INTERACT_HOME_KEY], user, project, job_id)

    return jsonify(message=cancel_message)


@app.route('/interact/execute', methods=['POST'])
@cross_origin()
def run_interact_job():
    """ Run execute a pipeline run.
    """
    config_dict = request.json
    user = config_dict['user']
    project = config_dict['project']
    project_home = f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}'
    if 'includedTasks' in config_dict:
        tasks = config_dict['includedTasks']
        config_dict = read_meta(project_home, 'parameters')
        config_dict['user'] = user
        config_dict['project'] = project
    else:
        tasks = None


    response = jsonify(
        message=f'http://{app.config[SERVER_ADDRESS_KEY]}:5000/interact/{user}/{project}/results'
    )

    try:
        # If task is already running or queued, do nothing:
        if check_pids(
            project_home, app.config.get(INTERACT_SLURM_SCRIPT) is not None,
        ) == 'waiting':
            return response

        variant = read_meta(project_home, 'core')['variant']
        if variant == 'invitro':
            execute_invitro_job(app.config, project_home, config_dict, tasks)
        elif variant == 'pisces':
            execute_pisces(app.config, project_home, config_dict, tasks)
        else:
            execute_job(app.config, project_home, config_dict, tasks)

        

    except Exception as err:
        return jsonify(message=f'interact-ms failed with error code: {err}')

    return response

@app.route('/interact/<user>/<project>/<workflow>', methods=['GET'])
@cross_origin()
def check_results(user, project, workflow):
    """ Check results.
    """
    project_home = f'{app.config[INTERACT_HOME_KEY]}/projects/{user}/{project}'
    server_address = app.config[SERVER_ADDRESS_KEY]
    header_and_footer = format_header_and_footer(app.config[SERVER_ADDRESS_KEY])

    if not os.path.exists(project_home):
        return render_template('404.html', **header_and_footer), 404

    time.sleep(0.5)
    status = check_pids(project_home, app.config.get(INTERACT_SLURM_SCRIPT) is not None)

    # Task incomplete - either running or queueing (or total failure)
    if status == 'waiting':
        queue_df, task_id = fetch_queue_and_task(
            project_home, app.config[INTERACT_HOME_KEY],
            app.config.get(INTERACT_SLURM_SCRIPT) is not None,
        )

        if not queue_df.shape[0]:
            time.sleep(2)
            queue_df, task_id = fetch_queue_and_task(
                project_home, app.config[INTERACT_HOME_KEY],
                app.config.get(INTERACT_SLURM_SCRIPT) is not None,
            )

        if not queue_df.shape[0]:
            return deal_with_failure(
                project_home,
                server_address,
                user,
                project,
                workflow,
                header_and_footer
            )

        if int(queue_df['taskID'].iloc[0]) == task_id:
            return deal_with_waiting(
                project_home,
                server_address,
                user,
                project,
                header_and_footer,
            )

        return deal_with_queue(
            app.config[INTERACT_HOME_KEY], project_home, server_address,
            user, project, header_and_footer,
        )

    # Task complete : either in success or failure.
    variant = read_meta(project_home, 'core')['variant']

    if variant == 'pathogen':
        pep_seek_visible = 'visible'
        key_file = 'PEPSeek/potentialEpitopeCandidates.xlsx'
    elif variant == 'invitro':
        pep_seek_visible = 'hidden'
        key_file = 'filtered_finalAssignments.csv'
    elif variant == 'standard':
        pep_seek_visible = 'hidden'
        key_file = 'inspire-report.html'
    else:
        pep_seek_visible = 'hidden'
        key_file = 'pisces-report.html'

    if os.path.exists(f'{project_home}/outputFolder/{key_file}'):
        return deal_with_success(
            project_home,
            server_address,
            user,
            project,
            workflow,
            variant,
            pep_seek_visible,
            header_and_footer,
        )
    return deal_with_failure(
        project_home,
        server_address,
        user,
        project,
        workflow,
        header_and_footer,
    )


@app.route('/interact/get_results/<user>/<project>/<workflow>', methods=['GET'])
@cross_origin()
def get_results_file(user, project, workflow):
    """ Function to return the results files from any interact workflow.
    """
    home_key= app.config[INTERACT_HOME_KEY]
    server_address = app.config[SERVER_ADDRESS_KEY]
    project_home = f'{home_key}/projects/{user}/{project}'

    # The quantification results require a zip archive
    if workflow in ('quantification', 'PEPSeek', 'piscesFinal', 'piscesDetails'):
        if os.path.exists(f'{project_home}/{ZIP_PATHS[workflow]}.zip'):
            os.remove(f'{project_home}/{ZIP_PATHS[workflow]}.zip')

        shutil.make_archive(
            f'{project_home}/{ZIP_PATHS[workflow]}',
            'zip',
            f'{project_home}/{ZIP_PATHS[workflow]}',
        )
    key_file = KEY_FILES[workflow]
    core_config = read_meta(project_home, 'core')
    variant = core_config['variant']
    if variant == 'invitro' and workflow == 'peptides':
        key_file = 'outputFolder/filtered_finalAssignments.csv'
    # The following results require the relevant results file to be sent:
    if workflow in (
        'epitopePlots',
        'psms',
        'peptides',
        'executionLog',
        'PEPSeek',
        'quantification',
        'piscesFinal',
        'piscesDetails',
        'piscesPlots',
        'piscesMetrics',
    ):
        if os.path.exists(f'{project_home}/{key_file}'):
            kwargs = {}
            if key_file.endswith('.zip'):
                kwargs['mimetype'] = 'zip'
                kwargs['as_attachment'] = True
            return send_file(f'{project_home}/{key_file}', **kwargs)

    # The following send html reports
    if workflow in (
        'epitopeReport', 'hostReport', 'performance', 'quantReport',
        'invitroPlots', 'piscesReport', 'piscesQcReport',
    ):
        if workflow == 'invitroPlots':
            return send_from_directory(project_home, KEY_FILES[workflow])
        if (contents := safe_fetch(f'{project_home}/{KEY_FILES[workflow]}')):
            if workflow == 'epitopeReport':
                contents = contents.replace(
                    f'{project_home}/outputFolder/PEPSeek/spectralPlots.pdf',
                    f'http://{server_address}:5000/interact/get_results/{user}/{project}/epitopePlots',
                )
            if workflow == 'piscesQcReport':
                contents = contents.replace(
                    f'{project_home}/outputFolder/nonCanonicalPlots.pdf',
                    f'http://{server_address}:5000/interact/get_results/{user}/{project}/piscesPlots',
                )

            return contents

    return Response()

def get_arguments():
    """ Function to collect command line arguments.

    Returns
    -------
    args : argparse.Namespace
        The parsed command line arguments.
    """
    parser = ArgumentParser(description='interact-ms provides easy access to tools for mass spectrometry analysis.')

    parser.add_argument(
        '--config_file',
        required=True,
        help='All configurations.',
    )

    return parser.parse_args()


def main():
    """ Main function to run interact-ms.
    """
    args = get_arguments()

    with open(args.config_file, 'r', encoding='UTF-8') as stream:
        config_dict = yaml.safe_load(stream)
    for config_key in config_dict:
        if config_key not in ALL_CONFIG_KEYS:
            raise ValueError(f'Unrecognised key {config_key} found in config file.')

    for config_key in ALL_CONFIG_KEYS:
        app.config[config_key] = config_dict.get(config_key, None)

    app.config[INTERACT_HOME_KEY] = os.getcwd()
    app.config[INTERACT_HOME_KEY] = app.config[INTERACT_HOME_KEY].replace(
        '\\', '/'
    )
    if not os.path.exists('projects'):
        os.mkdir('projects')
    if not os.path.exists('locks'):
        os.mkdir('locks')
    if not os.path.exists(QUEUE_PATH.format(
        home_key=app.config[INTERACT_HOME_KEY])
    ):
        empty_queue_df = pd.DataFrame({
            'user': [],
            'project': [],
            'taskID': [],
            'status': [],
        })
        empty_queue_df.to_csv(QUEUE_PATH.format(
            home_key=app.config[INTERACT_HOME_KEY]), index=False
        )

    host_name = socket.gethostname()
    app.config[SERVER_ADDRESS_KEY] = host_name

    app.config[MHCPAN_KEY] = config_dict.get(MHCPAN_KEY)
    app.config[FRAGGER_PATH_KEY] = config_dict.get(FRAGGER_PATH_KEY)
    app.config[FRAGGER_MEMORY_KEY] = config_dict.get(FRAGGER_MEMORY_KEY)
    app.config[CPUS_KEY] = config_dict.get(CPUS_KEY, 1)
    app.config[SKYLINE_RUNNER_KEY] = config_dict.get(SKYLINE_RUNNER_KEY)
    app.config[INTERACT_SLURM_SCRIPT] = config_dict.get(INTERACT_SLURM_SCRIPT)
    app.config[RESCORE_COMMAND_KEY] = config_dict.get(RESCORE_COMMAND_KEY, 'percolator')
    app.config['containerMethod'] = config_dict.get('containerMethod', 'apptainer')
    app.config['apptainerImage'] = config_dict.get('apptainerImage')
    app.config['piscesTreeSize'] = config_dict.get('piscesTreeSize', 500)
    if app.config[SKYLINE_RUNNER_KEY] is not None:
         app.config[SKYLINE_RUNNER_KEY] = app.config[SKYLINE_RUNNER_KEY].replace(
            '\\', '/'
        )


    print('\n\033[1m\033[92m\nAddresses to navigate to')
    print(f'If you are running interact-ms on a remote server navigate to \033[96mhttp://{host_name}:5000/interact-page/home\033[92m')
    print(f'If you are running interact-ms on your local machine navigate to \033[96mhttp://127.0.0.1:5000/interact-page/home\033[92m')
    print('\n\033[0m\n')
    app.run(host='0.0.0.0', debug = False)

    print('Quitting, first clearing queue.')
    clear_queue(app.config[INTERACT_HOME_KEY])


if __name__ == '__main__':
    main()
