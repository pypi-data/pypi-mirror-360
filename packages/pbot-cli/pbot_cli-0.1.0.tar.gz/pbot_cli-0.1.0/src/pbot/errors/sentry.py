import sentry_sdk

def init_sentry():
    sentry_sdk.init(
        dsn="https://6cd7290b67f90fd0a8d1aaded84b71bc@o4509610439081984.ingest.de.sentry.io/4509610445570128",
        traces_sample_rate=1.0
    )
