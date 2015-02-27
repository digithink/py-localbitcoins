from datetime import datetime
import hmac
import hashlib
from urllib import urlencode

LOCALBITCOINS_API_KEY = ''
LOCALBITCOINS_API_SECRET = ''

import drest

class LocalbitcoinsRequestHandler(drest.request.RequestHandler):
    class Meta:
        api_key = ''
        api_secret = ''
        api_application_name = ''
    
    def make_request_with_relative_path(self, method, relative_path, url, params=None, headers=None):
        """
        Make a call to a resource based on path, and parameters.
    
        Required Arguments:
    
            method 
                One of HEAD, GET, POST, PUT, PATCH, DELETE, etc.
                
            url
                The full url of the request (without any parameters).  Any 
                params (with GET method) and self.extra_url_params will be 
                added to this url.
                
        Optional Arguments:
        
            params
                Dictionary of additional (one-time) keyword arguments for the
                request.
            
            headers
                Dictionary of additional (one-time) headers of the request.
                
        """
        assert(self._meta.api_key)
        assert(self._meta.api_secret)
        
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        params = dict(self._extra_params, **params)
        headers = dict(self._extra_headers, **headers)
        
        url = self._get_complete_url(method, url, params)
        payload = urlencode(params)
        
        if self._meta.debug:
            print('DREST_DEBUG: method=%s url=%s params=%s headers=%s' % \
                   (method, url, params, headers))

        if method is 'GET' and not self._meta.allow_get_body:
            payload = ''
            if self._meta.debug:
                print("DREST_DEBUG: supressing body for GET request")
        
        """
        Nonce
        Nonce is a special integer number, that needs to increase in every API 
        call. It causes identical API calls to have different signature thus 
        making impossible to copy your calls and execute them later.
        
        - A 63 bit positive integer, for example unix timestamp as milliseconds.
        """
        # unix timestamp in milliseconds
        now = datetime.utcnow()
        epoch = datetime.utcfromtimestamp(0)
        delta = now - epoch
        nonce = int(delta.total_seconds() * 1000)
        
        """
        In HMAC, a message is signed with secret using some hashing algorithm to get signature. Message is formed by concatenating these four strings:

        - Nonce. A 63 bit positive integer, for example unix timestamp as milliseconds.
        - API authentication key. This is the first one of a key/secret pair.
        - Relative path, for example /api/wallet/.
        - GET or POST parameters in their URL encoded format, for example foo=bar&baz=quux.
        - Secret is got from Apps Dashboard along with the key. Hashing algorithm is SHA256.
        
        A Python example of this can be seen below:

          message = str(nonce) + api_auth_key + relative_path + get_or_post_params_urlencoded
          signature = hmac.new(api_auth_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
        """
        get_or_post_params_urlencoded = ''
        if params:
            get_or_post_params_urlencoded = urlencode(params)
        
        message = str(nonce) + self._meta.api_key + relative_path + get_or_post_params_urlencoded
        
        api_secret_bytes = self._meta.api_secret.encode('utf-8')
        message_bytes = message.encode('utf-8')
        signature = hmac.new(api_secret_bytes, msg=message_bytes, digestmod=hashlib.sha256).hexdigest().upper()
        
        """
        Signature is sent via HTTP headers. A total of three fields are needed:

        Apiauth-Key: API authentication key.
        Apiauth-Nonce: The nonce in this particular request.
        Apiauth-Signature: HMAC signature.
        """
        headers['Apiauth-Key'] = self._meta.api_key
        headers['Apiauth-Nonce'] = str(nonce)
        headers['Apiauth-Signature'] = signature
        
        """
        All arguments are given application/x-www-form-urlencoded, if not in GET 
        method
        """
        if method != 'GET':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        res_headers, data = self._make_request(url, method, payload,
                                               headers=headers)
        unserialized_data = data
        serialized_data = None
        if self._meta.deserialize:
            serialized_data = data
            data = self._deserialize(data)

        return_response = drest.response.ResponseHandler(
            int(res_headers['status']), data, res_headers,
            )
        if self._meta.debug:
            print("DREST_DEBUG: (response dict, get_or_post_params_urlencoded, message) =>", data, get_or_post_params_urlencoded, message)
        return self.handle_response(return_response)
            
class LocalbitcoinsAPI(drest.API):
    """
    Arguments:
    
        baseurl
            Translated to self.baseurl (for convenience).
        api_key
            API authentication key
        api_secret
            API authentication secret
    """
    class Meta:
        baseurl = 'https://localbitcoins.com/'
        request_handler = LocalbitcoinsRequestHandler
        
        api_key = LOCALBITCOINS_API_KEY
        api_secret = LOCALBITCOINS_API_SECRET

    def make_request(self, method, path, params=None, headers=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        url = "%s/%s/" % (self.baseurl.strip('/'), path.strip('/'))
        return self.request.make_request_with_relative_path(method, path, url, params, headers)
