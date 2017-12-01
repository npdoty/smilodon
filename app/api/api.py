# thanks to https://github.com/snarfed for the authorization -> signature headers hack

from app import mongo, rest_api
from .utilities import accept_headers, check_accept_headers, check_content_headers, content_headers, find_post, find_user

from activipy import core, vocab
from flask import abort, Blueprint, request, Response
from flask_restful import Resource

import json
import requests

api = Blueprint('api', __name__, template_folder='templates')
print('registered api')


class following(Resource):
    def get(self, handle):
        if check_accept_headers(request):
            u = find_user(handle)

            return u.get('following_coll', [])
        abort(406)


class followers(Resource):
    def get(self, handle):
        print('followers get')
        if check_accept_headers(request):
            u = find_user(handle)

            return u.get('followers_coll', [])
        abort(406)


class liked(Resource):
    def get(self, handle):
        if check_accept_headers(request):
            u = find_user(handle)
            likes = []

            for post in mongo.db.posts.find({'object.liked_coll': u['@id']}):
                likes.append(post['object'])

            return likes
        abort(406)


class inbox(Resource):
    def get(self, handle):
        print('inbox get')
        if check_accept_headers(request):
            items = list(mongo.db.posts.find({'to': find_user(handle)['@id']}, {'_id': False}).sort('published', -1))

            return items
        abort(406)

    def post(self, handle):
        print('inbox post')
        if check_content_headers(request):
            u = find_user(handle)
            r = request.get_json()

            if r['@type'] == 'Like':
                print('received Like')
                mongo.db.posts.update_one({'id': r['object']}, {'$push': {'object.liked_coll': r['actor']}}, upsert=True)

            elif r['@type'] == 'Follow':
                if u.get('followers_coll'):
                    if u['followers_coll'].get('actor'):
                        return 400

                mongo.db.users.update_one({'id': u['@id']}, {'$push': {'followers_coll': r['actor']}}, upsert=True)
                to = requests.get(r['actor'], headers=accept_headers(u)).json()['inbox']
                accept = vocab.accept(
                                to=to,
                                object=r.get_json()).json()
                headers = content_headers(u)

                requests.post(to, json=accept, headers=headers)
                return 202

            elif r['@type'] == 'Accept':
                print('received Accept')
                mongo.db.users.update_one({'id': u['@id']}, {'$push': {'following_coll': r['object']['actor']}}, upsert=True)
                return 202

            elif r['@type'] == 'Create':
                # this needs more stuff, like creating a user if necessary
                print('received Create')
                print(r)
                if not mongo.db.posts.find({'id': r['@id']}):
                    mongo.db.posts.insert_one(r['object'].json())
                    return 202

            else:
                print('other type')
                print(r)
            abort(400)
        abort(400)


class feed(Resource):
    def get(self, handle):
        print('feed get')
        if check_accept_headers(request):
            u = find_user(handle)

            items = list(mongo.db.posts.find({'object.attributedTo': u['@id']}, {'_id': False}).sort('published', -1))
            
            resp = vocab.OrderedCollection(
                u['outbox'],
                totalItems=len(items),
                orderedItems=items)

            return Response(json=resp.json(), headers=content_headers(u))
        abort(406)

    def post(self, handle):
        if check_content_headers(request):
            r = core.ASObj(request.get_json(), vocab.BasicEnv)
            u = find_user(handle)

            # if it's a note it turns it into a Create object
            if 'Note' in r.types:
                print('Note')

                obj = r.get_json()
                r = vocab.Create(
                    obj['@id']+'/activity',
                    actor=u['@id'],
                    published=obj['published'],
                    to=obj['to'],
                    bto=obj['bto'],
                    cc=obj['cc'],
                    bcc=obj['bcc'],
                    audience=obj['audience'],
                    obj=obj)

            if 'Create' in r.types:
                if r['object']['@type'] != 'Note':
                    print(str(r))
                    print('not a note')
                    abort(403)

                print('Create')

                mongo.db.users.update({'acct': u['acct']}, {'$inc': {'metrics.post_count': 1}})

            elif 'Like' in r.types:
                if u['acct'] not in mongo.db.posts.find({'@id': r['object']['@id']})['likes']:
                    mongo.db.posts.update({'@id': r['object']['@id']}, {'$push': {'likes': u['acct']}})

            elif 'Follow' in r.types:
                pass

            elif 'Update' in r.types:
                """
                update user object on other servers
                """
                pass

            elif 'Delete' in r.types:
                """
                notify other servers that an object has been deleted
                """
                pass

            elif 'Add' in r.types:
                """
                """
                pass

            elif 'Remove' in r.types:
                """
                """
                pass

            elif 'Announce' in r.types:
                """
                """
                pass

            elif 'Block' in r.types:
                """
                """
                pass

            elif 'Undo' in r.types:
                """
                """
                pass

            recipients = []
            r = r.json()

            for group in ['to', 'bto', 'cc', 'bcc', 'audience']:
                addresses = r.get(group, [])
                recipients.extend(addresses)

            for address in addresses:
                requests.post(address, json=r, headers=content_headers(u))
            mongo.db.posts.insert_one(r)

            return 202
        abort(400)


class user(Resource):
    def get(self, handle):
        print('get user')
        if check_accept_headers(request):
            u = find_user(handle)

            if request.args.get('get') == 'main-key':
                return u['publicKey']['publicKeyPem'].decode('utf-8')

            user = {
                    '@context': u['@context'],
                    'id': u['@id'],
                    'followers': u['followers'],
                    'following': u['following'],
                    'icon': {'type': 'Image', 'url': u['avatar']},
                    'inbox': u['inbox'],
                    'manuallyApprovesFollowers': u['manuallyApprovesFollowers'],
                    'name': u['name'],
                    'outbox': u['outbox'],
                    'preferredUsername': u['username'],
                    'publicKey': {'id': u['@id']+'#main-key', 'owner': u['@id'], 'publicKeyPem': u['publicKey']['publicKeyPem'].decode('utf-8')},
                    'summary': '',
                    'type': u['@type'],
                    'url': u['url']
                }

            return user, content_headers(u)
        abort(406)


class get_post(Resource):
    def get(self, handle, post_id):
        post = find_post(handle, post_id)
        if check_accept_headers(request):
            return post['object']
        return 'template yet to be written'


class get_post_activity(Resource):
    def get(self, handle, post_id):
        post = find_post(handle, post_id)
        if check_accept_headers(request):
            return post
        return 'template yet to be written'


# url handling
rest_api.add_resource(following, '/<string:handle>/following', subdomain='api')
rest_api.add_resource(followers, '/<string:handle>/followers', subdomain='api')
rest_api.add_resource(liked, '/<string:handle>/liked', subdomain='api')
rest_api.add_resource(inbox, '/<string:handle>/inbox', subdomain='api')
rest_api.add_resource(feed, '/<string:handle>/feed', subdomain='api')
rest_api.add_resource(user, '/user/<string:handle>')
rest_api.add_resource(get_post, '/<string:handle>/<string:post_id>', subdomain='api')
rest_api.add_resource(get_post_activity, '/<string:handle>/<string:post_id>/activity', subdomain='api')
