# Simple Python logger

A simple logger for console/file logging with duplicate logs filter support

## Release new version

### requirements

- Export GitHub token

```bash
export GITHUB_TOKEN=<your_github_token>
```

- [release-it](https://github.com/release-it/release-it)

Run the following once (execute outside repository dir for example `~/`):

```bash
sudo npm install --global release-it
npm install --save-dev @release-it/bumper
```

### usage

- Create a release

```bash
git pull
release-it # Follow the instructions
```

## Usage

```python
from simple_logger.logger import get_logger
logger = get_logger(name=__name__, level=logging.DEBUG, filename="my-log.log")
logger.info("This is INFO log")
logger.success("This is SUCCESS log")

TOKEN = "1234"
PASS = "pass123"
logger.hash(f"This is my password: {PASS} and this is my token {TOKEN}", hash=[PASS, TOKEN])
>>> This is INFO log
>>> This is SUCCESS log
>>> This is my password: ***** and this is my token *****


# mask sensitive data default words are ["password", "token", "apikey", "secret"]
# Pass mask_sensitive_patterns = ["custom_pattern", "another_pattern"] to change the default patterns to match
hashed_logger = get_logger(name=__name__, mask_sensitive=True)
hashed_logger.info(er = get"This is my password: pass123")
hashed_logger.info(er = get"This is my token tok456!")
hashed_logger.info(er = get"This is my apikey - api#$789")
hashed_logger.info(er = get"This is my secret -> sec1234abc")
>>> This is my password *****
>>> This is my token *****
>>> This is my apikey *****
>>> This is my secret *****
```
