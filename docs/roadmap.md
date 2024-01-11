# Roadmap

## Custom Response Class

Currently, the response returned is a basic httpx.Response. It could be useful to abstract this in some manner, especially for responses which return a zip file.

- Ability to iterate through the zip file contents in some way
- Ability to write the response to some given output location?
