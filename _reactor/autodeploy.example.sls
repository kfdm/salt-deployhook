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
