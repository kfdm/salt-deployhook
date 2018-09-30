# salt-deployhook

Map a Github Webhook to a SaltStack Reactor

Salt has a powerful [reactor] system that we can take advantage of for automatically deploying via Github Webhook.
We could use one of the [netapi] modules, but to keep thing simple, we will use the basing [webhook] engine.


## Salt Master Configuration

First we need to clone our module on our Salt Master

`git clone https://github.com/kfdm/salt-deployhook.git /srv/salt-deployhook`

Then we configure our Master settings

```yaml
# Ensure that our custom state tree can be found in addition
# to our default salt states
file_roots:
  base:
    - /srv/salt
    - /srv/salt-deployhook

# For our example, enable the webhook engine with default values
engines:
  - webhook: {}

# A post to our salt master ( https://salt.example.com/github )
# Will map to our reactor ( salt://_reactor/autodeploy.sls) 
reactor:
  - 'salt/engines/hook/github':
    - salt://_reactor/autodeploy.sls

```

We configure the [webhook] engine with default settings which will map our webhook endpoint ( `https://salt.example.com/hook/github` ) to the salt event `salt/engines/hook/github`. Our [reactor] will then map our salt event to our autodeploy state

Lastly we want to ensure our modules are loaded properly

```bash
# Systemd example
# Reload salt-master to pick up our new file_roots
systemctl restart salt-master
# Sync our modules to the salt master
salt-run saltutil.sync_all
# Restart our salt-master once more to ensure our modules are loaded
systemctl restart salt-master
```

## Salt Reactor State

```yaml
#!yaml|github
# Our example autodeploy.sls
# Here we map a repository: example/salt
# and a reference: refs/heads/master
# to a state that we want to deploy: salt.repo
example/salt:
  refs/heads/master:
    deploy_repo:
      local.state.sls:
        - tgt: role:salt-master
        - tgt_type: grain
        - args:
            - mods: salt.repo

# We can setup other deployment targets as well
example/webapp:
  refs/heads/master:
    deploy_webapp:
      local.state.sls:
        - tgt: role:webserver
        - tgt_type: grain
        - args:
            - mods: mywebapp
```


## How It Works

For specific details, please check the [source]

Github webhooks contain amongst other things, a repository name and a reference. With these in mind, we create our own [renderer] module, that will loop through and return the commands that are applicable to our webhook.

Example, if we push a new commit to `master` on `example/salt`, our `yaml|github` renderer pipeline will filter our `salt://_reactor/autodeploy.sls` state, returning our correct deployment reactor

```yaml
# End result of filtering
deploy_repo:
  local.state.sls:
    - tgt: role:salt-master
    - tgt_type: grain
    - args:
        - mods: salt.repo
```


[netapi]: http://docs.saltstack.com/en/latest/ref/netapi/all/index.html
[reactor]: https://docs.saltstack.com/en/latest/topics/reactor/
[renderer]: http://docs.saltstack.com/en/latest/ref/renderers/
[source]: _renderers/github.py
[webhook]: http://docs.saltstack.com/en/latest/ref/engines/all/salt.engines.webhook.html#module-salt.engines.webhook