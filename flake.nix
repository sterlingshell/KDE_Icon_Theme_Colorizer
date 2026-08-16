{
  description = "KDE Icon Theme Colorizer - Inject system colors into icon themes";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      nixpkgsFor = forAllSystems (system: import nixpkgs { inherit system; });
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgsFor.${system};
          finalPkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in {
          default = pkgs.callPackage ./default.nix { };
          test-colorized = finalPkgs.papirus-icon-theme-colorized { themeVariant = "Papirus-Dark"; };
        });

      overlays.default = final: prev: {
        kde-icon-theme-colorizer = final.callPackage ./default.nix { };

        # 一个辅助函数，用于生成处理过的图标包
        # 用法示例:
        # environment.systemPackages = [
        #   (pkgs.papirus-icon-theme-colorized { themeVariant = "Papirus-Dark"; })
        # ];
        papirus-icon-theme-colorized = { themeVariant ? "Papirus" }:
          final.stdenv.mkDerivation {
            pname = "${final.lib.toLower themeVariant}-colorized";
            version = prev.papirus-icon-theme.version;

            src = prev.papirus-icon-theme;

            nativeBuildInputs = [ self.packages.${final.system}.default ];

            installPhase = ''
              runHook preInstall
              mkdir -p $out/share

              # 正确复制 share/icons 目录到 $out/share/ 下
              cp -r share/icons $out/share/

              # 确保文件可写以进行处理
              chmod -R u+w $out/share/icons

              if [ -d "$out/share/icons/${themeVariant}" ]; then
                # 重命名目标变体（例如 Papirus-Dark -> Papirus-Dark-Colorized）
                mv $out/share/icons/${themeVariant} $out/share/icons/${themeVariant}-Colorized

                # 运行着色工具处理重命名后的目录
                # 注意：此时目录下的软链接应该依然指向 $out/share/icons/Papirus/ 下的文件
                kde-icon-colorizer --yes $out/share/icons/${themeVariant}-Colorized

                # 修改 index.theme
                if [ -f "$out/share/icons/${themeVariant}-Colorized/index.theme" ]; then
                  sed -i "s/Name=${themeVariant}/Name=${themeVariant}-Colorized/g" $out/share/icons/${themeVariant}-Colorized/index.theme
                fi
              else
                echo "Error: Theme variant ${themeVariant} not found in $out/share/icons/"
                ls $out/share/icons/
                exit 1
              fi

              runHook postInstall
            '';
          };
      };

      devShells = forAllSystems (system: {
        default = nixpkgsFor.${system}.mkShell {
          buildInputs = with nixpkgsFor.${system}; [
            (python3.withPackages (ps: with ps; [ ps.tomli ]))
          ];
        };
      });
    };
}
