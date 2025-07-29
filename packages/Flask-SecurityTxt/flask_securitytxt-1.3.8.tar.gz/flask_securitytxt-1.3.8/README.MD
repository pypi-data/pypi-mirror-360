# Flask-SecurityTxt

Flask-SecurityTxt is a simple extension for Flask that makes it easy to add a 
security.txt file to your website. This file, as specified by the [Internet 
Security Research Group](https://securitytxt.org/), is used to provide 
information to security researchers about how to report vulnerabilities in your 
website.

## Installation

You can install Flask-SecurityTxt using pip:

```bash
pip install flask-securitytxt
```

## Usage

```python
from flask import Flask
from flask_security_txt import SecurityTxt

app = Flask(__name__)
security_txt = SecurityTxt(app)
```

You can also customize the contents of the security.txt file by providing the
following settings in the configuration file:

| Property                           | Type                | Default                 | Description                                                                                                                                                                                                                                                                              |
|------------------------------------|---------------------|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `SECURITY_TXT_ENDPOINT`            | `str`               | `"security_txt"`        | The name by which the end-point will be known to the Flask-app.                                                                                                                                                                                                                          |
| `WELL_KNOWN_DIR`                   | `str`               | `".well-known"`         | The name of the directory that will contain the security.txt file.                                                                                                                                                                                                                       |
| `SECURITY_TXT_FILE_NAME`           | `str`               | `"security.txt"`        | The name of the security.txt file.                                                                                                                                                                                                                                                       |
| `SECURITY_TXT_SIGN_KEY`            | `str`               | `None`                  | The name of a file containing a GPG-key used for signing the security.txt file.                                                                                                                                                                                                          |
| `SECURITY_TXT_CONTACT`             | `str` `Iterable`    | `None`                  | The value of the `contact` field. An `Iterable` type value will result in multiple `contact` fields. The `contact` field value is automatically generated using ` SECURITY_TXT_CONTACT_MAILBOX` if `None`.                                                                               |
| `SECURITY_TXT_CONTACT_MAILBOX`     | `str`               | `"security"`            | The local part of the automatically generated `contact` email address. Only used if `SECURITY_TXT_CONTACT` is `None`.                                                                                                                                                                    |
| `SECURITY_TXT_EXPIRES`             | `str` `datetime`    | `None`                  | The value of the `expires` field. A `datetime` type value will result in a ISO-formatted timestamp string. The `expires` field value is automatically generated using `SECURITY_TXT_OFFSET` if `None`.                                                                                   |
| `SECURITY_TXT_EXPIRES_OFFSET`      | `tuple` `timedelta` | `(0, 0, 0, 0, 0, 0, 1)` | The offset to be applied to `datetime.now()` in order to automatically generate the value of the `expires` field. A `tuple` type will be unpacked and passed to the `timedelta` constructor, which interprets it as days, seconds, microseconds, milliseconds, minutes, hours and weeks. |
| `SECURITY_TXT_ENCRYPTION`          | `str` `Iterable`    | `None`                  | The value of the `encryption` field. An `Iterable` type value will result in multiple `encryption` fields, a value of `None` will omit the `encryption` field.                                                                                                                           |
| `SECURITY_TXT_ACKNOWLEDGMENTS`     | `str` `Iterable`    | `None`                  | The value of the `acknowledgments` field. An `Iterable` type value will result in multiple `acknowledgments` fields, a value of `None` will omit the `acknowledgments` field.                                                                                                            |
| `SECURITY_TXT_PREFERRED_LANGUAGES` | `str` `Iterable`    | `None`                  | The value of the `languages` field. An `Iterable` type value will result in a comma-separated string. The `languages` field value is attempted to be automatically generated using the available translations listed by the `Flask-Babel` extension if `None`.                           |
| `SECURITY_TXT_CANONICAL`           | `str`               | `None`                  | The value of the `canonical` field. The `canonical` field value is automatically generated using a HTTPS-scheme, the host-name of the current request and the URL associated with the security.txt end-point, as named in `SECURITY_TXT_ENDPOINT`.                                       |
| `SECURITY_TXT_POLICY`              | `str` `Iterable`    | `None`                  | The value of the `policy` field. An `Iterable` type value will result in multiple `policy` fields, a value of `None` will omit the `policy` field.                                                                                                                                       |
| `SECURITY_TXT_HIRING`              | `str` `Iterable`    | `None`                  | The value of the `hiring` field. An `Iterable` type value will result in multiple `hiring` fields, a value of `None` will omit the `hiring` field.                                                                                                                                       |
| `SECURITY_TXT_HEADER`              | `str`               | <default header>        | A comment added to the start of the security.txt                                                                                                                                                                                                                                         |
| `SECURITY_TXT_FOOTER`              | `str`               | `None`                  |                                                                                                                                                                                                                                                                                          |

### Configuring Comments

For each property that directly controls that value of a field, a comment can
be added on the preceding line(s) by configuring the property name 
`SECURITY_TXT_<PROPERTY>_COMMENT`. Note that it is up to the developer to
optionally add whitespace and prepend each line of the comment with a `#`.

### Configuring Contact Details

The `Contact` field of the security.txt file can be configured with one of 
two different ways. First of all, the whole value string can be defined
using the `SECURITY_TXT_CONTACT` property. This take precedence over the
alternative method, which uses the `SECURITY_TXT_CONTACT_MAILBOX` property.
The value of this property is combined with the domain name of the current
host, as it is known to Flask. The latter method is less reliable, as such the
prior method is preferred if possible. By default, the contact is set to be
"security@<domain>", with the domain name being provided by Flask.

## Example

A security.txt file will be available in your website's `.well-known` 
directory, with the following contents:

```text
Contact: mailto:security@example.com
Encryption: https://example.com/key.asc
Canonical: https://example.com/.well-known/security.txt
```
