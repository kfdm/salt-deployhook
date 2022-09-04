"""
Renderer to convert Github Webhooks into SaltStack Reactors

"""
import json
import logging
import salt.utils.event

__opts__ = {}

log = logging.getLogger(__name__)


def render(dict_data, saltenv="", sls="", tag="", **kwargs):
    event = salt.utils.event.get_master_event(
        __opts__, __opts__["sock_dir"], listen=False
    )
    lowstate = {}

    log.debug("Rendering for %s", tag)
    # If our tag is from the engine hook, then we will need to parse
    # the data and pull out the body and headers
    if tag.startswith("salt/engines/hook"):
        assert "body" in kwargs["data"], "Webhook payload should have body"
        assert "headers" in kwargs["data"], "Webhook payload should have headers"
        body = json.loads(kwargs["data"]["body"])
        headers = kwargs["data"]["headers"]

        if headers["X-Github-Event"] != "push":
            log.warning("Skipping %s event", headers["X-Github-Event"])
            return lowstate
    # Otherwise, we'll assume that the data came from another source
    # and will try to process the body as is. This allows us to support other
    # sources like mqtt_subscribe engine
    else:
        body = kwargs["data"]

    assert "repository" in body, "Payload should have repository object"
    assert "ref" in body, "Payload should have git ref"

    try:
        event.fire_event(
            {
                "repo": body["repository"]["full_name"],
                "ref": body["ref"],
                "sls": sls,
                "saltenv": saltenv,
            },
            "autodeploy/check/github",
        )
    except:
        log.exception("Unable to log check")

    for repo in dict_data:
        if repo != body["repository"]["full_name"]:
            log.debug("%s != %s", repo, body["repository"]["full_name"])
            continue

        for ref in dict_data[repo]:
            if ref != body["ref"]:
                log.debug("%s != %s", ref, body["ref"])
                continue

            for state in dict_data[repo][ref]:
                lowstate["%s:%s:%s" % (repo, ref, state)] = dict_data[repo][ref][state]
                event.fire_event(
                    {
                        "repo": repo,
                        "ref": ref,
                        "state": dict_data[repo][ref][state],
                        "sls": sls,
                        "saltenv": saltenv,
                    },
                    "autodeploy/found/github",
                )

    return lowstate
