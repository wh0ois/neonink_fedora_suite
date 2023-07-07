# System Design and rand(bs)

```shorturl.py``` is a minimal implementation of a URL shortening service.
The /shorten endpoint accepts a POST request with a JSON payload containing a long URL. It generates a unique short URL by hashing the long URL and taking the first 6 characters of the hash. The short URL is stored in Memcache and the long URL, along with other details, is stored in DynamoDB. If the long URL is already in the cache, it is retrieved from there. The response includes the generated short URL.  The /redirect_url endpoint handles requests made to the short URL. It first checks the cache (Redis) for the long URL associated with the short URL. If the long URL is found in the cache, a permanent redirect (301) is performed to the long URL. If not found in the cache, it retrieves the long URL from DynamoDB and performs a redirect. The redirection count is incremented in DynamoDB, and the long URL is cached for future requests.

The code includes Batch Writes to DynamoDB, multiple requests for long URLs are made concurrently, Redis is used as a cache to store frequently accessed long URLs (reducing load to the permanent cache) and it also keep tracks the number of times a short URL has been redirected.

To use:
```python app.py```

```
POST http://127.0.0.1:5000/shorten

Body:
{
  "long_url": "https://example.com/very-long-url-to-shorten"
}
```

----------------------------------------------------------------------


Fedora Pkg Managment: Enter interactive mode by ```python pkg_mgmt.py```
```
To search for packages, enter: search <query>
To install a package, enter: install <package_name>
To update installed packages, enter: update
To remove a package, enter: remove <package_name>
To add a repository, enter: addrepo <repo_name> <repo_url>
To remove a repository, enter: removerepo <repo_name>
To update repositories, enter: updaterepos
To exit the interactive mode, enter: exit
```
