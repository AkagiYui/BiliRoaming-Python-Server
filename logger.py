from logging import DEBUG, Logger, StreamHandler, getLogger

from uvicorn.logging import DefaultFormatter

log: Logger = getLogger('biliroaming')
log.setLevel(DEBUG)

log.addHandler(StreamHandler())
log.handlers[0].setFormatter(DefaultFormatter(fmt='%(levelprefix)s %(message)s'))
