<br>
<div align="center">
  <img src="https://cdn.phenompeople.com/CareerConnectResources/PMCNUS/images/1675854791014_Phenom_Lockup_RGB_Black-1658753087938.png"><br>
</div>
<br>



# Phenom : Helping a billion people find the right work.


## What is it?

**Phenom** is at the forefront of Talent Experience Management (TXM), offering a suite of APIs designed to revolutionize talent acquisition, engagement, and retention processes. With Phenom's public APIs, developers gain access to powerful tools for creating seamless and personalized experiences throughout the entire talent lifecycle.
Phenom's public APIs empower organizations to elevate their talent experience management strategies, driving better outcomes for candidates, employees, and businesses alike. Whether you're a recruiter, HR professional, or developer, Phenom's APIs provide the tools and resources you need to succeed in today's competitive talent market.

## Authentication

By default, token authentication depends on correct configure of following environment variables.

- `TOKEN_URL` for token generation.
- `CLIENT_ID` for client ID.
- `CLIENT_SECRET` for client SECRET.
- `GATEWAY_URL` for phenom public api's accessing url.
- `API_KEY` secret key for accessing azure public api's.

With above configuration, client can be authenticated by following code:

```python
from phenom.commons.authorization import Authorization

client = ApiManagementClient(TOKEN_URL, CLIENT_ID, CLIENT_SECRET, GATEWAY_URL,
                       API_KEY)
```

## Table of Contents

- [Pre-requisites](#pre-requisites)
- [Documentation](#documentation)
- [Contact us](#contact-us)

## Pre-requisites
Python 3.6+ is required to use this package.

## Documentation
The official documentation is hosted on [Phenom Apis](https://developer.phenom.com/).

## Contact us
If you have any questions or need help, please contact us at [Phenom Support](https://developer.phenom.com/ContactUs/).
