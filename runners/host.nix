{ self, microvm }:
{ config, lib, ... }:
let
  cfg = config.services.ci-runners;
in
{
  imports = [ microvm.nixosModules.host ];

  options.services.ci-runners = {
    enable = lib.mkEnableOption "Forgejo CI runner microVMs";
    externalInterface = lib.mkOption { type = lib.types.str; };
    dns = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ "1.1.1.1" ];
      description = "DNS servers handed to the runners over DHCP.";
    };
    authorizedKeys = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "SSH public keys allowed to log in as root on every runner.";
    };
    runners = lib.mkOption {
      default = { };
      type = lib.types.attrsOf (
        lib.types.submodule {
          options.mac = lib.mkOption { type = lib.types.str; };
        }
      );
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.network = {
      enable = lib.mkDefault true;
      # With NetworkManager owning the uplink, the only links networkd manages
      # are ours (RequiredForOnline = no), so wait-online has nothing to wait
      # for and just times out.
      wait-online.enable = lib.mkIf config.networking.networkmanager.enable (lib.mkDefault false);
      netdevs."10-microvm".netdevConfig = {
        Kind = "bridge";
        Name = "microvm";
      };

      networks = {
        "10-microvm" = {
          matchConfig.Name = "microvm";
          networkConfig.DHCPServer = true;
          dhcpServerConfig = {
            EmitDNS = true;
            DNS = cfg.dns;
          };
          addresses = [ { Address = "10.68.0.1/24"; } ];
          # don't make network-online.target wait on the bridge or the TAPs
          linkConfig.RequiredForOnline = "no";
        };

        "11-microvm" = {
          # networkd reports TAP devices as Kind "tun"
          matchConfig = {
            Name = "vm-*";
            Kind = "tun";
          };
          # Attach to the bridge that was configured above
          networkConfig.Bridge = "microvm";
          bridgeConfig.Isolated = true;
          linkConfig.RequiredForOnline = "no";
        };
      };
    };

    networking = {
      firewall.interfaces.microvm.allowedUDPPorts = [ 67 ];
      nat = {
        enable = true;
        externalInterface = cfg.externalInterface;
        internalInterfaces = [ "microvm" ];
      };
      networkmanager.unmanaged = lib.mkIf config.networking.networkmanager.enable [
        "microvm"
        "vm-*"
      ];
    };

    microvm.vms = lib.mapAttrs (name: r: {
      config = {
        imports = [ self.nixosModules.runner ];
        networking.hostName = name;
        users.users.root.openssh.authorizedKeys.keys = cfg.authorizedKeys;
        microvm.interfaces = [
          {
            type = "tap";
            id = "vm-${name}";
            inherit (r) mac;
          }
        ];
      };
    }) cfg.runners;
  };
}
