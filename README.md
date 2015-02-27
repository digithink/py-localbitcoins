Client for localbitcoins.com written in Python through drest


Settings
----

two settings: `LOCALBITCOINS_API_KEY` and `LOCALBITCOINS_API_SECRET`.

Samples
----

```
# enable debug logging
>>> import os
>>> os.environ['DREST_DEBUG'] = '1'

# send a GET request for "/api/myself/"
>>> from api import LocalbitcoinsAPI
>>> api = LocalbitcoinsAPI()
>>> response = api.make_request('GET', '/api/myself/')
>>> response.data
{u'data': {u'username': u'weipin', u'trading_partners_count': 0, u'feedback_count': 0, u'age_text': u'5\xa0hours, 14\xa0minutes', u'url': u'https://localbitcoins.com/p/weipin/', u'has_feedback': False, u'trusted_count': 0, u'feedbacks_unconfirmed_count': 0, u'blocked_count': 0, u'trade_volume_text': u'Less than 25 BTC', u'has_common_trades': False, u'feedback_score': u'N/A', u'confirmed_trade_count_text': u'0', u'created_at': u'2015-02-19T07:34:42+00:00'}}

# send a POST request for "/api/wallet-send/"
data = {'address': 'test address', 'amount': 0.0001}
response = api.make_request('POST', '/api/wallet-send/', data)
>>> response = api.make_request('POST', '/api/wallet-send/', data)
DREST_DEBUG: method=POST url=https://localbitcoins.com/api/wallet-send/ params={'amount': 0.0001, 'address': 'test address'} headers={'Content-Type': 'application/json'}
('DREST_DEBUG: (response dict, get_or_post_params_urlencoded, message) =>', {u'error': {u'message': u'An unspecified error has occurred.', u'errors': {u'address': u'* Invalid Bitcoin address.'}, u'error_code': 9, u'error_lists': {u'address': [u'Invalid Bitcoin address.']}}}, 'amount=0.0001&address=test+address', u'142435030176473ce691d07dcdb74846499357743745b/api/wallet-send/amount=0.0001&address=test+address')
```

The last POST request for "/api/wallet-send/" will produce an exception (`drest` will always throw an exception for non-200 status code). The debug output will print the response data with error string.


Important Notes
----
- The base URL of the API is "https://localbitcoins.com/", not "https://localbitcoins.com/api/"
- The relative path of the endpoints are prefixed with "api" like "/api/ads/", "/api/pincode/", etc.
- "Nonce" is NOT a random(unique) string but a integer number, and is supposed to increase in every API call. The current implementation simply uses "unix timestamp in milliseconds" to represent a nonce, which should be fine if there aren't multiple requests in one same millisecond. Another easy work around is to catch the exception for `error_code` 42 and resend the request. Here is the error response for a invalid nonce.
    ```
    {u'error': {u'message': u'Given nonce was too small.', u'error_code': 42}}
    ```
- `drest` (and so our code) will always throw an exception for non-200 status code. In most cases, you will want to catch the exception and process the error.