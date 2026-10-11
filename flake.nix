{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    microvm = {
      url = "github:microvm-nix/microvm.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      microvm,
      ...
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {

      # Export dagger-beta as a package so developers can run ci locally
      packages = forAllSystems (pkgs: {
        dagger-beta = pkgs.callPackage ./pkgs/dagger-beta.nix { };
        default = self.packages.${pkgs.stdenv.hostPlatform.system}.dagger-beta;
      });
      overlays.default = final: prev: {
        dagger-beta = final.callPackage ./pkgs/dagger-beta.nix { };
      };

      nixosModules = {
        runner = ./runners/runner.nix; # runner configuration
        host = import ./runners/host.nix { inherit self microvm; };
        default = self.nixosModules.host;
      };
    };
}
