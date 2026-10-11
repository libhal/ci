{ pkgs, ... }:
{
  environment.systemPackages = [ (pkgs.callPackage ../pkgs/dagger-beta.nix { }) ];
}
