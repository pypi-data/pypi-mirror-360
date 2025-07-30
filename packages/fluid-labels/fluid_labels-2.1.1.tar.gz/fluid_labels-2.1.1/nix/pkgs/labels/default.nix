{ lib', pkgs }:
pkgs.writeShellApplication {
  bashOptions = [ "errexit" "nounset" "pipefail" ];
  name = "labels";
  runtimeInputs = pkgs.lib.flatten [
    lib'.envs.labels.dependencies.default
    lib'.envs.labels.envars
  ];
  text = ''
    # shellcheck disable=SC1091
    source labels-envars

    fluid-labels "$@"
  '';
}
