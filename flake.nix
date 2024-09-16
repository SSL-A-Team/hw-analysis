{
  description = "The firmware repository for the SSL A-Team.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachSystem [
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
        "x86_64-linux" ]
    (system: 
      let 

        pkgs = import nixpkgs {
          inherit system; 
        };

        python = "python312";

        packageName = "ateam-hw-analysis";

      in {
        devShells.default = pkgs.mkShell {

          LD_LIBRARY_PATH = "${pkgs.zlib.outPath}/lib";

          shellHook = "";

          buildInputs = with pkgs; [
            # Python
            (pkgs.${python}.withPackages
              (ps: with ps; [ numpy matplotlib scipy jupyter ]))

            # Stuff PyPi packages need
            zlib
          ];
        };
      }
    );
}
