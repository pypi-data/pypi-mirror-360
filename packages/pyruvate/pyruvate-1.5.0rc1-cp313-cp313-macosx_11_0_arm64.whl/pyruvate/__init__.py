from pyruvate._pyruvate import serve, FileWrapper  # noqa: F401


def serve_paste(app, global_conf, **kw):
    kwargs = dict()
    if "max_number_headers" in kw:
        kwargs["max_number_headers"] = int(kw["max_number_headers"])
    if "async_logging" in kw:
        kwargs["async_logging"] = bool(kw["async_logging"] == "False")
    if "chunked_transfer" in kw:
        kwargs["chunked_transfer"] = bool(kw["chunked_transfer"] == "True")
    if "max_reuse_count" in kw:
        kwargs["max_reuse_count"] = int(kw["max_reuse_count"])
    if "keepalive_timeout" in kw:
        kwargs["keepalive_timeout"] = int(kw["keepalive_timeout"])
    if "qmon_warn_threshold" in kw:
        kwargs["qmon_warn_threshold"] = int(kw['qmon_warn_threshold'])
    if "send_timeout" in kw:
        kwargs["send_timeout"] = int(kw["send_timeout"])
    serve(
        app,
        kw.get("socket"),
        int(kw.get("workers")),
        **kwargs)
    return 0
