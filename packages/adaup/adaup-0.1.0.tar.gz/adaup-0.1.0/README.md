# Cardano Node Configuration

This repository contains the setup and configuration for running a Cardano node.

## Directory Structure

For each network, there will be a dedicated folder under `~/.cardano`. The directory structure is organized as follows:

```
$HOME/
└── .cardano
    ├── bin
    │   └── ... # common binary files cardano-node, cardano-cli, hydra-node etc.
    ├── mainnet
    │   │── configuration
    │   │── db
    │   │── hydra-{index}  
    │   └── ...  
    ├── preview
    │   └── ...
    ├── preprod
    │   └── ...
```

### Networks

- **mainnet**: Configuration and data for the Cardano main network.
- **preview/preprod**: Configuration and data for Cardano test networks.
