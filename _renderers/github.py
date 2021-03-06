"""
Renderer to convert Github Webhooks into SaltStack Reactors

"""
import json
import logging
import salt.utils.event

__opts__ = {}

log = logging.getLogger(__name__)


def render(dict_data, saltenv="", sls="", **kwargs):
    event = salt.utils.event.get_master_event(
        __opts__, __opts__["sock_dir"], listen=False
    )
    lowstate = {}
    body = json.loads(kwargs["data"]["body"])
    headers = kwargs["data"]["headers"]

    if headers["X-Github-Event"] != "push":
        log.warning("Skipping %s event", headers["X-Github-Event"])
        return lowstate

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
