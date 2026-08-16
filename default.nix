{ lib, stdenv, python3, makeWrapper }:

stdenv.mkDerivation rec {
  pname = "kde-icon-theme-colorizer";
  version = "0.1.0";

  src = ./.;

  nativeBuildInputs = [ makeWrapper ];
  buildInputs = [ (python3.withPackages (ps: with ps; [ ps.tomli ])) ];

  installPhase = ''
    runHook preInstall
    mkdir -p $out/bin $out/lib/kde-icon-theme-colorizer
    cp -r src/* $out/lib/kde-icon-theme-colorizer/
    cp config.toml $out/lib/kde-icon-theme-colorizer/

    makeWrapper $out/lib/kde-icon-theme-colorizer/main.py $out/bin/kde-icon-colorizer \
      --prefix PYTHONPATH : "$out/lib/kde-icon-theme-colorizer" \
      --set KDE_COLORIZER_CONFIG "$out/lib/kde-icon-theme-colorizer/config.toml"

    chmod +x $out/lib/kde-icon-theme-colorizer/main.py
    runHook postInstall
  '';

  meta = with lib; {
    description = "KDE Icon Theme Colorizer - A tool to inject system color support into icon themes";
    license = licenses.mit;
    platforms = platforms.linux;
  };
}
