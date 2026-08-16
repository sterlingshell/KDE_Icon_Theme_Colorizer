{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "kde-icon-theme-colorizer-dev";

  buildInputs = with pkgs; [
    (python3.withPackages (ps: with ps; [ ps.tomli ]))
  ];

  shellHook = ''
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src
    echo ">>> KDE Icon Theme Colorizer 开发环境已就绪 <<<"
    echo "可以直接运行: python3 src/main.py --help"
  '';
}
