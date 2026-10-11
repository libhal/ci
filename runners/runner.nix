{ pkgs, ... }:
{
  imports = [
    ./dagger.nix
    ./forgejo.nix
  ];

  # networking.hostName and microvm.interfaces are set per runner by host.nix
  # Unprivileged login; authorized keys are set per runner by host.nix. It has
  # no password, so it cannot escalate; root key login is the escape hatch.
  users.users.ci = {
    isNormalUser = true;
    extraGroups = [
      "wheel"
      "docker"
    ];
  };

  services.openssh = {
    enable = true;
    settings = {
      # key-only; keys are only installed if rootAuthorizedKeys is set
      PermitRootLogin = "prohibit-password";
      PasswordAuthentication = false;
      KbdInteractiveAuthentication = false;
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
