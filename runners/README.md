# libhal-runners

A NixOS module that runs CI runners as [microvm.nix](https://github.com/microvm-nix/microvm.nix) virtual machines, each with Docker and Dagger inside.

## What it sets up

- A `microvm` bridge on `10.68.0.1/24` with a DHCP server (and DNS) for the VMs.
- One QEMU microVM per runner, attached to the bridge through a `vm-<name>` TAP.
- Port isolation: runners can reach the host and the internet (via NAT), but not each other.
- Per runner: 2 vCPUs, 4 GiB RAM, a sparse 30 GiB `/var` volume, the host `/nix/store` shared over virtiofs, sshd (key-only), fstrim and memory ballooning.

## Usage

```nix
{
  inputs.ci-runners.url = "git+file:///home/phazonic/Documents/libhal-runners";
  inputs.ci-runners.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { nixpkgs, ci-runners, ... }: {
    nixosConfigurations.vps = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ci-runners.nixosModules.default
        {
          services.ci-runners = {
            enable = true;
            externalInterface = "ens3"; # uplink used for NAT
            authorizedKeys = [ "ssh-ed25519 AAAA..." ];
            runners = {
              runner1.mac = "02:00:00:00:00:01";
              runner2.mac = "02:00:00:00:00:02";
            };
          };
        }
      ];
    };
  };
}
```

### Options

| Option | Default | Description |
|---|---|---|
| `enable` | `false` | Turn the module on. |
| `externalInterface` | required | Host interface the VMs are NATed out of. |
| `dns` | `[ "1.1.1.1" ]` | DNS servers handed to the VMs over DHCP. |
| `authorizedKeys` | `[ ]` | SSH keys allowed as `root` on every runner. |
| `runners.<name>.mac` | required | MAC for the runner's NIC. Must be unique. |

Runner names are limited to 12 characters (TAP names are capped at 15, including the `vm-` prefix).

## Flake outputs

- `nixosModules.default` (alias of `nixosModules.host`): the host module above.
- `nixosModules.runner`: the guest configuration, imported into each VM by the host module.
- `nixosConfigurations.test`: a throwaway system for checking evaluation:
  `nix build .#nixosConfigurations.test.config.system.build.toplevel`

## Effect on the host's network

- Enables `systemd.network` (as a default, so it can be overridden) with `.network` files that match only `microvm` and `vm-*` TAPs.
- Marks those interfaces unmanaged in NetworkManager, if it is enabled.
- Enables `networking.nat` and IP forwarding for the `microvm` bridge.
- Opens UDP 67 on the `microvm` interface only.

It does not touch `networking.useDHCP` or `networking.useNetworkd`.
