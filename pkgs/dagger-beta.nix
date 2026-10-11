{
  lib,
  stdenvNoCC,
  fetchurl,
  installShellFiles,
}:
let
  # dagger/nix only packages stable releases (0.21.x), so the 1.0 beta is pinned here.
  # Checksums: https://dl.dagger.io/dagger/releases/<version>/checksums.txt
  daggerVersion = "1.0.0-beta.15";
  daggerArch =
    {
      x86_64-linux = {
        name = "linux_amd64";
        sha256 = "c00b0b21a77f9cd069605806856e4c9eec57320a61e18eefc4c38ed48b013b75";
      };
      aarch64-linux = {
        name = "linux_arm64";
        sha256 = "0afa9260fd4b537018bfec942503715a0db5cb69866797928f434a4cf655c568";
      };
    }
    .${stdenvNoCC.hostPlatform.system};
in
# Upstream publishes a prebuilt static binary, so "building" is download + install.
stdenvNoCC.mkDerivation {
  pname = "dagger";
  version = daggerVersion;

  src = fetchurl {
    url = "https://dl.dagger.io/dagger/releases/${daggerVersion}/dagger_v${daggerVersion}_${daggerArch.name}.tar.gz";
    inherit (daggerArch) sha256;
  };
  sourceRoot = ".";

  nativeBuildInputs = [ installShellFiles ];

  installPhase = ''
    runHook preInstall
    install -Dm755 dagger $out/bin/dagger
    installShellCompletion --cmd dagger \
      --bash <($out/bin/dagger completion bash) \
      --fish <($out/bin/dagger completion fish) \
      --zsh <($out/bin/dagger completion zsh)
    runHook postInstall
  '';

  meta = {
    description = "Dagger CLI (prebuilt release binary)";
    homepage = "https://dagger.io";
    license = lib.licenses.asl20;
    sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "dagger";
  };
}
