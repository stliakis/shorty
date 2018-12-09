# shorty
Flask app for making urls short with a mongodb backend store, its based on https://github.com/pyr/url-shortener but 
uses mongodb instead of redis and its in python3


## Usage

### Create

```python
import requests
from pprint import pprint

r = requests.post('http://ws-shorty.domain.com', data={"url":"www.google.com"})
pprint(r.json())
```

#### response
```json
{
    "code": "00Z9sTE3IUA",
    "shorturl": "https://ws-shorty.domain.com/00Z9sTE3IUA",
    "success": true,
    "url": "http://www.google.com"
}
```

### Get
```python
import requests
from pprint import pprint

r = requests.get('http://ws-shorty.domain.com/g/00Z9sTE3IUA')
pprint(r.json())
```

#### response
```json
{
    "url": "http://www.google.com"
}


*Hitting http://ws-shorty.domain.com/00Z9sTE3IUA will redirect you to https://ws-shorty.domain.com/00Z9sTE3IUA
