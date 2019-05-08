# rmatics

## Ansible deployment

1. Create `localhost` and target host in inventory file.
2. Run playbook, specifying deployment target host:

    `ansible-playbook --extra-vars 'target_server=stage' ansible/main.yml`
    
    Inventory file can be specified manually without modifying system-wide one.