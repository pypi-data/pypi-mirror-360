import json
from .rest import request_with_retry

def profile_search(name, key, cx, limit = 4):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': key,
        'cx': cx,
        'q': f'instagram {name}',
        'num': limit
    }
    data = request_with_retry('get', url, params=params)
    
    return [json.dumps(item) for item in data.get('items', [])]

def business_discovery(username, user_id, token, limit = 4):
    url = f'https://graph.facebook.com/v22.0/{user_id}'
    fields = (
        f'business_discovery.username({username})'
        '{biography,followers_count,follows_count,has_profile_pic,id,is_published,'
        'legacy_instagram_user_id,media_count,name,profile_picture_url,username,website,'
        f'media.limit({limit})'
        '{caption,comments_count,id,legacy_instagram_media_id,like_count,'
        'media_product_type,media_type,media_url,permalink,thumbnail_url,timestamp,view_count}}'
    )
    params = {
        'fields': fields,
        'access_token': token
    }
    data = request_with_retry('get', url, params=params)

    return [json.dumps(item)] if (item := data.get('business_discovery')) else []

def hashtag_search(hashtag, user_id, token):
    url = f'https://graph.facebook.com/v22.0/ig_hashtag_search'
    params = {
        'user_id': user_id,
        'q': hashtag,
        'access_token': token
    }
    data = request_with_retry('get', url, params=params)

    return [[item.get('id'), hashtag] for item in data.get('data', [])]

def hashtag(hashtag_id, edge, user_id, token):
    url = f'https://graph.facebook.com/v22.0/{hashtag_id}/{edge}'
    params = {
        'user_id': user_id,
        'fields': 'caption,comments_count,id,like_count,media_product_type,media_type,permalink,timestamp',
        'access_token': token
    }
    data = request_with_retry('get', url, params=params)

    return [[hashtag_id, edge, json.dumps(item)] for item in data.get('data', [])]