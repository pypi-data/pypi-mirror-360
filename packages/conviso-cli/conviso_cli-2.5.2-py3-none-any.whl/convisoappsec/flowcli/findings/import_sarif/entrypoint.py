import click
import click_log
import json
import os
from base64 import b64decode
from re import search as regex_search
from copy import deepcopy as clone
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import LOGGER
from convisoappsec.flowcli.requirements_verifier import RequirementsVerifier
from convisoappsec.flow.graphql_api.beta.models.issues.sast import (CreateSastFindingInput)
from convisoappsec.flow.graphql_api.beta.models.issues.sca import CreateScaFindingInput
from convisoappsec.common.graphql.errors import ResponseError

click_log.basic_config(LOGGER)


@click.command()
@click.option(
    "-i",
    "--input-file",
    required=True,
    type=click.Path(exists=True),
    help='The path to SARIF file.',
)
@click.option(
    "--company-id",
    required=False,
    envvar=("CONVISO_COMPANY_ID", "FLOW_COMPANY_ID"),
    help="Company ID on Conviso Platform",
)
@click.option(
    "-r",
    "--repository-dir",
    default=".",
    show_default=True,
    type=click.Path(
        exists=True,
        resolve_path=True,
    ),
    required=False,
    help="The source code repository directory.",
)
@click.option(
    '--asset-name',
    required=False,
    envvar=("CONVISO_ASSET_NAME", "FLOW_ASSET_NAME"),
    help="Provides a asset name.",
)
@help_option
@pass_flow_context
@click.pass_context
def import_sarif(context, flow_context, input_file, company_id, repository_dir, asset_name):
    context.params['company_id'] = company_id if company_id is not None else None
    context.params['repository_dir'] = repository_dir

    prepared_context = RequirementsVerifier.prepare_context(clone(context))
    asset_id = prepared_context.params['asset_id']

    try:
        conviso_api = flow_context.create_conviso_api_client_beta()
        LOGGER.info("💬 Starting the import process for the SARIF file.")
        parse_sarif_file(conviso_api, asset_id, input_file)
    except Exception as e:
        LOGGER.error(f"❌ Error during SARIF file import: {str(e)}")
        raise Exception("SARIF file import failed. Please contact support and provide the SARIF file for assistance.")


def parse_sarif_file(conviso_api, asset_id, sarif_file):
    cleaned_file = clean_file(sarif_file)

    with open(cleaned_file) as file:
        sarif_data = json.load(file)

        if sarif_data.get('runs'):
            driver_name = sarif_data['runs'][0].get('tool', {}).get('driver', {}).get('name', '')
            if driver_name in {'GitHub CodeQL', 'CodeQL'}:
                parse_code_ql(conviso_api, asset_id, cleaned_file)

    sarif_infos = []

    for run in sarif_data['runs']:
        for rule in run.get('tool', {}).get('driver', {}).get('rules', []):
            id = rule.get('id')
            name = rule.get('name')
            references = rule.get('helpUri')
            description = rule.get('help', {}).get('text', None)

            result = {
                "id": id,
                "name": name,
                "references": references,
                "description": description
            }

            sarif_infos.append(result)

    for run in sarif_data['runs']:
        for result in run.get('results', []):
            title = None
            references = None
            description = None
            cve = None

            matching_info = next((info for info in sarif_infos if info['id'] == result['ruleId']), None)
            if matching_info:
                title = matching_info['name']
                references = matching_info['references']
                description = matching_info['description']

            if title is None:
                title = result.get('message').get('text', 'No title provided')

            if description is None:
               description = result.get('message', {}).get('text', 'No description provided')

            vulnerable_line = result.get('locations', {})[0].get('physicalLocation', {}).get('region', {}).get('startLine')
            severity = result.get('level', 'Unknown')
            file_name = result.get('locations', {})[0].get('physicalLocation', {}).get('artifactLocation', {}).get('uri')
            code_snippet = result.get('locations', {})[0].get('physicalLocation', {}).get('contextRegion', {}).get('snippet', {}).get('text', '')
            first_line = result.get('locations', {})[0].get('physicalLocation', {}).get('region', {}).get('startLine', 1)

            if "(sca)" in result.get('ruleId'):
                title = result.get('message', {}).get('text')
                package = title.split(':')[1].split(' ')[0]
                version = package.split('-')[-1]
                cve = title.split(' ')[1].strip('()')

                create_sca_vulnerabilities(
                    conviso_api, asset_id, title, references, description,
                    severity, file_name, first_line, package, version, cve
                )

            if "(sast)" in result.get('ruleId'):
                create_sast_vulnerabilities(
                    conviso_api, asset_id, title, references, description, vulnerable_line, severity, file_name,
                    code_snippet, first_line, cve
                )

    LOGGER.info("✅ SARIF file import completed successfully.")

def parse_code_ql(conviso_api, asset_id, sarif_file):
    """Parses a SARIF file and extracts specific fields."""
    results = []

    package = None
    version = None

    try:
        with open(sarif_file, mode="r", encoding="utf-8") as f:
            sarif_data = json.load(f)

        for run in sarif_data.get('runs', []):
            for result in run.get('results', []):
                rule = result.get('rule')
                title = rule.get('shortDescription', {}).get('text') or result.get('ruleId', "No Title")
                references = [r.get('url') for r in rule.get('references', [])] if rule else []
                description = result.get('message', {}).get('text')
                severity = result.get('level', 'Unknown')

                locations = result.get('locations', [])
                file_name = None
                vulnerable_line = None
                first_line = None
                code_snippet = ""

                if locations:
                    location = locations[0]
                    physical_location = location.get('physicalLocation')
                    if physical_location:
                        file_name = physical_location.get('artifactLocation', {}).get('uri')
                        region = physical_location.get('region')
                        if region:
                            vulnerable_line = region.get('startLine')
                            first_line = region.get('startLine')

                            if file_name and os.path.exists(file_name) and vulnerable_line is not None:
                                try:
                                    with open(file_name, 'r', encoding='utf-8') as source_file:
                                        lines = source_file.readlines()
                                        start_line = max(0, vulnerable_line - 3)
                                        end_line = min(len(lines), vulnerable_line + 2)
                                        code_snippet = "".join(lines[start_line:end_line]).strip()
                                except (FileNotFoundError, IndexError, UnicodeDecodeError) as e:
                                    print(f"Error extracting code snippet from {file_name}: {e}")
                                    code_snippet = ""

                cve = ''
                related_locations = result.get('relatedLocations', [])
                for related_location in related_locations:
                    message = related_location.get('message', {}).get('text', '')
                    if message.startswith("CVE-"):
                        cve = message
                        break

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error parsing SARIF file: {e}")
        return []

    if package and version:
        pass
        # create SCA
    else:
        create_sast_vulnerabilities(
            conviso_api, asset_id, title, references, description, vulnerable_line, severity, file_name,
            code_snippet, first_line, cve
        )

def create_sast_vulnerabilities(conviso_api, asset_id, *args):
    title, references, description, vulnerable_line, severity, file_name, code_snippet, first_line, cve = args

    issue_model = CreateSastFindingInput(
        asset_id=asset_id,
        file_name=file_name,
        vulnerable_line=vulnerable_line,
        title=title,
        description=description,
        severity=severity,
        commit_ref=None,
        deploy_id=None,
        code_snippet=parse_code_snippet(code_snippet),
        reference=parse_conviso_references(references),
        first_line=first_line,
        category=None,
        original_issue_id_from_tool=None
    )

    try:
        conviso_api.issues.create_sast(issue_model)
    except ResponseError as error:
        if error.code == 'RECORD_NOT_UNIQUE':
            pass
    except Exception:
        pass


def create_sca_vulnerabilities(conviso_api, asset_id, *args):
    title, references, description, severity, file_name, first_line, package, version, cve = args

    issue_model = CreateScaFindingInput(
        asset_id=asset_id,
        title=title,
        description=description,
        severity=severity,
        solution="Update to the last package version.",
        reference=references,
        file_name=file_name,
        affected_version=version,
        package=package,
        cve=cve,
        patched_version='',
        category='',
        original_issue_id_from_tool=''
    )

    try:
        conviso_api.issues.create_sca(issue_model)
    except ResponseError as error:
        if error.code == 'RECORD_NOT_UNIQUE':
            pass
    except Exception:
        pass


def parse_code_snippet(code_snippet):
    try:
        decoded_text = b64decode(code_snippet).decode("utf-8")
        lines = decoded_text.split("\n")
        cleaned_lines = []

        for line in lines:
            cleaned_line = line.split(": ", 1)[-1]
            cleaned_lines.append(cleaned_line)

        code_snippet = "\n".join(cleaned_lines)

        return code_snippet
    except Exception:
        return code_snippet


def parse_conviso_references(references=[]):
    if not references:
        return ""

    DIVIDER = "\n"

    references_to_join = []

    for reference in references:
        if reference:
            references_to_join.append(reference)

    return DIVIDER.join(references_to_join)

def parse_first_line_number(encoded_base64):
    decoded_text = b64decode(encoded_base64).decode("utf-8")

    regex = r"^(\d+):"

    result = regex_search(regex, decoded_text)

    if result and result.group(1):
        return result.group(1)

    LINE_NUMBER_WHEN_NOT_FOUND = 1
    return LINE_NUMBER_WHEN_NOT_FOUND


def clean_file(input_file):
    """Pre-process the file to remove BOM and save clean content."""
    with open(input_file, mode="rb") as file:
        content = file.read()

    # Remove BOM if it exists
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]

    # Save back the cleaned content
    cleaned_file = input_file + ".cleaned"
    with open(cleaned_file, mode="wb") as file:
        file.write(content)

    return cleaned_file


import_sarif.epilog = '''
'''
EPILOG = '''
Examples:

  \b
  1 - Import results on SARIF file to Conviso Platform:
    $ export CONVISO_API_KEY='your-api-key'
    $ {command} --input-file /path/to/file.sarif

'''  # noqa: E501

SHORT_HELP = "Perform import of vulnerabilities from SARIF file to Conviso Platform"

command = 'conviso findings import-sarif'
import_sarif.short_help = SHORT_HELP
import_sarif.epilog = EPILOG.format(
    command=command,
)
