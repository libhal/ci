{ pkgs, ... }:
{
  imports = [ ./dagger.nix ];

  # networking.hostName and microvm.interfaces are set per runner by host.nix
  users.users.root.password = "A"; # console only; TODO: replace before exposing the VPS

  services.openssh = {
    enable = true;
    settings = {
      PermitRootLogin = "prohibit-password";
      PasswordAuthentication = false;
    };
  };

  # return freed /var blocks to the sparse var.img on the host
  services.fstrim.enable = true;

  microvm = {
    vcpu = 2;
    mem = 4096; # MiB
    balloon = true; # idle VMs give free pages back to the host

    volumes = [
      {
        mountPoint = "/var";
        image = "var.img";
        size = 30720; # MiB
      }
    ];
    shares = [
      {
        # virtiofs because these VMs are started by systemd (microvm@<name>)
        proto = "virtiofs";
        tag = "ro-store";
        # the host's /nix/store is used directly, so no squashfs/erofs is built
        source = "/nix/store";
        mountPoint = "/nix/.ro-store";
      }
    ];

    hypervisor = "qemu";
    socket = "control.socket";
  };

  virtualisation.docker.enable = true;
  environment.systemPackages = with pkgs; [
    curl
    wget
    fastfetch
    htop
    vim
    git
  ];

  system.stateVersion = "26.11";
}
