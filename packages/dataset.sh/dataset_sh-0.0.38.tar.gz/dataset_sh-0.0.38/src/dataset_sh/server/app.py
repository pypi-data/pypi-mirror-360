import binascii
import json
import logging
import math
import os
from functools import wraps

import jwt
from flask import Flask, jsonify, send_file, g, request, make_response
from head_switcher import install_to_flask, load_from_package_resources

from dataset_sh.clients import LocalStorage
from dataset_sh.clients.locator import DatasetLocator
from dataset_sh.fileserver.sign import extract_token_from_request, get_token, verify_upload_token, \
    create_download_token, create_upload_token
from dataset_sh.fileserver.utils import suggest_parts, create_download_url, create_upload_cancel_url, \
    create_upload_finish_url
from dataset_sh.multipart.multipart import MultipartFileWriter
from dataset_sh.utils.files import filesize, file_creation_time
from werkzeug.security import safe_join
from importlib.metadata import version as lib_version

from dataset_sh.server.config import load_config
from dataset_sh.server.project_file_manager import ProjectArticleManager
from dataset_sh.server.utils import generate_download_code
from dataset_sh.utils.usage.read_data_codegen import get_read_data_code
from .core import RepoServerConfig
from .constants import ACCESS_KEY_HEADER_NAME, TOKEN_HEADER_KEY


def load_frontend_assets():
    try:
        return load_from_package_resources('dataset_sh.server.assets', 'app-ui.frontend', prefix='dist/')
    except FileNotFoundError as e:
        return {
            'index.html': 'dataset.sh web interface is disabled.'
        }


DISABLE_UI = os.environ.get('DISABLE_DATASET_APP_UI', '0').lower() in ['true', '1']


def calculate_chunk_size(config, file_length):
    max_chunk_count = config.max_chunk_count
    minimal_chunk_size = config.minimal_chunk_size

    if max_chunk_count * minimal_chunk_size > file_length:
        return minimal_chunk_size
    else:
        chunk_size = int(math.ceil(file_length / max_chunk_count))
        return chunk_size


def create_app(frontend_assets=None, config: RepoServerConfig = None):
    app = Flask(__name__, static_folder=None)

    # Only setup logging if debug mode is enabled
    if app.debug:
        # Set up basic logging to stdout
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Or you can configure the Flask logger directly
        app.logger.setLevel(logging.DEBUG)

        # Log that debug mode is enabled
        app.logger.debug('Debug mode is enabled')

    dataset_sh_version = lib_version('dataset.sh')

    @app.after_request
    def add_custom_header(response):
        response.headers['DATASET_SH_SERVER_VERSION'] = dataset_sh_version
        return response

    if config is None:
        config = load_config(app).override_from_env()

    if frontend_assets is None:
        if not DISABLE_UI:
            frontend_assets = load_frontend_assets()
        else:
            frontend_assets = {
                'index.html': "dataset.sh web ui is disabled"
            }

    config.make_dirs()

    local_storage = LocalStorage(config.data_folder)
    pf_manager = ProjectArticleManager(config.article_folder)

    @app.route('/api/version', methods=['GET'])
    def get_server_version():
        return jsonify({
            'server': 'dataset.sh server',
            'version': lib_version('dataset.sh')
        })

    if config.require_auth:
        @app.route('/api/login', methods=['POST'])
        def login():
            username = request.json.get('username')
            password = request.json.get('password')
            if config.verify_userpass(username, password):
                token = jwt.encode({
                    'username': username
                }, config.secret_key, algorithm="HS256")
                response = make_response(jsonify({'message': 'Login successful'}))
                response.set_cookie(TOKEN_HEADER_KEY, token)
                return response
            else:
                return '', 401

        @app.route('/api/logout', methods=['POST'])
        def logout():
            response = make_response(jsonify({'message': 'Logout successful'}))
            response.delete_cookie(TOKEN_HEADER_KEY)
            return response

    @app.before_request
    def before_request_func():

        g.current_user = None
        token = request.cookies.get(TOKEN_HEADER_KEY, None)
        if token:
            try:
                payload = jwt.decode(token, config.secret_key, algorithms=['HS256'])
                g.current_user = payload['username']
            except jwt.ExpiredSignatureError:  # pragma: no cover
                pass
            except jwt.InvalidTokenError:  # pragma: no cover
                pass
        else:
            access_key = request.headers.get(ACCESS_KEY_HEADER_NAME, None)
            if access_key is not None:
                try:
                    g.current_user = config.verify_key(access_key)
                except (json.decoder.JSONDecodeError, binascii.Error):
                    pass

    def require_auth(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if config.require_auth and g.current_user is None:
                return '', 401
            return f(*args, **kwargs)

        return decorated_function

    @app.route('/api/info', methods=['GET'])
    @require_auth
    def get_info():
        if g.current_user is None:
            return jsonify({'username': ''})
        else:
            return jsonify({'username': g.current_user})

    @app.route('/api/hostname', methods=['GET'])
    @require_auth
    def get_host():
        return jsonify({'hostname': config.hostname})

    @app.route('/api/dataset', methods=['GET'])
    @require_auth
    def list_datasets():
        items = local_storage.datasets()
        return jsonify({
            'items': [{
                'namespace': item.namespace,
                'dataset': item.dataset_name,
            } for item in items]
        }), 200

    @app.route('/api/namespace', methods=['GET'])
    @require_auth
    def list_namespaces():
        items = local_storage.namespaces()
        return jsonify({
            'namespaces': [item.namespace for item in items]
        }), 200

    @app.route('/api/dataset/<namespace>', methods=['GET'])
    @require_auth
    def list_datasets_in_store(namespace):
        items = local_storage.namespace(namespace).datasets()
        return jsonify({
            'items': [{
                'namespace': item.namespace,
                'dataset': item.dataset_name,
            } for item in items]
        }), 200

    def _get_version_description(namespace, dataset_name, version):
        ret = {
            "version": version,
        }
        dv = local_storage.namespace(namespace).dataset(dataset_name).version(version)
        if dv.exists():
            meta = dv.meta()

            fp = dv.datafile()
            if os.path.exists(fp):
                ret['fileSize'] = filesize(fp)
                ret['createdAt'] = int(file_creation_time(fp).timestamp())

            d = meta.get('description', None)
            if d:
                ret['description'] = d
        return ret

    @app.route('/api/dataset/<namespace>/<dataset_name>/version', methods=['GET'])
    @require_auth
    def list_dataset_versions(namespace, dataset_name):
        versions = local_storage.namespace(namespace).dataset(dataset_name).versions()
        return jsonify({
            'items': [_get_version_description(namespace, dataset_name, v.version) for v in versions]
        })

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag', methods=['GET'])
    @require_auth
    def list_dataset_tags(namespace, dataset_name):
        tags = local_storage.namespace(namespace).dataset(dataset_name).tags()
        return jsonify({
            'items': [{'tag': tag, 'version': version} for tag, version in tags.items()]
        })

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>', methods=['GET'])
    @require_auth
    def get_tag(namespace, dataset_name, tag):
        t = local_storage.namespace(namespace).dataset(dataset_name).resolve_tag(tag)
        if t:
            return jsonify({
                'tag': tag,
                'version': t
            })
        else:
            return '', 404

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>', methods=['POST'])
    @require_auth
    def set_tag(namespace, dataset_name, tag):

        if not config.allow_upload:
            return '', 401

        if not hasattr(g, 'current_user') or g.current_user != namespace:
            return '', 401

        local_storage.namespace(namespace).dataset(dataset_name).set_tag(tag, request.json.get('version'))
        return '', 204

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>', methods=['DELETE'])
    @require_auth
    def remove_tag(namespace, dataset_name, tag):
        if not config.allow_upload:
            return '', 401

        if not hasattr(g, 'current_user') or g.current_user != namespace:
            return '', 401
        local_storage.namespace(namespace).dataset(dataset_name).remove_tag(tag)
        return '', 204

    #
    #
    #
    #
    #  By Version
    #
    #
    #
    #
    @app.route('/api/dataset/<namespace>/<dataset_name>/version/<version>/meta', methods=['GET'])
    @require_auth
    def get_dataset_meta_by_version(namespace, dataset_name, version):
        dv = local_storage.namespace(namespace).dataset(dataset_name).version(version)
        if dv.exists():
            meta = dv.meta()
            fp = dv.datafile()
            meta['fileSize'] = filesize(fp)
            return jsonify(meta), 200
        else:
            return '', 404

    @app.route('/api/dataset/<namespace>/<dataset_name>/version/<version>', methods=['DELETE'])
    @require_auth
    def r_remove_dataset_version(namespace, dataset_name, version):
        if not config.allow_upload:
            return '', 401
        if not hasattr(g, 'current_user') or g.current_user != namespace:
            return '', 401

        dv = local_storage.namespace(namespace).dataset(dataset_name).version(version)
        if dv.exists():
            dv.delete()
            return '', 204
        else:
            return '', 404

    @app.route('/api/dataset/<namespace>/<dataset_name>/version/<version>/collection/<collection_name>/sample',
               methods=['GET'])
    @require_auth
    def get_collection_sample_by_version(namespace, dataset_name, version, collection_name):
        sample = local_storage.namespace(namespace).dataset(dataset_name).version(version).sample(collection_name)
        return jsonify(sample), 200

    @app.route('/api/dataset/<namespace>/<dataset_name>/version/<version>/collection/<collection_name>/type',
               methods=['GET'])
    @require_auth
    def get_collection_ta_by_version(namespace, dataset_name, version, collection_name):
        ta_dict = local_storage.namespace(namespace).dataset(dataset_name).version(version).type_annotation_dict(
            collection_name)
        return jsonify({"type": ta_dict}), 200

    @app.route('/api/dataset/<namespace>/<dataset_name>/version/<version>/collection/<collection_name>/code',
               methods=['GET'])
    @require_auth
    def get_collection_code_by_version(namespace, dataset_name, version, collection_name):
        reader_code = get_read_data_code(
            f'{namespace}/{dataset_name}',
            collection_name,
            version=version,
            tag=None
        )
        return {'code': reader_code}, 200

    @app.route('/api/dataset/<namespace>/<dataset_name>/version/<version>/download-code', methods=['GET'])
    @require_auth
    def get_download_code_by_version(namespace, dataset_name, version):
        fullname = f"{namespace}/{dataset_name}"
        lang = request.values.get('lang', 'python')
        if config.hostname:
            code = generate_download_code(lang, config.hostname, fullname, version=version)
            return {'code': code}, 200
        else:
            return {'code': ''}, 200

    @app.route('/api/dataset/<namespace>/<dataset_name>/version/<version>/file', methods=['GET'])
    @require_auth
    def get_dataset_file_by_version(namespace, dataset_name, version):
        dv = local_storage.namespace(namespace).dataset(dataset_name).version(version)
        if dv.exists():
            f = dv.datafile()
            if os.path.exists(f):
                root = os.path.normpath(local_storage.location)
                f = os.path.normpath(f)
                if f.startswith(root):
                    return send_file(
                        f,
                        as_attachment=True,
                        download_name=f"{namespace}_{dataset_name}.dataset"
                    )
        return '', 404

    #
    #
    #
    #
    #  By Tag
    #
    #
    #
    #
    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>/meta', methods=['GET'])
    @require_auth
    def get_dataset_meta_by_tag(namespace, dataset_name, tag):
        dv = local_storage.namespace(namespace).dataset(dataset_name).tag(tag, allow_none=True)
        if dv and dv.exists():
            meta = dv.meta()
            fp = dv.datafile()
            meta['fileSize'] = filesize(fp)
            return jsonify(meta), 200
        else:
            return '', 404

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>/collection/<collection_name>/sample',
               methods=['GET'])
    @require_auth
    def get_collection_sample_by_tag(namespace, dataset_name, tag, collection_name):
        dv = local_storage.namespace(namespace).dataset(dataset_name).tag(tag, allow_none=True)
        if dv and dv.exists():
            sample = dv.sample(collection_name)
            return jsonify(sample), 200
        else:
            return "", 404

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>/collection/<collection_name>/type',
               methods=['GET'])
    @require_auth
    def get_collection_typa_anotation_by_tag(namespace, dataset_name, tag, collection_name):
        dv = local_storage.namespace(namespace).dataset(dataset_name).tag(tag, allow_none=True)
        if dv and dv.exists():
            ta_dict = dv.type_annotation_dict(collection_name)
            return jsonify({"type": ta_dict}), 200
        else:
            return "", 404

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>/collection/<collection_name>/code',
               methods=['GET'])
    @require_auth
    def get_collection_code_by_tag(namespace, dataset_name, tag, collection_name):
        dv = local_storage.namespace(namespace).dataset(dataset_name).tag(tag, allow_none=True)
        if dv and dv.exists():
            reader_code = get_read_data_code(
                f'{namespace}/{dataset_name}',
                collection_name,
                version=None,
                tag=tag
            )
            return jsonify({'code': reader_code}), 200
        else:
            return "", 404

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>/download-code', methods=['GET'])
    @require_auth
    def get_download_code_by_tag(namespace, dataset_name, tag):
        fullname = f"{namespace}/{dataset_name}"
        lang = request.values.get('lang', 'python')
        if config.hostname:
            code = generate_download_code(lang, config.hostname, fullname, tag=tag)
            return {'code': code}, 200
        else:
            return {'code': ''}, 200

    @app.route('/api/dataset/<namespace>/<dataset_name>/tag/<tag>/file', methods=['GET'])
    @require_auth
    def get_dataset_file_by_tag(namespace, dataset_name, tag):
        dv = local_storage.namespace(namespace).dataset(dataset_name).tag(tag, allow_none=True)
        if dv and dv.exists():
            f = dv.datafile()
            if os.path.exists(f):
                root = os.path.normpath(local_storage.location)
                f = os.path.normpath(f)
                if f.startswith(root):
                    return send_file(
                        f,
                        as_attachment=True,
                        download_name=f"{namespace}_{dataset_name}.dataset"
                    )
        return '', 404

    #
    #
    #
    #
    #  Upload Dataset
    #
    #
    #
    #

    def get_writer(namespace, dataset_name, checksum_value, file_size):
        filename = f"dataset_file_{checksum_value}"

        os.makedirs(safe_join(
            config.uploader_folder,
            namespace, dataset_name),
            exist_ok=True)
        fp = safe_join(
            config.uploader_folder,
            namespace,
            dataset_name,
            filename
        )

        file_size = int(file_size)

        writer = MultipartFileWriter(
            fp,
            checksum=checksum_value,
            file_length=file_size,
            chunk_size=calculate_chunk_size(config, file_size)
        )

        return writer

    @app.route('/api/resource', methods=['POST'])
    @require_auth
    def r_query_resource():
        app.logger.debug(f"user %s", g.current_user)
        app.logger.debug(f"allow_upload: %s", config.allow_upload)

        app.logger.debug(f"upload config: minimal_chunk_size = %d", config.minimal_chunk_size)
        app.logger.debug(f"upload config: max_chunk_count = %d", config.max_chunk_count)

        if config.allow_upload and g.current_user is not None:
            action = request.args['action']
            filename = request.args['filename']
            dataset_locator = DatasetLocator.from_str(filename)
            if action == 'upload':

                if not hasattr(g, 'current_user') or g.current_user != dataset_locator.namespace:
                    return '', 401

                file_size = int(request.args['size'])
                checksum_value = request.args['checksum']
                tags = [t.strip() for t in request.args.get('tag', '').split(',') if t.strip() != '']

                writer = get_writer(
                    dataset_locator.namespace, dataset_locator.dataset_name,
                    checksum_value, file_size)

                existing: 'FilePartsInfo' = writer.load_existing_progress()
                if existing is None:
                    writer.start()
                    existing = writer.load_existing_progress()
                # return jsonify(existing.model_dump(mode='json'))

                locator_str = f'{dataset_locator.namespace}/{dataset_locator.dataset_name}:version={checksum_value}'

                token = create_upload_token(config.secret_key, locator_str)

                parts = suggest_parts(
                    config.hostname,
                    dataset_locator,
                    file_size,
                    checksum_value,
                    token,
                    min_chunk_size=config.minimal_chunk_size,
                    max_chunks=config.max_chunk_count
                )
                """
                Part item looks like this.
                {
                    'part': part_number,
                    'start': chunk_start,
                    'size': chunk_end - chunk_start,
                    'url': create_part_upload_url(
                        hostname,
                        dataset_locator.namespace, dataset_locator.dataset_name,
                        checksum_value, file_size, part_number, token),
                    'report_url': create_part_progress_report_url(
                        hostname,
                        dataset_locator.namespace, dataset_locator.dataset_name,
                        checksum_value, file_size, part_number, token
                    )
                }
                """

                cancel_url = create_upload_cancel_url(
                    config.hostname,
                    dataset_locator.namespace,
                    dataset_locator.dataset_name,
                    checksum_value,
                    file_size,
                    token
                )

                finish_url = create_upload_finish_url(
                    config.hostname,
                    dataset_locator.namespace,
                    dataset_locator.dataset_name,
                    checksum_value,
                    file_size,
                    tags,
                    token
                )

                return jsonify({
                    'allowed': True,
                    'action': 'upload',
                    'parts': parts,
                    'finished_parts': existing.finished,
                    'cancel_url': cancel_url,
                    'finish_url': finish_url
                })
            elif action == 'download':
                token = create_download_token(
                    config.secret_key,
                    filename
                )

                download_url = create_download_url(
                    config.hostname,
                    dataset_locator, token
                )

                return jsonify({
                    'allowed': True,
                    'action': 'download',
                    'url': download_url
                })
            else:
                return '', 401
        else:
            return '', 401

    @app.route('/api/dataset/<namespace>/<dataset_name>/upload', methods=['PUT'])
    def r_presigned_upload(namespace, dataset_name):
        if config.allow_upload:
            file_size = request.args['file_size']
            checksum_value = request.args['checksum_value']
            part_id = request.args['part_id']
            locator_str = f'{namespace}/{dataset_name}:version={checksum_value}'

            if not verify_upload_token(config.secret_key, locator_str):
                return '', 401

            writer = get_writer(namespace, dataset_name, checksum_value, file_size)
            part_file = writer.part_file(int(part_id))
            with open(part_file, 'wb') as out:
                out.write(request.data)
            writer.mark_file_as_complete(int(part_id))

            return '', 204
        else:
            return '', 401

    @app.route('/api/dataset/<namespace>/<dataset_name>/upload-progress', methods=['POST'])
    def r_presigned_upload_report(namespace, dataset_name):
        if config.allow_upload:
            # TODO: check token
            action = request.args['action']
            file_size = request.args['file_size']
            checksum_value = request.args['checksum_value']
            locator_str = f'{namespace}/{dataset_name}:version={checksum_value}'
            tags = [t.strip() for t in request.args.get('tag', '').split(',') if t.strip() != '']

            if not verify_upload_token(config.secret_key, locator_str):
                return '', 401

            writer = get_writer(namespace, dataset_name, checksum_value, file_size)

            if action == 'progress-update':
                pass
            elif action == 'abort':
                writer.terminate()
                return '', 204
            elif action == 'done':
                writer.done()
                version_hex = local_storage.namespace(namespace).dataset(dataset_name).import_file(
                    writer.target,
                    remove_source=True,
                    tags=tags
                )

            # Do nothing.
            return '', 204
        else:
            return '', 401

    # @app.route('/api/dataset/<namespace>/<dataset_name>', methods=['POST'])
    # @require_auth
    # def create_dataset(namespace, dataset_name):
    #     if config.allow_upload:
    #         user_name = namespace
    #         dataset_name = dataset_name
    #         tags = [t.strip() for t in request.args.get('tag', '').split(',') if t.strip() != '']
    #
    #         if not hasattr(g, 'current_user') or g.current_user != user_name:
    #             return '', 401
    #
    #         checksum_value = request.args['checksum_value']
    #         file_length = int(request.args['file_length'])
    #         action = request.args['action']
    #
    #         filename = f"dataset_file_{checksum_value}"
    #
    #         os.makedirs(safe_join(config.uploader_folder, user_name, dataset_name), exist_ok=True)
    #         fp = safe_join(config.uploader_folder, user_name, dataset_name, filename)
    #
    #         writer = MultipartFileWriter(
    #             fp,
    #             checksum=checksum_value,
    #             file_length=file_length,
    #             chunk_size=calculate_chunk_size(config, file_length)
    #         )
    #
    #         if action == 'init':
    #             existing = writer.load_existing_progress()
    #             if existing is None:
    #                 writer.start()
    #                 existing = writer.load_existing_progress()
    #             return jsonify(existing.model_dump(mode='json'))
    #         elif action == 'upload':
    #             part_id = request.args['part_id']
    #             part_file = writer.part_file(int(part_id))
    #             with open(part_file, 'wb') as out:
    #                 out.write(request.data)
    #             writer.mark_file_as_complete(part_id)
    #             return '', 204
    #         elif action == 'done':
    #             writer.done()
    #             version_hex = local_storage.namespace(namespace).dataset(dataset_name).import_file(
    #                 fp,
    #                 remove_source=True,
    #                 tags=tags
    #             )
    #             return '', 204
    #         elif action == 'abort':
    #             writer.terminate()
    #             return '', 204
    #         return '', 400
    #     else:
    #         return '', 401

    @app.route('/api/dataset/<namespace>/<dataset_name>/readme', methods=['POST'])
    @require_auth
    def update_dataset_readme(namespace, dataset_name):
        if config.allow_upload:
            t = local_storage.namespace(namespace).dataset(dataset_name)
            readme = request.json.get('readme')
            t.set_readme(readme)
            return '', 204
        else:
            return '', 401

    @app.route('/api/dataset/<namespace>/<dataset_name>/readme', methods=['GET'])
    @require_auth
    def get_dataset_readme(namespace, dataset_name):
        t = local_storage.namespace(namespace).dataset(dataset_name)
        readme = t.readme()
        if readme is None:
            return '', 404
        return readme, 200

    #
    #
    #
    #
    #  Articles
    #
    #
    #
    #
    @app.route('/api/post-assets/<path:asset_path>', methods=['GET'])
    @require_auth
    def get_asset_path(asset_path):
        fp = os.path.join(
            pf_manager.base_folder,
            '__assets__',
            asset_path
        )

        fp = os.path.normpath(fp)
        if not fp.startswith(pf_manager.base_folder):
            return '', 404

        if os.path.exists(fp):
            return send_file(fp)
        else:
            return '', 404

    @app.route('/api/post', methods=['GET'])
    @require_auth
    def list_posts():
        articles = [a.model_dump(mode='json') for a in pf_manager.list_articles()]
        return jsonify({'items': articles})

    @app.route('/api/post/<path:post_name>', methods=['GET'])
    @require_auth
    def get_post(post_name):
        article = pf_manager.extract_article(post_name)
        if article is None:
            return '', 404
        return article

    install_to_flask(frontend_assets, app)

    return app


if __name__ == '__main__':  # pragma: no cover
    _frontend_assets = {
        'index.html': "dataset.sh web ui is disabled"
    }

    if not DISABLE_UI:
        _frontend_assets = load_frontend_assets()

    app = create_app(frontend_assets=_frontend_assets)
    app.run(port=8989)
