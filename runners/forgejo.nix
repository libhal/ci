{
  pkgs,
  config,
  ...
}:
{
  services.gitea-actions-runner = {
    package = pkgs.forgejo-runner;
    instances.my-forgejo-instance = {
      enable = true;
      name = "${config.networking.hostName}-instance";
      # EnvironmentFile (TOKEN=...) delivered by the host as a systemd system
      # credential; see microvm.credentialFiles in host.nix
      tokenFile = "/run/credentials/@system/forgejo-token";
      url = "https://git-libhal.phazonicridley.xyz/";
      labels = [ ];
      #settings = { ... };
    };
  };
}
